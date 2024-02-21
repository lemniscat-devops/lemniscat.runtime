from logging import Logger
from typing import List, Optional

from .engine_manifest import StepsParser
from .engine_variables import BagOfVariables
from lemniscat.runtime.plugin.pluginmanager import PluginManager
from lemniscat.core.util.helpers import LogUtil, FileSystem
from lemniscat.core.model import TaskResult
from lemniscat.runtime.model.models import Capabilities, Solution, Task
from dacite import ForwardReferenceError, MissingValueError, UnexpectedDataError, WrongTypeError, from_dict
import ast
import re

_REGEX_CAPTURE_VARIABLE = r"(?:\${{(?P<var>[^}]+)}})"

class OrchestratorEngine:
    """The orchestrator engine is the main entry point for the application"""
    _logger: Logger
    _bagOfVariables: BagOfVariables
    _capabilities: Capabilities
    _steps: StepsParser
    plugins: PluginManager
    


    def __init__(self, **args) -> None:
        self._logger = LogUtil.create(args['options']['log_level'])
        self.plugins = PluginManager(args['options'])
        self._bagOfVariables = BagOfVariables(self._logger, args['options'])
        self._steps = StepsParser(self._logger, ast.literal_eval(args['options']['steps']))
        self._capabilities = self.__read_manifest(args['options']['manifest'])

    def __read_manifest(self, manifest_path) -> Optional[Capabilities]:
        try:
            manifest_data = FileSystem.load_configuration_path(manifest_path)
            capabilities = Capabilities(**manifest_data["capabilities"])
            return capabilities
        except FileNotFoundError as e:
            self._logger.error('Unable to read configuration file', e)
        except (NameError, ForwardReferenceError, UnexpectedDataError, WrongTypeError, MissingValueError) as e:
            self._logger.error('Unable to parse plugin configuration to data class', e)
        return None
    
    def __interpretTaskCondition(self, capability: str, condition: str) -> bool:
        if(condition is None):
            return True
        if(isinstance(condition, str)):
            variables = self._bagOfVariables.get_all_for_capability(capability)
            matches = re.findall(_REGEX_CAPTURE_VARIABLE, condition)
            if(len(matches) > 0):
                for match in matches:
                    var = str.strip(match)
                    if(var in variables):
                        condition = condition.replace(f'${{{{{match}}}}}', variables[var].value)
                        self._logger.debug(f"Interpreting variable: {var} -> {variables[var]}")
                    else:
                        condition = condition.replace(f'${{{{{match}}}}}', "")
                        self._logger.debug(f"Variable not found: {var}. Replaced by empty string.")
        return eval(condition)
    
    def __runTasks(self, step: str, capability: str, solution: Solution) -> None:
        if(solution.status == 'Failed'):
            return
        for task in solution.tasks_byStep(step):
            if(self._steps.get(step, capability)):
                if(task.condition is None or self.__interpretTaskCondition(capability, task.condition) == True):
                    self._logger.info(f'     |->🚀 [{step}] Running task: {task.displayName}')
                    self._logger.debug(f'    |->🚀 [{step}] Running task: {task.id}')
                    taskResult = self.__invoke_on_plugin(task.name, task.parameters, self._bagOfVariables.get_all_for_capability(capability))
                    if(taskResult.status == 'Failed'):
                        task.status = 'Failed'
                        solution.status = 'Failed'
                        break
                    else:
                        self._bagOfVariables.interpret();    
                        task.status = 'Finished'
                else:
                    self._logger.info(f'    |->🚀 [{step}] Skipping task: {task.name}')
                    self._logger.debug(f'    |->🚀 [{step}] Running task: {task.id}')
                     
    def __runSolution(self, capability: str, solution: Solution) -> None:
        solution.status = 'Running'
        self.__runTasks('pre', capability, solution)
        self.__runTasks('run', capability, solution)
        self.__runTasks('decom', capability, solution)
        self.__runTasks('post', capability, solution)  
     
    def __runCapability(self, current: str, capability: Optional[List[Solution]]) -> None:
        self._logger.info(f'🦾 Running capability: {current}')
        if(not capability is None): 
            isEnable = self._bagOfVariables.get(f"{current}.enable")
            if(isEnable.value == True):
                for solution in capability:
                    if(self._bagOfVariables.get(f"{current}.solution").value == solution.name):
                        self._logger.info(f' |->💡 Running solution: {solution.name}')
                        self.__runSolution(current, solution)
                    else:
                        self._logger.debug(f'    Skipping solution: {solution.name}')
        else:
            self._logger.debug(f'Skipping capability: {current}')

    def start(self) -> None:
        self.__reload_plugins()
        
        self.__runCapability("code", self._capabilities.code)
        self.__runCapability("build", self._capabilities.build)
        self.__runCapability("test", self._capabilities.test)
        self.__runCapability("deploy", self._capabilities.deploy)
        self.__runCapability("release", self._capabilities.release)
        self.__runCapability("operate", self._capabilities.operate)
        self.__runCapability("monitor", self._capabilities.monitor)
        self.__runCapability("plan", self._capabilities.plan)

    def __reload_plugins(self) -> None:
        """Reset the list of all plugins and initiate the walk over the main
        provided plugin package to load all available plugins
        """
        self.plugins.discover_plugins(True)

    def __invoke_on_plugin(self, moduleName: str, parameters: dict = None, variables: dict = None) -> TaskResult:
        plugin = self.plugins.register_plugin_by_alias(moduleName)
        if(plugin is None):
            self._logger.error(f'       Failed to load plugin: {moduleName} - Skip task')
            return
        delegate = self.plugins.hook_invoke(plugin)
        task = delegate(parameters=parameters, variables=variables)
        if(task.status == 'Failed'):
            self._logger.error(f'       Failed task: {task.name} with errors: {task.errors}')
        else:
            variables = self.plugins.getVariables(plugin)
            if(not variables is None):
                self._logger.debug(f"Received {len(variables)} variables")
                self._bagOfVariables.append(variables)
                self._logger.debug(f"Now, there are {len(self._bagOfVariables._variables)} variables in the bag")
            self._logger.log(70, f'     Finished task: {task.name}')
        return task
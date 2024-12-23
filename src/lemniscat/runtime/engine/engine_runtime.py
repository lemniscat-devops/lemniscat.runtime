from logging import Logger
from typing import List, Optional
from .engine_manifest import StepsParser
from .engine_variables import BagOfVariables
from lemniscat.runtime.plugin.pluginmanager import PluginManager
from lemniscat.core.util.helpers import LogUtil, FileSystem
from lemniscat.core.model import TaskResult
from lemniscat.runtime.model.models import Capabilities, Solution, Phase
from dacite import ForwardReferenceError, MissingValueError, UnexpectedDataError, WrongTypeError
import ast

class OrchestratorEngine:
    """The orchestrator engine is the main entry point for the application"""
    _logger: Logger
    _bagOfVariables: BagOfVariables
    _capabilities: Capabilities
    _preTasks: Phase
    _postTasks: Phase
    _steps: StepsParser
    plugins: PluginManager
    _outputContextPath: str = None

    def __init__(self, **args) -> None:
        self._logger = LogUtil.create(args['options']['verbosity'])
        self.plugins = PluginManager(args['options'])
        self._bagOfVariables = BagOfVariables(self._logger, args['options'])
        self._steps = StepsParser(self._logger, ast.literal_eval(args['options']['steps']))
        self.__read_manifest(args['options']['manifest'])
        self._outputContextPath = args['options']['outputContext']

    def __read_manifest(self, manifest_path) -> None:
        try:
            manifest_data = FileSystem.load_configuration_path(manifest_path)
            capabilitiesData = manifest_data["capabilities"]
            capabilitiesData = self._bagOfVariables.interpretManifest(capabilitiesData, excludeInterpret=['condition'])
            self._capabilities = Capabilities(self._bagOfVariables._variables, **capabilitiesData)
            if(manifest_data.get("pre")):
                preTasks = manifest_data["pre"]
                preTasks = self._bagOfVariables.interpretManifest(preTasks, excludeInterpret=['condition'])
                self._preTasks = Phase(self._bagOfVariables._variables, **preTasks)
            else:
                self._preTasks = None
            if(manifest_data.get("post")):
                postTasks = manifest_data["post"]
                postTasks = self._bagOfVariables.interpretManifest(postTasks, excludeInterpret=['condition'])
                self._postTasks = Phase(self._bagOfVariables._variables, **postTasks)
            else:
                self._postTasks = None
        except FileNotFoundError as e:
            self._logger.error('Unable to read configuration file', e)
        except (NameError, ForwardReferenceError, UnexpectedDataError, WrongTypeError, MissingValueError) as e:
            self._logger.error('Unable to parse plugin configuration to data class', e)
        return None
    
    def __evalTaskCondition(self, capability: str, condition: str) -> bool:
        if(condition is None):
            return True
        if(isinstance(condition, str)):
            return self._bagOfVariables.interpretEvalCondition(condition)
    
    def __runTasks(self, step: str, capability: str, solution: Solution) -> None:
        if(solution.status == 'Failed'):
            return
        for task in solution.tasks_byStep(step):
            if(self._steps.get(step, capability)):
                if(task.condition is None or self.__evalTaskCondition(capability, task.condition) == True):
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
                    self._logger.info(f'    |->🚀 [{step}] Skipping task: {task.displayName}')
                    self._logger.debug(f'    |->🚀 [{step}] Running task: {task.id}')
                     
    def __runSolution(self, capability: str, solution: Solution) -> None:
        solution.status = 'Running'
        self.__runTasks('pre', capability, solution)
        self.__runTasks('pre-clean', capability, solution)
        self.__runTasks('run', capability, solution)
        self.__runTasks('run-clean', capability, solution)
        self.__runTasks('post', capability, solution)
        self.__runTasks('post-clean', capability, solution)
        
    def __runPhase(self, capability: str, phase: Phase) -> str:
        if(phase is None):
            return 'Finished'
        phase.status = 'Running'
        self.__runTasks('pre', capability, phase)
        self.__runTasks('pre-clean', capability, phase)
        self.__runTasks('run', capability, phase)
        self.__runTasks('run-clean', capability, phase)
        self.__runTasks('post', capability, phase)
        self.__runTasks('post-clean', capability, phase)
        return phase.status
     
    def __runpre(self) -> str:
        status = 'Finished'
        if(self._preTasks is None):
            return status
        self._logger.info(f'🦾 Running pre tasks')
        status = self.__runPhase("global", self._preTasks)  
        if(status == 'Failed'):
            self._logger.error(f'Pre tasks failed')
        return status 
    
    def __runpost(self) -> str:
        status = 'Finished'
        if(self._postTasks is None):
            return status
        self._logger.info(f'🦾 Running post tasks')
        status = self.__runPhase("global", self._postTasks)  
        if(status == 'Failed'):
            self._logger.error(f'Post tasks failed')
        return status 
     
    def __runCapabilities(self) -> str:
        status = 'Finished' 
        for capability in self._capabilities.order:
            status = self.__runCapability(capability, self._capabilities.capability[capability])  
            if(status == 'Failed'):
                self._logger.error(f'Capability: {capability} failed')
                break 
        return status
     
    def __runCapability(self, current: str, capability: Optional[List[Solution]]) -> str:
        status = 'Finished'
        self._logger.info(f'🦾 Running capability: {current}')
        if(not capability is None): 
            isEnable = self._bagOfVariables.get(f"{current}_enable") or self._bagOfVariables.get(f"{current}.enable")
            if(isEnable.value == True):
                for solution in capability:
                    if(self._bagOfVariables.get(f"{current}_solution").value == solution.name or self._bagOfVariables.get(f"{current}.solution").value == solution.name):
                        self._logger.info(f' |->💡 Running solution: {solution.name}')
                        self.__runSolution(current, solution)
                    else:
                        self._logger.debug(f'    Skipping solution: {solution.name}')
                    if(solution.status == 'Failed'):
                        status = 'Failed'
                        break
        else:
            self._logger.debug(f'Skipping capability: {current}')
        return status

    def start(self) -> str:
        self.__reload_plugins()
        status = self.__runpre()
        if(status == 'Failed'):
            return status
        status = self.__runCapabilities()
        if(status == 'Failed'):
            return status
        status = self.__runpost()
  
        if(self._outputContextPath is not None):
            self._logger.info(f"Saving output context...")
            self._bagOfVariables.save(self._outputContextPath)
            self._logger.info(f"Output context saved to: {self._outputContextPath}")
        return status

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
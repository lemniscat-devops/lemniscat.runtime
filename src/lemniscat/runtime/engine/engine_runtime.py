from logging import Logger
from typing import List, Optional

from .engine_manifest import StepsParser
from .engine_variables import BagOfVariables
from lemniscat.runtime.plugin.pluginmanager import PluginManager
from lemniscat.core.util.helpers import LogUtil, FileSystem
from lemniscat.runtime.model.models import Capabilities, Solution
from dacite import ForwardReferenceError, MissingValueError, UnexpectedDataError, WrongTypeError, from_dict
import ast

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
    
    def __runSolution(self, capability: str, solution: Solution) -> None:
        for task in solution.pre_tasks():
            if(self._steps.get_pre(capability)):
                self._logger.info(f'     |->🚀 [PRE] Running task: {task.name}')
                self.__invoke_on_plugin(task.name, task.parameters, self._bagOfVariables.get_all_for_capability(capability))
        for task in solution.run_tasks():
            if(self._steps.get_run(capability)):
                self._logger.info(f'     |->🚀 [RUN] Running task: {task.name}')
                self.__invoke_on_plugin(task.name, task.parameters, self._bagOfVariables.get_all_for_capability(capability))
        for task in solution.decom_tasks():
            if(self._steps.get_decom(capability)):
                self._logger.info(f'     |->🚀 [DECOM] Running task: {task.name}')
                self.__invoke_on_plugin(task.name, task.parameters, self._bagOfVariables.get_all_for_capability(capability))        
        for task in solution.post_tasks():
            if(self._steps.get_post(capability)):
                self._logger.info(f'     |->🚀 [POST] Running task: {task.name}')
                self.__invoke_on_plugin(task.name, task.parameters, self._bagOfVariables.get_all_for_capability(capability))     
     
    def __runCapability(self, current: str, capability: Optional[List[Solution]]) -> None:
        self._logger.info(f'🦾 Running capability: {current}')
        if(not capability is None): 
            if(self._bagOfVariables.get(f"{current}.enable") == True):
                for solution in capability:
                    if(self._bagOfVariables.get(f"{current}.solution") == solution.name):
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

    def __invoke_on_plugin(self, moduleName: str, parameters: dict = None, variables: dict = None):
        plugin = self.plugins.register_plugin_by_alias(moduleName)
        if(plugin is None):
            self._logger.error(f'       Failed to load plugin: {moduleName} - Skip task')
            return
        delegate = self.plugins.hook_plugin(plugin)
        task = delegate(parameters=parameters, variables=variables)
        if(task.status == 'Failed'):
            self._logger.error(f'       Failed task: {task.name} with errors: {task.errors}')
        else:
            self._logger.log(70, f'     Finished task: {task.name}')
import os
import importlib
from logging import Logger
from typing import List, Any, Dict

from dacite import ForwardReferenceError, MissingValueError, UnexpectedDataError, WrongTypeError, from_dict

from lemniscat.core.contract import IPluginRegistry, PluginCore
from lemniscat.runtime.model.models import DependencyModule
from lemniscat.core.util.helpers import FileSystem, LogUtil
from .utilities import PluginUtility


class PluginManager:
    _logger: Logger
    modules: dict
    _plugins: List[DependencyModule]

    def __init__(self, options: Dict) -> None:
        self._logger = LogUtil.create(options['verbosity'])
        self._plugins = self.__read_pluginDependencies(options['manifest'])
        self.plugin_util = PluginUtility(self._logger)
        self.modules = {}

    
    def __read_pluginDependencies(self, manifest_path) -> List[str]:
        dependencies = []
        try:
            manifest_data = FileSystem.load_configuration_path(manifest_path)
            for requirement in manifest_data['requirements']:
                dependency = from_dict(data_class=DependencyModule, data=requirement)
                dependencies.append(dependency)
        except FileNotFoundError as e:
            self._logger.error('Unable to read configuration file', e)
        except (NameError, ForwardReferenceError, UnexpectedDataError, WrongTypeError, MissingValueError) as e:
            self._logger.error('Unable to parse plugin configuration to data class', e)
        return dependencies

    def __search_for_plugins_in(self, plugins: List[DependencyModule]):
        for plugin in plugins:
            entry_point = self.plugin_util.setup_plugin_configuration(plugin)
            if entry_point is not None:
                self.modules[entry_point.alias] = IPluginRegistry.plugin_registries[-1]
                self._logger.debug(f'Plugin {plugin.name} gracefully loaded')
            else:
                self._logger.debug(f'No valid plugin found in {plugin.name}')

    def discover_plugins(self, reload: bool):
        """
        Discover the plugin classes contained in Python files, given a
        list of directory names to scan.
        """
        if reload:
            self.modules.clear()
            IPluginRegistry.plugin_registries.clear()
            self._logger.debug(f'Searching for plugins...')
            self.__search_for_plugins_in(self._plugins)
    
    def register_plugin_by_alias(self, alias: str) -> PluginCore:
        """
        Return a plugin instance by name.
        """
        if alias in self.modules.keys():
            return self.register_plugin(self.modules[alias], self._logger) 
        else:
            self._logger.error(f'       No plugin found for alias: {alias}')       
            
    @staticmethod
    def register_plugin(module: type, logger: Logger) -> PluginCore:
        """
        Create a plugin instance from the given module
        :param module: module to initialize
        :param logger: logger for the module to use
        :return: a high level plugin
        """
        return module(logger)

    @staticmethod
    def hook_invoke(plugin: PluginCore):
        """
        Return a function accepting commands.
        """
        return plugin.invoke
    
    @staticmethod
    def getVariables(plugin: PluginCore) -> dict:
        """
        Return a function accepting commands.
        """
        return plugin.getVariables()
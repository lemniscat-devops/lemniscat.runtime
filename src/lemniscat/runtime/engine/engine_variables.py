from logging import Logger
import json
import ast
import logging
import re

class BagOfVariables:
    """A bag of variables that can be used to store and retrieve variables"""
    _logger: Logger
    _variables: dict = {}

    def __init__(self, logger, *args) -> None:
        self._logger = logger
        self._logger.info("Loading variables")
        conf = args[0]['config_files']
        configFiles = ast.literal_eval(conf)
        for file in configFiles:
            self._logger.debug(f"Loading variables from file: {file}...")
            with open(file, 'r') as f:
                variables = json.load(f)
            for key in variables:
                self._variables[key] = variables[key]
            self._logger.debug(f"{len(variables)} loaded.")    
        
        self._logger.debug(f"Override variables from parameters...")
        override = json.loads(args[0]['override_variables'])        
        if(override != None):
            for key in override:
                self._variables[key] = args[0]['override_variables'][key]
            self._logger.debug(f"{len(override)} loaded.")
        self._logger.info("Variables loaded")

    def get(self, key: str) -> str:
        if(not key in self._variables):
            self._logger.error(f"Variable '{key}' not found")
            return None
        return self._variables[key]
    
    def get_all_for_capability(self, capability: str) -> dict:
        result = {}
        for key in self._variables.keys():
            m = re.match(r"^(?P<capability>\w+)\.(?P<variable>.*)", str(key))
            if(not m is None):
                if(m.group('capability') == capability):
                    result[m.group('variable')] = self._variables[key]
        result.update(self._variables)
        
        if(self._logger.level == logging.DEBUG):
            self._logger.debug(f"-----------------------------------------------")
            self._logger.debug(f"Variables for task in capability '{capability}':")
            for key in result.keys():
                self._logger.debug(f"{key}: {result[key]}")
            self._logger.debug(f"-----------------------------------------------")
        return result

    def set(self, key: str, value: str) -> None:
        self._variables[key] = value
        
    def append(self, variables: dict) -> None:
        self._variables.update(variables)

    def __str__(self) -> str:
        return f'{self._variables}'
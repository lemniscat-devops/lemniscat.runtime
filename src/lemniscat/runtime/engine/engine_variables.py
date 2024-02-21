from logging import Logger
import json
import ast
import logging
import re
from dacite import ForwardReferenceError, MissingValueError, UnexpectedDataError, WrongTypeError, from_dict
from lemniscat.core.util.helpers import FileSystem
from lemniscat.runtime.model.models import VariableValue, Variable

_REGEX_CAPTURE_VARIABLE = r"(?:\${{(?P<var>[^}]+)}})"

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
                self._variables[key] = VariableValue(variables[key])
            self._logger.debug(f"{len(variables)} loaded.")    
        
        self._logger.debug(f"Loading variables from manifest...")
        self.__append_manifestVariables(args[0]['manifest'])
        self._logger.debug(f"{len(variables)} loaded.")
        
        self._logger.debug(f"Override variables from parameters...")
        override = json.loads(args[0]['override_variables'])        
        if(override != None):
            for key in override:
                self._variables[key] = VariableValue(override[key])
            self._logger.debug(f"{len(override)} loaded.")
        self.interpret(); 
        self._logger.info("Variables loaded")
        
    def __append_manifestVariables(self, manifest_path) -> None:
        try:
            manifest_data = FileSystem.load_configuration_path(manifest_path)
            for var in manifest_data['variables']:
                variable = from_dict(data_class=Variable, data=var).to_dict()
                self._variables.update(variable)
        except FileNotFoundError as e:
            self._logger.error('Unable to read configuration file', e)
        except (NameError, ForwardReferenceError, UnexpectedDataError, WrongTypeError, MissingValueError) as e:
            self._logger.error('Unable to parse plugin configuration to data class', e)

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

    def set(self, key: str, value: str, sensitive: bool = False) -> None:
        self._variables[key] = VariableValue(value, sensitive)
        
    def append(self, variables: dict) -> None:
        self._variables.update(variables)

    def __interpretDict(self, variable: dict) -> VariableValue:
        isSensitive = False
        for key in variable:
            if(isinstance(variable[key], str)):
                tmp = self.__intepretString(variable[key])
            elif(isinstance(variable[key], dict)):
                tmp = self.__interpretDict(variable[key])
            elif(isinstance(variable[key], list)):
                tmp = self.__interpretList(variable[key])
            else:
                tmp = variable[key]
            if(tmp.sensitive):
                isSensitive = True
            variable[key] = tmp.value
        return VariableValue(variable, isSensitive)
    
    def __interpretList(self, variable: list) -> VariableValue:
        isSensitive = False
        for val in variable:
            if(isinstance(val, str)):
                tmp = self.__intepretString(val)
            elif(isinstance(val, dict)):
                tmp = self.__interpretDict(val)
            elif(isinstance(val, list)):
                tmp = self.__interpretList(val)
            else:
                tmp = val
            if(tmp.sensitive):
                isSensitive = True
            val = tmp.value
        return VariableValue(variable, isSensitive)    
    
    def __intepretString(self, value: str) -> VariableValue:
        isSensitive = False
        matches = re.findall(_REGEX_CAPTURE_VARIABLE, value)
        if(len(matches) > 0):
            for match in matches:
                var = str.strip(match)
                if(var in self._variables):
                    if(self._variables[var].sensitive):
                        isSensitive = True
                    value = value.replace(f'${{{{{match}}}}}', self._variables[var].value)
                    self._logger.debug(f"Interpreting variable: {var} -> {self._variables[var]}")
        return VariableValue(value, isSensitive)        
                        
    def __interpret(self, variable: VariableValue) -> VariableValue:
        isSensitive = variable.sensitive
        if(variable is None):
            return None
        if(isinstance(variable.value, str)):
            tmp = self.__intepretString(variable.value)
        elif(isinstance(variable.value, dict)):
            tmp = self.__interpretDict(variable.value)
        elif(isinstance(variable.value, list)):
            tmp = self.__interpretList(variable.value)
        else:
            tmp = variable
        if(tmp.sensitive):
            isSensitive = True
        variable.value = tmp.value
        return VariableValue(variable.value, isSensitive)    
        
    def interpret(self) -> None:
        for key in self._variables:
            self._variables[key] = self.__interpret(self._variables[key])

    def __str__(self) -> str:
        return f'{self._variables}'
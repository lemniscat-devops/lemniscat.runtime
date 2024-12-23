from logging import Logger
import json
import ast
import logging
import re
from dacite import ForwardReferenceError, MissingValueError, UnexpectedDataError, WrongTypeError, from_dict
from lemniscat.core.util.helpers import FileSystem, Interpreter
from lemniscat.core.model.models import VariableValue
from lemniscat.runtime.model.models import Variable

class BagOfVariables:
    """A bag of variables that can be used to store and retrieve variables"""
    _logger: Logger
    _interpeter: Interpreter
    _variables: dict = {}

    def __loadVariables__(self, key: str, variable) -> None:
        if isinstance(variable, dict):
            if '~object' in variable.keys() and variable['~object'] == True:
                variable.pop('~object')
                self._variables[key] = VariableValue(variable)
            else:
                for subKey in variable:
                    self.__loadVariables__(f'{key}_{subKey}', variable[subKey])
        else:    
            self._variables[key] = VariableValue(variable)

    def __init__(self, logger, *args) -> None:
        self._logger = logger
        self._variables = {}

        try:
            self._logger.info("Loading variables")
            conf = args[0]['configFiles']
            try:
                configFiles = ast.literal_eval(conf)
            except (ValueError, SyntaxError) as e:
                self._logger.error(f"Error parsing config files: {e}")
                configFiles = []

            for file in configFiles:
                self._logger.debug(f"Loading variables from file: {file}...")
                try:
                    if file.endswith('.json'):
                        with open(file, 'r') as f:
                            variables = json.load(f)
                        for key in variables:
                            self.__loadVariables__(key, variables[key])
                        self._logger.debug(f"{len(variables)} loaded.")
                    if file.endswith('.yaml') or file.endswith('.yml'):
                        variables = FileSystem.load_configuration_path(file)
                        for key in variables:
                            self.__loadVariables__(key, variables[key])
                        self._logger.debug(f"{len(variables)} loaded.")
                except Exception as e:
                    try:
                        with open(file, 'r') as f:
                            file_content = f.read()
                        self._logger.error(f"Error loading file {file}: {e}\nFile content:\n{file_content}")
                    except Exception as read_error:
                        self._logger.error(f"Error reading file {file} for content display: {read_error}")

            self._logger.debug(f"Loading variables from manifest...")
            try:
                self.__append_manifestVariables(args[0]['manifest'])
                self._logger.debug(f"{len(variables)} loaded.")
            except Exception as e:
                self._logger.error(f"Error loading manifest variables: {e}")

            self._logger.debug(f"Override variables from parameters...")
            try:
                override = json.loads(args[0]['extraVariables'])        
                if override is not None:
                    for key in override:
                        self._variables[key] = VariableValue(override[key])
                    self._logger.debug(f"{len(override)} loaded.")
            except json.JSONDecodeError as e:
                self._logger.error(f"Error parsing extra variables: {e}")

            self._interpeter = Interpreter(logger, self._variables)
            self._interpeter.interpret()
            self._logger.info("Variables loaded")

        except Exception as e:
            self._logger.error(f"Unexpected error in initialization: {e}")
        
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
    
    def get_all_without_sensitive(self) -> dict:
        result = {}
        for key in self._variables:
            if(not self._variables[key].sensitive):
                result[key] = self._variables[key].value
        return result  
    
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
        
    def save(self, filePath: str) -> None:
        output = {}
        for key in self._variables:
            if(self._variables[key].sensitive == False):
                output[key] = self._variables[key].value
        
        with open(filePath, 'w') as f:
            json.dump(output, f)  
        
    def interpret(self, excludeInterpret: list = []) -> None:
        self._interpeter.interpret(excludeInterpret)
        
    def interpretManifest(self, manifest: dict, excludeInterpret: list = []) -> dict:
        return self._interpeter.interpretDict(manifest, "manifest", excludeInterpret)        

    def interpretEvalCondition(self, condition) -> bool:
        return self._interpeter.interpretEvalCondition(condition)

    def __str__(self) -> str:
        return f'{self._variables}'
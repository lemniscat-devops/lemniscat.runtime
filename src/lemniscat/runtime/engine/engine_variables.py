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

    def __init__(self, logger, *args) -> None:
        
        self._logger = logger
        self._logger.info("Loading variables")
        conf = args[0]['configFiles']
        configFiles = ast.literal_eval(conf)
        for file in configFiles:
            self._logger.debug(f"Loading variables from file: {file}...")
            if(file.endswith('.json')):
                with open(file, 'r') as f:
                    variables = json.load(f)
                for key in variables:
                    self._variables[key] = VariableValue(variables[key])
                self._logger.debug(f"{len(variables)} loaded.")
            if(file.endswith('.yaml') or file.endswith('.yml')):
                variables = FileSystem.load_configuration_path(file)
                for key in variables:
                    self._variables[key] = VariableValue(variables[key])
                self._logger.debug(f"{len(variables)} loaded.")
        
        self._logger.debug(f"Loading variables from manifest...")
        self.__append_manifestVariables(args[0]['manifest'])
        self._logger.debug(f"{len(variables)} loaded.")
        
        self._logger.debug(f"Override variables from parameters...")
        override = json.loads(args[0]['extraVariables'])        
        if(override != None):
            for key in override:
                self._variables[key] = VariableValue(override[key])
            self._logger.debug(f"{len(override)} loaded.")
        self._interpeter = Interpreter(logger, self._variables)
        self._interpeter.interpret(); 
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
        
    def interpret(self) -> None:
        self._interpeter.interpret()
        
    def interpretManifest(self, manifest: dict) -> dict:
        return self._interpeter.interpretDict(manifest, "manifest")        

    def interpretCondition(self, condition: str) -> str:
        return self._interpeter.interpretString(condition, "condition")

    def __str__(self) -> str:
        return f'{self._variables}'
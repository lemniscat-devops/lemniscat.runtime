import ast
from dataclasses import dataclass
import re
from typing import List, Optional
from lemniscat.core.model.models import VariableValue
from lemniscat.core.util.helpers import LogUtil, FileSystem, Interpreter
import uuid

@dataclass
class PluginRunTimeOption(object):
    main: str
    tests: Optional[List[str]]

@dataclass
class Variable:
    name: str
    value: object
    sensitive: bool = False

    def to_dict(self) -> dict:
        return { self.name: VariableValue(self.value, self.sensitive) }

@dataclass
class DependencyModule:
    name: str
    version: str

    def __str__(self) -> str:
        return f'{self.name}=={self.version}'

@dataclass
class Parameters:
    name: str
    description: Optional[str]
    type: str
    default: Optional[str]
    required: bool = False

@dataclass
class PluginConfig:
    name: str
    alias: str
    creator: str
    runtime: PluginRunTimeOption
    repository: str
    description: str
    version: str
    parameters: Optional[List[Parameters]]
    requirements: Optional[List[DependencyModule]]


@dataclass
class Task:
    id: str
    status: str
    name: str
    condition: str
    displayName: str
    steps: List[str]
    parameters: dict
    
    def __init__(self, **kwargs) -> None:
        self.name = kwargs['task']
        self.displayName = kwargs['displayName']
        if(self.displayName is None):
            self.displayName = self.name
        if(kwargs.__contains__('prefix')):
            val = kwargs['prefix']
            self.displayName = f'{val}{self.displayName}'
        self.steps = kwargs['steps']
        self.parameters = kwargs['parameters']
        if(kwargs.__contains__('condition')):
            self.condition = kwargs['condition']
        else:
            self.condition = None
        self.id = str(uuid.uuid4())
        self.status = 'Pending'

@dataclass
class Template:
    path: str
    displayName: str = None
    _variables: dict = None
    
    def __init__(self, variables: dict, **kwargs) -> None:
        self.path = kwargs['template']
        self._variables = variables
        if(kwargs.__contains__('displayName')):
            val = kwargs['displayName']
            self.displayName = f'[{val}] '
        if(kwargs.__contains__('prefix')):
            val = kwargs['prefix']
            self.displayName = f'{val}{self.displayName}'
    
    def getTasks(self) -> List[Task]:
        tasks = FileSystem.load_configuration_path(self.path)
        Interpreter(LogUtil.root, self._variables).interpretDict(tasks)
        result = []
        for task in tasks['tasks']:
            task['prefix'] = self.displayName
            if(dict(task).keys().__contains__('template')):

                result.extend(Template(self._variables, **task).getTasks())
            else:
                result.append(Task(**task))              
        return result

@dataclass
class Solution:
    id: str
    status: str
    name: str
    description: str
    tasks: Optional[List[Task]]
    
    def tasks_byStep(self, step: str) -> List[Task]:
        return [task for task in self.tasks if step in task.steps and task.status == 'Pending']
    
    def pre_tasks(self) -> List[Task]:
        return [task for task in self.tasks if 'pre' in task.steps and task.status == 'Pending']
    
    def run_tasks(self) -> List[Task]:
        return [task for task in self.tasks if 'run' in task.steps and task.status == 'Pending']
    
    def post_tasks(self) -> List[Task]:
        return [task for task in self.tasks if 'post' in task.steps and task.status == 'Pending']

    def preclean_tasks(self) -> List[Task]:
        return [task for task in self.tasks if 'pre-clean' in task.steps and task.status == 'Pending']

    def runclean_tasks(self) -> List[Task]:
        return [task for task in self.tasks if 'run-clean' in task.steps and task.status == 'Pending']

    def postclean_tasks(self) -> List[Task]:
        return [task for task in self.tasks if 'post-clean' in task.steps and task.status == 'Pending']
    
    def __init__(self, variables: dict, **kwargs) -> None:
        self.name = kwargs['solution']
        self.tasks = []
        for task in kwargs['tasks']:
            if(dict(task).keys().__contains__('template')):
                self.tasks.extend(Template(variables, **task).getTasks())
            else:
                self.tasks.append(Task(**task))    
        self.id = str(uuid.uuid4())
        self.status = 'Pending'

@dataclass
class Capabilities:
    capability: dict
    order: List[str] = None
    
    def __reorder(self, capability: str, dependsOn: List[str]) -> None:
        idx = self.order.index(capability)
        self.order.pop(idx)
        newPosition = 0 
        for item in dependsOn:
            if(newPosition < self.order.index(item)):
                newPosition = self.order.index(item)
        self.order.insert(newPosition + 1, capability)
    
    def __init__(self, variables: dict, **kwargs) -> None:
        self.capability = {}
        self.order = ['code', 'build', 'test', 'deploy', 'release', 'operate', 'monitor', 'plan']
        if kwargs['code'] is not None:
            self.capability['code'] = list(map(lambda x: Solution(variables, **x), kwargs['code']['solutions']))
            if kwargs['code'].__contains__('dependsOn'):
                self.__reorder('code', kwargs['code']['dependsOn'])
        else:
            self.capability['code'] = None
        if kwargs['build'] is not None:    
            self.capability['build'] = list(map(lambda x: Solution(variables, **x), kwargs['build']['solutions']))
            if kwargs['build'].__contains__('dependsOn'):
                self.__reorder('build', kwargs['build']['dependsOn'])
        else:
            self.capability['build'] = None
        if kwargs['test'] is not None:    
            self.capability['test'] = list(map(lambda x: Solution(variables, **x), kwargs['test']['solutions']))
            if kwargs['test'].__contains__('dependsOn'):
                self.__reorder('test', kwargs['test']['dependsOn'])
        else:
            self.capability['test'] = None
        if kwargs['deploy'] is not None:    
            self.capability['deploy'] = list(map(lambda x: Solution(variables, **x), kwargs['deploy']['solutions']))
            if kwargs['deploy'].__contains__('dependsOn'):
                self.__reorder('deploy', kwargs['deploy']['dependsOn'])
        else:
            self.capability['deploy'] = None
        if kwargs['release'] is not None:  
            self.capability['release'] = list(map(lambda x: Solution(variables, **x), kwargs['release']['solutions']))
            if kwargs['release'].__contains__('dependsOn'):
                self.__reorder('release', kwargs['release']['dependsOn'])
        else:
            self.capability['release'] = None
        if kwargs['operate'] is not None:
            self.capability['operate'] = list(map(lambda x: Solution(variables, **x), kwargs['operate']['solutions']))
            if kwargs['operate'].__contains__('dependsOn'):
                self.__reorder('operate', kwargs['operate']['dependsOn'])
        else:
            self.capability['operate'] = None
        if kwargs['monitor'] is not None:
            self.capability['monitor'] = list(map(lambda x: Solution(variables, **x), kwargs['monitor']['solutions']))
            if kwargs['monitor'].__contains__('dependsOn'):
                self.__reorder('monitor', kwargs['monitor']['dependsOn'])
        else:
            self.capability['monitor'] = None
        if kwargs['plan'] is not None:
            self.capability['plan'] = list(map(lambda x: Solution(variables, **x), kwargs['plan']['solutions']))
            if kwargs['plan'].__contains__('dependsOn'):
                self.__reorder('plan', kwargs['plan']['dependsOn'])
        else:
            self.capability['plan'] = None
            

@dataclass
class Manifest:
    capabilities: Capabilities
    requirements: Optional[List[DependencyModule]] = None
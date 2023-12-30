from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PluginRunTimeOption(object):
    main: str
    tests: Optional[List[str]]


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
    name: str
    displayName: str
    steps: List[str]
    parameters: dict
    
    def __init__(self, **kwargs) -> None:
        self.name = kwargs['task']
        self.displayName = kwargs['displayName']
        self.steps = kwargs['steps']
        self.parameters = kwargs['parameters']

@dataclass
class Solution:
    name: str
    description: str
    tasks: Optional[List[Task]]
    
    def pre_tasks(self) -> List[Task]:
        return [task for task in self.tasks if 'pre' in task.steps]
    
    def run_tasks(self) -> List[Task]:
        return [task for task in self.tasks if 'run' in task.steps]

    def decom_tasks(self) -> List[Task]:
        return [task for task in self.tasks if 'decom' in task.steps]
    
    def post_tasks(self) -> List[Task]:
        return [task for task in self.tasks if 'post' in task.steps]
    
    def __init__(self, **kwargs) -> None:
        self.name = kwargs['solution']
        self.tasks = list(map(lambda x: Task(**x), kwargs['tasks']))


@dataclass
class Capabilities:
    code : Optional[List[Solution]] = None
    build: Optional[List[Solution]] = None
    test: Optional[List[Solution]] = None
    deploy: Optional[List[Solution]] = None
    release: Optional[List[Solution]] = None
    operate: Optional[List[Solution]] = None
    monitor: Optional[List[Solution]] = None
    plan: Optional[List[Solution]] = None
    
    def __init__(self, **kwargs) -> None:
        if kwargs['code'] is not None:
            self.code = list(map(lambda x: Solution(**x), kwargs['code']))
        if kwargs['build'] is not None:    
            self.build = list(map(lambda x: Solution(**x), kwargs['build']))
        if kwargs['test'] is not None:    
            self.test = list(map(lambda x: Solution(**x), kwargs['test']))
        if kwargs['deploy'] is not None:    
            self.deploy = list(map(lambda x: Solution(**x), kwargs['deploy']))
        if kwargs['release'] is not None:  
            self.release = list(map(lambda x: Solution(**x), kwargs['release']))
        if kwargs['operate'] is not None:
            self.operate = list(map(lambda x: Solution(**x), kwargs['operate']))
        if kwargs['monitor'] is not None:
            self.monitor = list(map(lambda x: Solution(**x), kwargs['monitor']))
        if kwargs['plan'] is not None:
            self.plan = list(map(lambda x: Solution(**x), kwargs['plan']))

@dataclass
class Manifest:
    capabilities: Capabilities
    requirements: Optional[List[DependencyModule]] = None
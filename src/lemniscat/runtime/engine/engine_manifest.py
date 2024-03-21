from logging import Logger
from typing import List

class StepsParser:
    """The steps parser is responsible for parsing the steps"""
    _steps: List[str] = []
    _logger : Logger

    def __init__(self, logger: Logger, steps: List[str]) -> None:
        capabilities = List[str]
        for step in steps:
            parts = step.split(':')
            
            if(parts[1] == 'all'):
                capabilities = ['code', 'build', 'test', 'deploy', 'release', 'operate', 'monitor', 'plan']
            else:
                capabilities = [parts[1]]
            
            if(parts[0] == 'all'):
                steps = ['pre', 'run', 'post']
            if(parts[0] == 'allclean'):
                steps = ['pre', 'clean', 'post']
            else:
                steps = [parts[0]]
                
            for capability in capabilities:
                for step in steps:
                    self._steps.append(f'{capability}.{step}')
                    
    def get(self, step: str, capability: str) -> bool:
        return bool(any(item in f'{capability}.{step}' for item in self._steps))

    def get_pre(self, capability: str) -> bool:
        return bool(any(item in f'{capability}.pre' for item in self._steps))
    
    def get_run(self, capability: str) -> bool:
        return bool(any(item in f'{capability}.run' for item in self._steps))
    
    def get_post(self, capability: str) -> bool:
        return bool(any(item in f'{capability}.post' for item in self._steps))
    
    def get_clean(self, capability: str) -> bool:
        return bool(any(item in f'{capability}.clean' for item in self._steps))  
from logging import Logger
from typing import List

class StepsParser:
    """The steps parser is responsible for parsing the steps"""
    _steps: List[str] = []
    isCleanSteps: bool = False
    _logger : Logger

    def __init__(self, logger: Logger, steps: List[str]) -> None:
        capabilities = List[str]
        for step in steps:
            parts = step.split(':')
            
            if(parts[1] == 'all'):
                capabilities = ['global', 'code', 'build', 'test', 'deploy', 'release', 'operate', 'monitor', 'plan']
            else:
                capabilities = ['global', parts[1]]
            
            if(parts[0] == 'all'):
                steps = ['pre', 'run', 'post']
            elif(parts[0] == 'allclean'):
                steps = ['pre-clean', 'run-clean', 'post-clean']
                self.isCleanSteps = True
            else:
                steps = [parts[0]]
                
            if(parts[0] == 'pre-clean' or parts[0] == 'run-clean' or parts[0] == 'post-clean'):
                self.isCleanSteps = True
                
            for capability in capabilities:
                for step in steps:
                    self._steps.append(f'{capability}.{step}')
                    
    def get(self, step: str, capability: str) -> bool:
        return bool(any(item == f'{capability}.{step}' for item in self._steps))

    def get_pre(self, capability: str) -> bool:
        return bool(any(item == f'{capability}.pre' for item in self._steps))
    
    def get_run(self, capability: str) -> bool:
        return bool(any(item == f'{capability}.run' for item in self._steps))
    
    def get_post(self, capability: str) -> bool:
        return bool(any(item == f'{capability}.post' for item in self._steps))

    def get_preclean(self, capability: str) -> bool:
        return bool(any(item == f'{capability}.pre-clean' for item in self._steps))    
    
    def get_runclean(self, capability: str) -> bool:
        return bool(any(item == f'{capability}.run-clean' for item in self._steps)) 
     
    def get_postclean(self, capability: str) -> bool:
        return bool(any(item == f'{capability}.post-clean' for item in self._steps)) 
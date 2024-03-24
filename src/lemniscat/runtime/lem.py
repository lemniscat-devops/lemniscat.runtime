import argparse
import os
from lemniscat.runtime.version import __version__, __release_date__

## Debugging
if os.environ.get('LEM_DEBUG') == '1':
    print('Debug ON')
    import sys
    #sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) + '/core/src')
    print(sys.path)

from lemniscat.runtime.engine.engine_runtime import OrchestratorEngine

def __description() -> str:
    return "Lemniscat is a simple and lightweight orchestrator for running a sequence of tasks. It is designed to be used in a CI/CD pipeline, but can be used for any other purpose as well. It is designed to be simple and easy to use, but also powerful and flexible."


def __usage() -> str:
    return "lem --manifest [path to your manifest file] --steps [list of steps to execute]"

def __init_cli() -> argparse:
    parser = argparse.ArgumentParser(description=__description(), usage=__usage())
    parser.add_argument(
        '-m', '--manifest', required=True, 
        help="""(Required) Supply a manifest file which should be loaded. The default is ./manifest.yaml
        """
    )
    parser.add_argument(
        '-v', '--verbosity', default='INFO', help="""
        Specify log verbosity which should use. Default will always be DEBUG, choose between the following options
        CRITICAL, ERROR, WARNING, INFO, DEBUG
        """
    )
    parser.add_argument(
        '-s', '--steps', required=True, help="""
        (Optional) Supply a list of steps which should be executed. The default is ["run:all"]
        """
    )
    parser.add_argument(
        '-c', '--configFiles', default='[]', help="""
        (Optional) Supply a list of config files which should be loaded. The default is []
        """
    )
    parser.add_argument(
        '-x', '--extraVariables', default='{}', help="""
        (Optional) Supply a dictionary of variables which should be overridden. The default is {}
        """
    )
    parser.add_argument(
        '-o', '--outputContext', default=None, help="""
        (Optional) Supply a path to the output context. The default is None
        """
    )                  
    return parser


def __print_program_end() -> None:
    print("--------------------------------------------------------------")
    print("           |\      _,,,---,,_             █▀▀ █▀▀▄ █▀▀▄       ")
    print("     ZZZzz /,`.-'`'    -.  ;-;;,_         █▀▀ █  █ █  █       ")
    print("          |,4-  ) )-,_. ,\ (  `'-'        ▀▀▀ ▀  ▀ ▀▀▀        ")
    print("         '---''(_/--'  `-'\_)             of execution        ")
    print("--------------------------------------------------------------")


def __init_app(parameters: dict) -> None:
    print("")
    print("--------------------------------------------------------------")
    print("▒█░░░ █▀▀ █▀▄▀█ █▀▀▄ ░▀░ █ █▀▀░░░░░░░░░░░░░░░░▒█▀▀█ █▀▀█ ▀▀█▀▀")
    print("▒█░░░ █▀▀ █░▀░█ █░░█ ▀█▀ ░ ▀▀█░|\__/,|░░░(`\░░▒█░░░ █▄▄█ ░░█░░")
    print("▒█▄▄█ ▀▀▀ ▀░░░▀ ▀░░▀ ▀▀▀ ░ ▀▀_.|o o  |_░░░) )░▒█▄▄█ ▀░░▀ ░░▀░░")
    print("----------------------------(((---(((-------------------------")
    print(f"----------------- version {__version__} - {__release_date__} -----------------")
    print("--------------------------------------------------------------")
    print("")
    status = OrchestratorEngine(options=parameters).start()
    __print_program_end()
    if(status == 'Failed'):
        exit(1)

def lem() -> None:
    __cli_args = __init_cli().parse_args()
    __init_app({
        'manifest': __cli_args.manifest,
        'verbosity': __cli_args.verbosity,
        'steps': __cli_args.steps,
        'configFiles': __cli_args.configFiles,
        'extraVariables': __cli_args.extraVariables,
        'outputContext': __cli_args.outputContext
    })

if __name__ == '__main__':
    lem()
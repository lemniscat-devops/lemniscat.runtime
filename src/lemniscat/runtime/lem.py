import argparse
import os
from version import __version__, __release_date__

## Debugging
if os.environ.get('LEM_DEBUG') == '1':
    print('Debug ON')
    import sys
    #sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) + '/core/src')
    print(sys.path)

from lemniscat.runtime.engine.engine_runtime import OrchestratorEngine

def __description() -> str:
    return "Create your own anime meta data"


def __usage() -> str:
    return "vrv-meta.py --service vrv"

def __init_cli() -> argparse:
    parser = argparse.ArgumentParser(description=__description(), usage=__usage())
    parser.add_argument(
        '-m', '--manifest', required=True, 
        help="""(Required) Supply a manifest file which should be loaded. The default is ./manifest.yaml
        """
    )
    parser.add_argument(
        '-l', '--log', default='INFO', help="""
        Specify log level which should use. Default will always be DEBUG, choose between the following options
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
        '-o', '--overrideVariables', default='{}', help="""
        (Optional) Supply a dictionary of variables which should be overridden. The default is {}
        """
    )
    parser.add_argument(
        '-x', '--outpoutContext', default=None, help="""
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
    OrchestratorEngine(options=parameters).start()
    __print_program_end()

def lem() -> None:
    __cli_args = __init_cli().parse_args()
    __init_app({
        'manifest': __cli_args.manifest,
        'log_level': __cli_args.log,
        'steps': __cli_args.steps,
        'config_files': __cli_args.configFiles,
        'override_variables': __cli_args.overrideVariables,
        'output_context': __cli_args.outpoutContext
    })

if __name__ == '__main__':
    lem()
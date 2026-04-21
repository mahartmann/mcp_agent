class bcolors:
    USER = '\033[38;5;165m'
    ENVIRONMENT = '\033[38;5;28m'
    ASSISTANT = '\033[38;5;104m'
    SYSTEM = '\033[38;5;166m'
    ENDC = '\033[0m'


def print_colored(text: str|None, color: str) -> None:
    if text:
        print(color + text + bcolors.ENDC)


def print_user(text: str|None) -> None:
    if text:
        print_colored(text, bcolors.USER)


def print_assistant(text: str|None) -> None:
    if text:
        print_colored(text, bcolors.ASSISTANT)


def print_environment(text: str|None) -> None:
    print_colored(text, bcolors.ENVIRONMENT)


def print_system(text: str|None) -> None:
    if text:
        print_colored(text, bcolors.SYSTEM)
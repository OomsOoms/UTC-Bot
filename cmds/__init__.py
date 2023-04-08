# Init file for all commands

# from file name import init_function
from .add_event import init_add_event
from .event_selector import init_event_selector
from .results import init_results


def init_cmds(bot):
    #init_add_event(bot)
    init_event_selector(bot)
    init_results(bot)
# Init file for all commands

# from file name import init_function
from .add_event import init_add_event
from .create_thread import init_create_thread


def init_cmds(bot):
    init_add_event(bot)
    init_create_thread(bot)
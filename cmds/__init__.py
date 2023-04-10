# Init file for all commands

# Import the commands and their views
from .event_selector import init_event_selector, EventSelectorView
from .results import init_results_selector, ResultSelectorView

def init_cmds(bot):
    # Add the views to the bot
    bot.add_view(EventSelectorView())
    bot.add_view(ResultSelectorView())

    # Add the commands to the bot
    init_event_selector(bot)
    init_results_selector(bot)
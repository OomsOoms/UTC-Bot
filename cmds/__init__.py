# Init file for all commands

# Import the commands and their views
from .event_selector import init_event_selector, EventSelectorView
from .results_selector import init_results_selector, ResultSelectorView
from .day_selector import init_day_selector
from .submit import SubmitModalView, ConfirmModalView

def cmds(bot):
    # Add the commands to the bot
    init_event_selector(bot)
    init_results_selector(bot)
    init_day_selector(bot)

def views(bot):
    # Add the views to the bot
    bot.add_view(EventSelectorView())
    bot.add_view(ResultSelectorView())
    bot.add_view(SubmitModalView())
    bot.add_view(ConfirmModalView())
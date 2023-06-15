# Init file for all commands

# Import the commands and their views
from .event_selector import init_event_selector, EventSelectorView
from .result_command import init_results_command
from .submit import SubmitModalView, ConfirmModalView

def cmds(bot):
    # Add the commands to the bot
    init_event_selector(bot)
    init_results_command(bot)

def views(bot):
    # Add the views to the bot
    bot.add_view(EventSelectorView(bot))
    bot.add_view(SubmitModalView())
    bot.add_view(ConfirmModalView())
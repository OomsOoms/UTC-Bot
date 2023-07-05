# Init file for all commands

# Import the commands and their views
from .event_selector import init_event_selector, EventSelectorView
from .submit import SubmitButton

def cmds(bot):
    # Add the commands to the bot
    init_event_selector(bot)

def views(bot):
    # Add the views to the bot
    bot.add_view(EventSelectorView())
    bot.add_view(SubmitButton())

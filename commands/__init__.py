# Import the commands and their views
from .event_selector import event_dropdown, EventSelectorView
from .find_user_results import find_results
from .submit import SubmitButton

def cmds(bot):
    # Add the commands to the bot
    event_dropdown(bot)
    find_results(bot)

def views(bot):
    # Add the views to the bot
    bot.add_view(EventSelectorView())
    bot.add_view(SubmitButton())

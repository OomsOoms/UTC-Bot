# Import the commands and their views
from .event_selector import event_dropdown, EventSelectorView
from .find_user_results import find_results
from .submit import SubmitSolveButton, SubmitAverageButton
from .find_records import scrape_records
from .results import create_results, ResultEventSelector

def cmds(bot):
    # Add the commands to the bot
    event_dropdown(bot)
    find_results(bot)
    create_results(bot)

def views(bot):
    # Add the views to the bot
    bot.add_view(EventSelectorView())
    bot.add_view(SubmitSolveButton())
    bot.add_view(SubmitAverageButton())
    bot.add_view(ResultEventSelector(bot))

# Init file for all commands

# Import the commands and their views
from .event_selector import init_event_selector, EventSelectorView # Has caoomands and persistent views 
#from .result_command import init_results_command # Has caoomands
#from .submit import SubmitModalView, ConfirmModalView # Has persistent views 

def cmds(bot):
    # Add the commands to the bot
    init_event_selector(bot)
    #init_results_command(bot)
    pass

def views(bot):
    # Add the views to the bot
    bot.add_view(EventSelectorView(bot))
    #bot.add_view(SubmitModalView())
    #bot.add_view(ConfirmModalView())
    pass
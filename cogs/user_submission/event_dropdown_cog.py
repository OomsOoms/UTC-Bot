import traceback

from nextcord.ext.commands import Bot, Cog
from nextcord import slash_command

from utils.custom_logger import CustomLogger


from .modal import CompetitionIdModal
from .views import RequestHelpButton, EventSelectorDropdown

logger = CustomLogger(__name__)

def custom_decorator(func):
    async def wrapper(interaction, *args, **kwargs):
        logger.info("Custom decorator is running!")

        # Access interaction here
        # For example, you can access interaction.guild, interaction.author, etc.
        some_condition = True
        # Add your custom condition to stop the command from running
        if some_condition:
            logger.info("Command stopped by the custom decorator")
            await interaction.response.send_message("You are not authorized to run this command.", ephemeral=True)
            return  # Return here to stop the command from running
        
        # If the condition doesn't apply, proceed to the original function
        result = await func(interaction, *args, **kwargs)
        return result

    return wrapper



class EventDropdownCog(Cog):

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command(name="event-selector", description="Creates a dropdown menu where users can select an event", guild_ids=[988085977719402536])
    @custom_decorator  # Apply the custom decorator here
    async def event_selector(self, interaction):
        logger.info("Event selector command invoked")
        await interaction.response.send_modal(CompetitionIdModal())


def setup(bot: Bot):
    try:
        bot.add_cog(EventDropdownCog(bot))
        bot.add_view(EventSelectorDropdown())
        bot.add_view(RequestHelpButton())
        logger.info("Loaded extension")
    except Exception as e:
        exception = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        logger.error(f"Failed to load extension {__name__}\n{exception}")

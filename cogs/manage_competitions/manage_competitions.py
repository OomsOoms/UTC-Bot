import traceback
import secrets

from nextcord import Interaction, slash_command, SlashOption, Embed
from nextcord.ext.commands import Bot, Cog

from database import database_manager
from utils.custom_logger import CustomLogger

logger = CustomLogger(__name__)

class ManageCompetitions(Cog):

    choices = {event[1]: event[0] for event in database_manager.select_events()}

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command(name="create-competition", description="In testing", guild_ids=[988085977719402536])
    async def create_competition(
        self,
        interaction: Interaction,
        competition_name: str = SlashOption(name="competition-name", description="The name of the competition", required=True),
        event_1: str = SlashOption(choices=choices, required=True, name="main-event", description="Select the main event for your competition"),
        event_2: str = SlashOption(choices=choices, required=False, name="second-event", description="Select another event for your competition"),
        event_3: str = SlashOption(choices=choices, required=False, name="third-event", description="Select another event for your competition"),
        event_4: str = SlashOption(choices=choices, required=False, name="fourth-event", description="Select another event for your competition"),
        event_5: str = SlashOption(choices=choices, required=False, name="fifth-event", description="Select another event for your competition")
    ) -> None:

        competition_id = secrets.token_hex(8)
        database_manager.insert_competition(competition_name, competition_id, interaction.user.id, event_1, event_2, event_3, event_4, event_5)

        events = [event_1, event_2, event_3, event_4, event_5]
        events = [event for event in events if event is not None]
        events_str = "\n".join(events)
        
        embed = Embed(title=competition_name, description=f"Created by <@{interaction.user.id}>")
        embed.add_field(name="Event IDs", value=events_str)
        embed.add_field(name="Competition ID", value=competition_id)
        embed.add_field(name="Status", value="Active")
        embed.add_field(value="[Website](https://www.youtube.com/watch?v=dQw4w9WgXcQ)\n[Competition](https://www.youtube.com/watch?v=dQw4w9WgXcQ)\n[Results](https://www.youtube.com/watch?v=dQw4w9WgXcQ)", name="Links", inline=False)
        embed.add_field(value="Info that doesnt exist yet", name="Important Note", inline=False)
       
        await interaction.user.send(embed=embed)
        await interaction.response.send_message(embed=embed, ephemeral=True)


# Define the setup function for the cog
def setup(bot: Bot) -> None:
    try:
        bot.add_cog(ManageCompetitions(bot))
        logger.info(f"Loaded extension")
    except Exception as e:
        exception = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        logger.error(f"Failed to load extension {__name__}\n{exception}")

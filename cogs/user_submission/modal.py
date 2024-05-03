from nextcord import Interaction, Embed, PermissionOverwrite
from nextcord.ui import Modal, TextInput

from database import database_manager
from utils.custom_logger import CustomLogger
from .views import EventSelectorDropdown

logger = CustomLogger(__name__)

class CompetitionIdModal(Modal):
    
    def __init__(self):
        super().__init__("Competition credentials")
        self.competition_id = TextInput(label="Competition ID", min_length=3, max_length=128, required=True, placeholder="Enter the ID")
        self.add_item(self.competition_id)

    async def callback(self, interaction: Interaction) -> None:
        competition_data = database_manager.select_competition(self.competition_id.value)
        competition_id, competition_name, host_id, active, extra_info = competition_data
        
        if not competition_data:
            await interaction.response.send_message("Invalid credentials", ephemeral=True)
            return

        if not active:
            await interaction.response.send_message("This competition is not active", ephemeral=True)
            return

        logger.info(f"Event selector for ID: {competition_id} created")

        embed = Embed(
            title=competition_name,
            color=0xffa500,
            description="""- Select an event you would like to compete in
                          \n- A private thread contain`ing scrambles and more information will be created. Here you can submit your times.
                          \nIf you have any questions feel free to ask! And remember it's always worth competing for the fun!
                          """
        )

        if extra_info:
            embed.add_field(name="Extra information", value=extra_info)

        view = EventSelectorDropdown()
        message = await interaction.send(embed=embed, view=view)
        view.update_options()
        await message.edit(view=view)

        channel = interaction.channel
        default_role_permissions = PermissionOverwrite(send_messages=False, send_messages_in_threads=False)
        permissions = {channel.guild.default_role: default_role_permissions}
        await channel.edit(overwrites=permissions)

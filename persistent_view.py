import nextcord
from nextcord.ext import application_checks, commands

class PersistentView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label="Green", style=nextcord.ButtonStyle.green, custom_id="persistent_view:green"
    )
    async def green(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("This is green.", ephemeral=True)

    @nextcord.ui.button(
        label="Red", style=nextcord.ButtonStyle.red, custom_id="persistent_view:red"
    )
    async def red(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("This is red.", ephemeral=True)

    @nextcord.ui.button(
        label="Grey", style=nextcord.ButtonStyle.grey, custom_id="persistent_view:grey"
    )
    async def grey(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("This is grey.", ephemeral=True)
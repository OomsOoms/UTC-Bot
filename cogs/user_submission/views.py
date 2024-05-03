import nextcord
from nextcord import Interaction, SelectOption, Embed
from nextcord.ui import View, button, Select, select

from database import database_manager
from .submit import submit


class EventSelectorDropdown(View):

    def __init__(self):
        super().__init__(timeout=None)

    def update_options(self):
        competition_events = database_manager.select_competition_events((self.competition_id,))
        options = [nextcord.SelectOption(label=record[2], value=f"{record[0]},{record[1]},{record[2]},{record[3]},f") for record in competition_events]

        if len(options) == 0:
            options.append(nextcord.SelectOption(label="No events available", value="None"))

        return options

    @select(placeholder="Select an event", options=[SelectOption(label="No events available", value="None")], custom_id="EventSelectorView:dropdown")
    async def dropdown(self, select: Select, interaction: Interaction):
        if select.values[0] == "None":
            return

        competition_id, event_id, event_name, video_evidence, round_type = select.values[0].split(",")
        participated = database_manager.check_participation(competition_id, interaction.user.id, event_id, round_type)

        if not participated:
            await interaction.response.defer()

            thread = await interaction.channel.create_thread(name=f"{event_name}", reason=f"{interaction.user} {event_id} submit thread", auto_archive_duration=None, type=nextcord.ChannelType.private_thread)
            
            database_manager.insert_thread(thread.id, interaction.user.id, event_id, competition_id, round_type)
            embed = Embed(title="How to submit your average", color=0xffa500, description="- Follow the scramble and time your solve\n - Try to follow the WCA regulations when solving\n- Click the blue submit button below the scramble\n - Enter the time in the format MM:SS.MS\n- Submit your average! This is automatically calculated by the bot\n - The average will NOT be recorded until you click the green button at the end")

            if video_evidence:
                embed.add_field(name="Video evidence", value="\n- If you think you may win, record your average\n- Have the cube and timer in shot\n- If possible, have the screen in shot as well")

            await thread.send(f"<@{interaction.user.id}>", embed=embed, view=RequestHelpButton())
            await submit(thread)
        else:
            if "threads" in participated[0]:
                await interaction.response.send_message(f"You already have a thread for this event! <#{participated[0][1]}>", ephemeral=True)
            else:
                await interaction.response.send_message("You have already submitted this event!", ephemeral=True)


class RequestHelpButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Request assistance", style=nextcord.ButtonStyle.primary, custom_id="RequestAssistanceButton:request")
    async def request_assistance(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.send("Help is on its way!", ephemeral=True)
        
        message = f"**<@{interaction.user.id}> needs help!**\n\n"
        
        admin_role_mentions = [f"<@&{role.id}>" for i, role in enumerate(sorted(interaction.guild.roles, key=lambda x: x.position, reverse=True)) if i <= 1 and role.permissions.administrator]
        
        if admin_role_mentions:
            message += "\n".join(admin_role_mentions)
            button.disabled = True
            await interaction.message.edit(view=self)
        else:
            message = "No one available to help"
            
        await interaction.channel.send(message)

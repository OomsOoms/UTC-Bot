import sqlite3
import pickle
import nextcord
from nextcord import Embed
from .submit import submit

# Establish a connection to the database
conn = sqlite3.connect("data/utc_database.db")

def update_dropdown():
    options = [nextcord.SelectOption(label="3x3 Cube", value="competitionId,333,3x3 Cube,1"), nextcord.SelectOption(label="2x2 Cube", value="competitionId,222,2x2 Cube,1")]

    return options


class EventSelectorView(nextcord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    # Define the select menu
    @nextcord.ui.select(
        placeholder="Select an event", options=update_dropdown(), custom_id="EventSelectorView:dropdown"
    )

    async def dropdown(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):

        await interaction.response.defer()

        cursor = conn.cursor()

        competition_id, event_id, event_name, round_type = select.values[0].split(",")

        # Execute the query to search for competition_id in the competitions table
        #cursor.execute("SELECT * FROM competitions WHERE competition_id = ?", (competition_id,))
        #competition = cursor.fetchone()
        cursor.execute("SELECT * FROM threads WHERE user_id = ? AND competition_id = ? AND event_id = ?", (interaction.user.id, competition_id, event_id))
        user_event_data = cursor.fetchone()

        if True: # not user_event_data: just so i can test

            thread = await interaction.channel.create_thread(name=event_name, reason=f"{interaction.user} {event_id} submit thread", auto_archive_duration=None, type=nextcord.ChannelType.private_thread)

            cursor = conn.cursor()
            cursor.execute("INSERT INTO threads (thread_id, user_id, event_id, competition_id, solve_num, round_type) VALUES (?, ?, ?, ?, 1, ?)",
                            (thread.id, interaction.user.id, event_id, competition_id, round_type))
            conn.commit()

            embed = nextcord.Embed(title="Info", description="Info")

            await thread.send(f"<@{interaction.user.id}>", embed=embed)

            await submit(thread)

        cursor.close()


class EmbedModal(nextcord.ui.Modal):

    def __init__(self):
        super().__init__("Competition credentials")

        self.competition_id = nextcord.ui.TextInput(label="Competition ID", min_length=3, max_length=128, required=True, placeholder="Enter the ID")
        self.add_item(self.competition_id)

        self.password = nextcord.ui.TextInput(label="Password", min_length=3, max_length=128, required=True, placeholder="Enter the admin password")
        self.add_item(self.password)

    async def callback(self, interaction: nextcord.Interaction) -> None:

        cursor = conn.cursor()
        cursor.execute("SELECT competition_id FROM competitions WHERE competition_id = ?", (self.competition_id.value,))
        competition = cursor.fetchone()
        cursor.close()

        if competition:
            # Create an Embed object with information about the competition
            embed = Embed(title="Cubing comp name", color=0xffa500)
            embed.add_field(name="Info", value="Info")
            embed.set_footer(text=self.competition_id.value)

            # Fetch the channel's permissions
            channel = interaction.channel
            permissions = channel.overwrites

            # Modify the permissions to disallow @everyone from sending messages in the channel and threads
            default_role_permissions = permissions.get(channel.guild.default_role, nextcord.PermissionOverwrite())
            default_role_permissions.send_messages = False
            default_role_permissions.send_messages_in_threads = False
            permissions[channel.guild.default_role] = default_role_permissions

            await channel.edit(overwrites=permissions)

            await interaction.send(embed=embed, view=EventSelectorView())
        else:
            await interaction.response.send_message("Invalid credentials", ephemeral=True)


def init_event_selector(bot):
    @bot.slash_command(name="event-selector",description="Creates a dropdown menu where users can select an event")
    async def event_selector(ctx):
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message("You are not authorized to run this command.", ephemeral=True)
        else:
            await ctx.response.send_modal(EmbedModal())

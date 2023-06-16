import sqlite3
import pickle
import nextcord
from nextcord import Embed
from .submit import submit
from .create_competition import Competition


def update_dropdown():
    # Create the select menu options
    options = [nextcord.SelectOption(label="event_name", value="Test0623013:eventId,Event name")]

    return options

class EventSelectorView(nextcord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    # Define the select menu
    @nextcord.ui.select(
        placeholder="Select an option", options=update_dropdown(), custom_id="EventSelectorView:dropdown"
    )

    async def dropdown(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):

        competition_id, temp = select.values[0].split(":")
        event_id, event_name = temp.split(",")

        # Establish a connection to the database
        with sqlite3.connect("data/utc_database.db") as conn:

            # Create a cursor object to execute SQL queries
            cursor = conn.cursor()

            # Execute the query to search for competition_id in the competitions table
            cursor.execute("SELECT * FROM competitions WHERE competition_id = ?", (competition_id,))

            # Fetch the results of the query
            result = cursor.fetchone()

        if result:
            # Get and deserialized the competition object frpm column 2
            deserialized_object = pickle.loads(result[1])

            print(deserialized_object)

        # Create a new thread in the channel
        thread = await interaction.channel.create_thread(name=event_name, auto_archive_duration=None, type=nextcord.ChannelType.private_thread)

        await thread.add_user(interaction.user)
        await submit(interaction=interaction, thread=thread)

    
def init_event_selector(bot):
    @bot.slash_command(name="event-selector", description="Creates a private thread for the user who clicks the button in the dropdown")
    async def event_selector(ctx):
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message("You are not authorized to run this command.", ephemeral=True)
        else:
            # Create an Embed object with information about the competition
            embed = Embed(title="Cubing comp name", color=0xffa500)
            embed.add_field(name="Info", value="Info")

            # Fetch the channel's permissions
            channel = ctx.channel
            permissions = channel.overwrites

            # Modify the permissions to disallow @everyone from sending messages in the channel
            channel_permissions = permissions.get(channel.guild.default_role) or nextcord.PermissionOverwrite()
            channel_permissions.send_messages = False
            permissions[channel.guild.default_role] = channel_permissions

            # Modify the permissions to disallow @everyone from sending messages in threads
            thread_permissions = permissions.get(channel.guild.default_role) or nextcord.PermissionOverwrite()
            thread_permissions.send_messages_in_threads = False
            permissions[channel.guild.default_role] = thread_permissions

            # Update the channel's permissions with the modified settings
            await channel.edit(overwrites=permissions)

            # Send the embed to a channel or user
            await ctx.send(embed=embed, view=EventSelectorView(bot))

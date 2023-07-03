import sqlite3
import pickle
import nextcord
from nextcord import Embed
from .submit import submit


def find_competition(competition_id):
    # Establish a connection to the database
    with sqlite3.connect("data/utc_database.db") as conn:

        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()

        # Execute the query to search for competition_id in the competitions table
        cursor.execute("SELECT * FROM competitions WHERE competition_id = ?", (competition_id,))

        # Fetch the results of the query
        result = cursor.fetchone()
        
        if result: result = pickle.loads(result[1])

    # Returns an object if found, returns None if not found
    return result

def update_competition(competition_id, new_data):
    # Establish a connection to the database
    with sqlite3.connect("data/utc_database.db") as conn:

        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()

        # Serialize the new data using pickle
        serialized_data = pickle.dumps(new_data)

        # Execute the query to update the record with the new data
        cursor.execute("UPDATE competitions SET serialized_data = ? WHERE competition_id = ?", (serialized_data, competition_id))

        # Commit the changes to the database
        conn.commit()

    
def update_dropdown():
    # Create the select menu options
    competition_id = "Test0723000"
    options = [nextcord.SelectOption(label="event_name", value=f"{competition_id},eventId,Event name")]

    return options
    

class Competitor:

    def __init__(self):

        self.events = {} # event id:[thread id,[results]]


class EventSelectorView(nextcord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)

        self.bot = bot

    # Define the select menu
    @nextcord.ui.select(
        placeholder="Select an event", options=update_dropdown(), custom_id="EventSelectorView:dropdown"
    )

    async def dropdown(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):

        await interaction.response.defer()

        competition_id, event_id, event_name = select.values[0].split(",")

        competition_object = find_competition(competition_id)

        if competition_object:
            competitors = competition_object.competitors
            competitor_object = competitors.get(interaction.user.id)

            if not competitor_object:
                competitor_object = Competitor()
                competitors[interaction.user.id] = competitor_object

            if event_id not in competitor_object.events.keys():
                # Create a new thread in the channel
                thread = await interaction.channel.create_thread(name=event_name, auto_archive_duration=None, type=nextcord.ChannelType.private_thread)
                # Update the competitor's events list
                competitor_object.events[event_id] = (thread.id, [])
                # Update the competition object in the database
                update_competition(competition_id, competition_object)

                await submit(interaction=interaction, thread=thread, competition_object=competition_object)


class EmbedModal(nextcord.ui.Modal):
    def __init__(self, bot):
        super().__init__("Competition credentials")

        self.bot = bot

        self.competition_id = nextcord.ui.TextInput(label="Competition ID", min_length=8, max_length=128, required=True, placeholder="Enter the ID")
        self.add_item(self.competition_id)

        self.password = nextcord.ui.TextInput(label="Password", min_length=8, max_length=128, required=True, placeholder="Enter the admin password")
        self.add_item(self.password)


    async def callback(self, interaction: nextcord.Interaction) -> None:

        competition_object = find_competition(self.competition_id.value)

        if competition_object:
        
            # Create an Embed object with information about the competition
            embed = Embed(title="Cubing comp name", color=0xffa500)
            embed.add_field(name="Info", value="Info")
            embed.set_footer(text=self.competition_id.value)

            # Fetch the channel's permissions
            channel = interaction.channel
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
            await interaction.send(embed=embed, view=EventSelectorView(self.bot))

        else:
            await interaction.response.send_message("Invalid credentials", ephemeral=True)

    
def init_event_selector(bot):
    @bot.slash_command(name="event-selector", description="Creates a private thread for the user who clicks the button in the dropdown")
    async def event_selector(ctx):
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message("You are not authorized to run this command.", ephemeral=True)
        else:
            modal = EmbedModal(bot)
            await ctx.response.send_modal(modal)

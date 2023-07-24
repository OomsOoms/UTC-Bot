import nextcord
from nextcord import Embed
from .submit import submit

from utils.database import conn


def generate_options(competition_id):
    cursor = conn.cursor()

    cursor.execute("SELECT c.competition_id, c.event_id, e.event_name FROM competition_events c "
                   "JOIN events e ON c.event_id = e.event_id WHERE c.competition_id = ?", (competition_id,))
    records = cursor.fetchall()

    options = [nextcord.SelectOption(
        label=record[2], value=f"{record[0]},{record[1]},{record[2]},f") for record in records]

    # If no events are available, create a single option saying "No events available."
    if len(options) == 0:
        options.append(nextcord.SelectOption(
            label="No events available", value="None"))

    return options


class EventSelectorView(nextcord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    # Method to update the options after the message is sent
    def update_options(self, competition_id):
        options = generate_options(competition_id)
        for child in self.children:
            if isinstance(child, nextcord.ui.Select):
                child.options = options
                break

    # Define the select menu with default options (can be changed later)
    @nextcord.ui.select(
        placeholder="Select an event", options=[nextcord.SelectOption(label="No events available", value="None")], custom_id="EventSelectorView:dropdown"
    )
    async def dropdown(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):
        if select.values[0] == "None":
            return  # Skip further processing

        await interaction.response.defer()

        cursor = conn.cursor()

        competition_id, event_id, event_name, round_type = select.values[0].split(",")
        
        # Checks if a thread already exists for this user event and competition
        cursor.execute("SELECT * FROM threads WHERE user_id = ? AND competition_id = ? AND event_id = ?",
                       (interaction.user.id, competition_id, event_id))
        user_event_data = cursor.fetchone()

        if not user_event_data:  # if not true they havent competed

            thread = await interaction.channel.create_thread(name=event_name, reason=f"{interaction.user} {event_id} submit thread", auto_archive_duration=None, type=nextcord.ChannelType.private_thread)

            cursor = conn.cursor()
            cursor.execute("INSERT INTO threads (thread_id, user_id, event_id, competition_id, solve_num, round_type) VALUES (?, ?, ?, ?, 0, ?)",
                           (thread.id, interaction.user.id, event_id, competition_id, round_type))
            conn.commit()

            embed = nextcord.Embed(title="Info", description="Info")

            await thread.send(f"<@{interaction.user.id}>", embed=embed)

            await submit(thread)

        cursor.close()


class EmbedModal(nextcord.ui.Modal):

    def __init__(self):
        super().__init__("Competition credentials")

        self.competition_id = nextcord.ui.TextInput(
            label="Competition ID", min_length=3, max_length=128, required=True, placeholder="Enter the ID")
        self.add_item(self.competition_id)

    async def callback(self, interaction: nextcord.Interaction) -> None:

        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM competitions WHERE competition_id = ?", (self.competition_id.value,))
        competition_info = cursor.fetchone()
        cursor.close()

        if competition_info:
            # Create an Embed object with information about the competition
            embed = Embed(title=competition_info[1], color=0xffa500)
            embed.add_field(name="infomation", value=competition_info[3])
            embed.set_footer(text=competition_info[0])

            # Fetch the channel's permissions
            channel = interaction.channel
            permissions = channel.overwrites

            # Modify the permissions to disallow @everyone from sending messages in the channel and threads
            default_role_permissions = permissions.get(
                channel.guild.default_role, nextcord.PermissionOverwrite())
            default_role_permissions.send_messages = False
            default_role_permissions.send_messages_in_threads = False
            permissions[channel.guild.default_role] = default_role_permissions

            await channel.edit(overwrites=permissions)

            # Create the view with initial options based on competition_info[0]
            view = EventSelectorView()

            # Send the message with the view
            message = await interaction.send(embed=embed, view=view)

            # Now, immediately after sending the message, update the options
            view.update_options(competition_info[0])

            # If you want to edit the message to reflect the updated options, you can use:
            await message.edit(view=view)

        else:
            await interaction.response.send_message("Invalid credentials", ephemeral=True)


def event_dropdown(bot):
    @bot.slash_command(name="event-selector", description="Creates a dropdown menu where users can select an event")
    async def event_selector(ctx):
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message("You are not authorized to run this command.", ephemeral=True)
        else:
            await ctx.response.send_modal(EmbedModal())

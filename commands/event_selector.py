import nextcord
from nextcord import Embed
from .submit import submit

from utils.database import conn


def generate_options(competition_id): # By default all rounds set to f as there is no round system in place yet these options are written to the threads table when selected
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

        cursor = conn.cursor()

        competition_id, event_id, event_name, round_type = select.values[0].split(",")
        
        # Checks if a thread already exists for this user event and competition
        cursor.execute("SELECT thread_id FROM threads WHERE user_id = ? AND competition_id = ? AND event_id = ?",
                       (interaction.user.id, competition_id, event_id))
        thread_id = cursor.fetchone()

        cursor.execute("SELECT * FROM results WHERE user_id = ? AND competition_id = ? AND event_id = ?",
                (interaction.user.id, competition_id, event_id))
        in_results = cursor.fetchone()

        if True: #(not thread_id) and not in_results:  # if not true they havent competed

            await interaction.response.defer()

            thread = await interaction.channel.create_thread(name=f"{event_name}", reason=f"{interaction.user} {event_id} submit thread", auto_archive_duration=None, type=nextcord.ChannelType.private_thread)

            cursor = conn.cursor()
            cursor.execute("INSERT INTO threads (thread_id, user_id, event_id, competition_id, solve_num, round_type) VALUES (?, ?, ?, ?, 0, ?)",
                           (thread.id, interaction.user.id, event_id, competition_id, round_type))
            conn.commit()

            embed = nextcord.Embed(title="How to submit your average", color=0xffa500, description="- Follow the scramble and time your solve\n - Try to follow the WCA regulations when solving\n- Click the blue submit button below the scramble\n - Enter the time in the format MM:SS.MS\n- Submit your average! This is automatically caculated by the bot\n - The average will NOT be recorded until you click the green button at the end\n\n**Remember if you think you may win record your cube with your screen in shot**")

            await thread.send(f"<@{interaction.user.id}>", embed=embed)

            await submit(thread)

        else:
            if in_results:
                await interaction.response.send_message("You have already submitted this event!", ephemeral=True)
            else:
                await interaction.response.send_message(f"You have already have a thread for this event! <#{thread_id[0]}>", ephemeral=True)

        cursor.close()


class CompetitionIdModal(nextcord.ui.Modal):

    def __init__(self):
        super().__init__("Competition credentials")

        self.competition_id = nextcord.ui.TextInput(
            label="Competition ID", min_length=3, max_length=128, required=True, placeholder="Enter the ID")
        self.add_item(self.competition_id)

    async def callback(self, interaction: nextcord.Interaction) -> None:

        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM competitions WHERE competition_id = ?", (self.competition_id.value,))
        try: competition_id, competition_name, extra_info = cursor.fetchone()
        except: competition_id = None
        cursor.close()

        if competition_id:
            # Create an Embed object with information about the competition
            embed = Embed(title=competition_name, color=0xffa500, description="- Select an event you would like to compete in\n- A private thread containing scrambles and more infomation will be created. Here you can submit your times.\nIf you have any questions feel free to ask! And remember its always worth competing for the fun!")
            if extra_info:
                embed.add_field(name="Extra infomation", value=extra_info)

            # Fetch the channel's permissions
            channel = interaction.channel
            permissions = channel.overwrites

            # Modify the permissions to disallow @everyone from sending messages in the channel and threads
            default_role_permissions = permissions.get(channel.guild.default_role, nextcord.PermissionOverwrite())
            default_role_permissions.send_messages = False
            default_role_permissions.send_messages_in_threads = False
            permissions[channel.guild.default_role] = default_role_permissions

            await channel.edit(overwrites=permissions)

            # Create the view with initial options based on competition_info[0]
            view = EventSelectorView()

            # Send the message with the view
            message = await interaction.send(embed=embed, view=view)

            # Now, immediately after sending the message, update the options
            view.update_options(competition_id)

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
            await ctx.response.send_modal(CompetitionIdModal())

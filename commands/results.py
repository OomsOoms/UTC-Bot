import nextcord
from nextcord import SlashOption

from utils.database import execute_query
from .event_selector import generate_options

def generate_results_embed(event_results):

    num_highlight = 3  # Replace this with the number of rows you want to highlight

    # Define maximum width for each column
    max_rank_width = 3
    max_user_name_width = 20
    max_value_width = 8

    # Define the column headers with left alignment
    header_row = f"{'Rank'.ljust(max_rank_width)} {'User'.ljust(max_user_name_width)} {'1'.rjust(max_value_width)} {'2'.rjust(max_value_width)} {'3'.rjust(max_value_width)} {'4'.rjust(max_value_width)} {'5'.rjust(max_value_width)} {'Average'.rjust(max_value_width)} {'Best'.rjust(max_value_width)}"

    # Truncate user names longer than their respective max width
    user_names = [str(row[3])[:max_user_name_width] for row in event_results]

    # Add padding to user names to match their respective max width
    user_names = [name.ljust(max_user_name_width) for name in user_names]

    # Define the rows with right alignment for value, average, and best columns
    rows = []
    for index, row in enumerate(event_results):
        values = [str(row[i]) for i in range(9, 14)]  # Get the "1" to "5" columns (index 9 to 13)
        average = str(row[8]).rjust(max_value_width)
        best = str(min(row[9:14])).rjust(max_value_width)  

        row_text = f"{str(index+1).ljust(max_rank_width)}{user_names[index].ljust(max_user_name_width)} {values[0].rjust(max_value_width)} {values[1].rjust(max_value_width)} {values[2].rjust(max_value_width)} {values[3].rjust(max_value_width)} {values[4].rjust(max_value_width)} {average} {best}"

        # Highlight the first num_highlight rows in green
        if index < num_highlight:
            rows.append(f"+ {row_text}")
        else:
            rows.append(f"  {row_text}")

    # Combine the header and rows into a single message
    message = header_row + "\n" + "-" * len(header_row) + "\n" + "\n".join(rows)

    return message


class ResultEventSelector(nextcord.ui.View):

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
        placeholder="Select an event", options=[nextcord.SelectOption(label="No events available", value="None")], custom_id="ResultEventSelector:dropdown"
    )
    async def dropdown(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):
        
        await interaction.response.defer()

        if select.values[0] == "None":
            return  # Skip further processing

        competition_id, event_id, event_name, round_type = select.values[0].split(",")

        results = execute_query("SELECT_event_results", (competition_id, event_id)).fetchall()

        message = generate_results_embed(results)

        message_chunks = []
        current_chunk = ""
        for line in message.splitlines():
            if len(current_chunk + line) > 2000:
                message_chunks.append(current_chunk)
                current_chunk = ""
            current_chunk += line + "\n"
        message_chunks.append(current_chunk)

        for i, message in enumerate(message_chunks):
            if i == 0:
                await interaction.channel.send(f"**{event_name} Results**")

            await interaction.channel.send(f"```diff\n{message}```\n_ _")


class ResultsCompetitionId(nextcord.ui.Modal):

    def __init__(self):
        super().__init__("Competition credentials")

        self.competition_id = nextcord.ui.TextInput(
            label="Competition ID", min_length=3, max_length=128, required=True, placeholder="Enter the ID")
        self.add_item(self.competition_id)

    async def callback(self, interaction: nextcord.Interaction) -> None:

        competition_data = execute_query("SELECT_competition", (self.competition_id.value,)).fetchone()

        if competition_data:
            view = ResultEventSelector()

            message = await interaction.response.send_message("Select an event to display results for.", view=view, ephemeral=True)

            view.update_options(self.competition_id.value)

            await message.edit(view=view)
        
        else:
            await interaction.response.send_message("Invalid credentials", ephemeral=True)


def create_results(bot):
    @bot.slash_command(name="results", description="Creates a private thread for the user who clicks the button in the dropdown")
    async def results_command(ctx):
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message("You are not authorized to run this command.")
        else:
            await ctx.response.send_modal(ResultsCompetitionId())
            
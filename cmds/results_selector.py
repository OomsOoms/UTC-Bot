import nextcord
import pandas as pd
from nextcord import Embed


results = pd.read_csv('data/Results.tsv', sep='\t')
competitions = pd.read_csv('data/Competitions.tsv', sep='\t')
events_data_list = pd.read_csv("data/Events.tsv", sep='\t').to_dict("list")

async def generate_results_embed(bot, event_name, event_results):

    # Define maximum width for each column
    max_rank_width = 3
    max_user_name_width = 20
    max_guild_name_width = 20
    max_value_width = 8
    num_highlight = 3

    # Define the column headers with left alignment
    header_row = f"{'Rank'.ljust(max_rank_width)} {'User'.ljust(max_user_name_width)} {'Guild Name'.ljust(max_guild_name_width)} {'1'.rjust(max_value_width)} {'2'.rjust(max_value_width)} {'3'.rjust(max_value_width)} {'4'.rjust(max_value_width)} {'5'.rjust(max_value_width)} {'Average'.rjust(max_value_width)} {'Best'.rjust(max_value_width)}"

    user_names = []
    guild_names = []
    for i, row in event_results.iterrows():
        guild_id = row['guild_id']
        user_id = row['user_id']
        try:
            user = await bot.fetch_user(user_id)
            user = user.name
            user_names.append(user)
            
        except:
            user_names.append("Unknown User")

        try:
            guild = await bot.fetch_guild(guild_id)
            guild_names.append(guild.name if guild else 'Unknown Guild')
        except:
            guild_names.append('Unknown Guild')

    # Truncate guild names and user IDs longer than their respective max width
    guild_names = [name[:max_guild_name_width] for name in guild_names]
    user_names = [name[:max_user_name_width] for name in user_names]

    # Add padding to guild names and user IDs to match their respective max width
    guild_names = [name.ljust(max_guild_name_width) for name in guild_names]
    user_names = [name.ljust(max_user_name_width) for name in user_names]

    event_results = event_results.reset_index(drop=True)

    # Define the rows with right alignment for value, average, and best columns
    rows = []
    for fuck, row in event_results.iterrows():

        

        
        value_1 = f"{str(row['value_1'])[:-2]}.{str(row['value_1'])[-2:]}" if row['value_1'] != -1 else "DNF"
        value_2 = f"{str(row['value_2'])[:-2]}.{str(row['value_2'])[-2:]}" if row['value_2'] != -1 else "DNF"
        value_3 = f"{str(row['value_3'])[:-2]}.{str(row['value_3'])[-2:]}" if row['value_3'] != -1 else "DNF"
        value_4 = f"{str(row['value_4'])[:-2]}.{str(row['value_4'])[-2:]}" if row['value_4'] != -1 else "DNF"
        value_5 = f"{str(row['value_5'])[:-2]}.{str(row['value_5'])[-2:]}" if row['value_5'] != -1 else "DNF"
        average = f"{str(row['average'])[:-2]}.{str(row['average'])[-2:]}" if row['average'] != -1 else "DNF"
        best = f"{str(row['best'])[:-2]}.{str(row['best'])[-2:]}" if row['best'] != -1 else "DNF"

        

        row_text = f"{str(fuck+1).ljust(max_rank_width)}{user_names[fuck].ljust(max_guild_name_width)} {guild_names[fuck].ljust(max_guild_name_width)} {value_1.rjust(max_value_width)} {value_2.rjust(max_value_width)} {value_3.rjust(max_value_width)} {value_4.rjust(max_value_width)} {value_5.rjust(max_value_width)} {average.rjust(max_value_width)} {best.rjust(max_value_width)}"
        
        # Highlight the first num_highlight rows in green
        if fuck < num_highlight:
            rows.append(f"+ {row_text}")
        else:
            rows.append(f"  {row_text}")

    # Combine the header and rows into a single message
    message =  header_row + "\n" + "-" * len(header_row) + "\n" + "\n".join(rows)


    message = "diff\n" + message + "\n"

    return message



class ResultSelectorView(nextcord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    options = [nextcord.SelectOption(label=event, value=f"{event},{eventId}") for event, eventId in zip(
        events_data_list["name"], events_data_list["event_id"])]

    @nextcord.ui.select(
        placeholder="Select an option", options=options, custom_id="ResultSelectorView:dropdown"
    )
    async def dropdown(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):
        await interaction.response.defer()

        # Get the selected option's label and value
        event_name, event_id = interaction.data['values'][0].split(",")

        competition_id = competitions[competitions["active_day"] != 0].iloc[0]["competition_id"]

        round_num = "f"

        try:
            event_results = results[(results['competition_id'].astype(str) == str(competition_id)) & 
                                    (results['event_id'].astype(str) == str(event_id)) & 
                                    (results['round_type'].astype(str) == str(round_num))]
                
            if not event_results.empty:
                message = await generate_results_embed(self.bot, event_name, event_results)
                embed = Embed(title=f"{event_name} Results", description=message, color=0xffa500)


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

                    await interaction.channel.send(f"```{message}```")
            else:
                await interaction.response.send_message(f"The results for this {event_name} are not available yet", ephemeral=True)

        except IndexError:
            await interaction.response.send_message(f"The results for this {event_name} are not available yet", ephemeral=True)


def init_results_selector(bot):
    @bot.slash_command(name="results-selector", description="Creates a private thread for the user who clicks the button in the dropdown")
    async def results_selector(ctx):

        # Create an Embed object with information about the competition
        embed = Embed(title="Cubing Competition Information", color=0xffa500)
        embed.add_field(name="Event Selection", value="Select an event from the dropdown menu. Note that the events will change every day for each new round, so please check the dropdown menu regularly to see what events are available.")
        embed.add_field(name="Leaderboard", value="The leaderboard shows the results of each round for the selected event. To view the leaderboard, go to the private channel named `leaderboard [event name]` and select the round you want to view. If there are no results for a particular round, it means that the round hasn't happened yet, as results are only added after the round has finished.")
        embed.add_field(name="Good Luck!", value="Have fun competing! If you have any questions, feel free to ask in the designated discussion channel.")

        # Send the embed to a channel or user
        await ctx.send(embed=embed, view=ResultSelectorView(bot))
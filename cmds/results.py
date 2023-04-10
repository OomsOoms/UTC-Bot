import nextcord
import pandas as pd
from nextcord import Embed


results = pd.read_csv('data/Results.tsv', sep='\t')
competitions = pd.read_csv('data/Competitions.tsv', sep='\t')
events_data_list = pd.read_csv("data/Events.tsv", sep='\t').to_dict("list")


def generate_results_embed(event_name, event_results, num_highlight=8):
    
    # Define maximum width for each column
    max_rank_width = 3
    max_user_id_width = 15
    max_guild_name_width = 20
    max_value_width = 5
    
    # Truncate guild names and user IDs longer than their respective max width
    event_results['guild_id'] = event_results['guild_id'].apply(lambda x: x[:max_guild_name_width])
    event_results['user_id'] = event_results['user_id'].apply(lambda x: x[:max_user_id_width])
    
    # Add padding to guild names and user IDs to match their respective max width
    event_results['guild_id'] = event_results['guild_id'].apply(lambda x: x.ljust(max_guild_name_width))
    event_results['user_id'] = event_results['user_id'].apply(lambda x: x.ljust(max_user_id_width))
    
    # Define the column headers with left alignment
    header_row = f"{'Rank'.ljust(max_rank_width)} {'User'.ljust(max_user_id_width)} {'Guild Name'.ljust(max_guild_name_width)} {'1'.rjust(max_value_width)} {'2'.rjust(max_value_width)} {'3'.rjust(max_value_width)} {'4'.rjust(max_value_width)} {'5'.rjust(max_value_width)} {'Average'.rjust(max_value_width)} {'Best'.rjust(max_value_width)}"

    # Define the rows with right alignment for value, average, and best columns
    rows = []
    for i, row in event_results.iterrows():
        guild_name =  row['guild_id']
        row_text = f"{str(i+1).ljust(max_rank_width)}{str(row['user_id']).ljust(max_user_id_width)} {guild_name.ljust(max_guild_name_width)} {str(row['value_1']).rjust(max_value_width)} {str(row['value_2']).rjust(max_value_width)} {str(row['value_3']).rjust(max_value_width)} {str(row['value_4']).rjust(max_value_width)} {str(row['value_5']).rjust(max_value_width)} {str(row['average']).rjust(max_value_width)} {str(row['best']).rjust(max_value_width)}"
        
        # Highlight the first num_highlight rows in green
        if i < num_highlight:
            rows.append(f"+ {row_text}")
        else:
            rows.append(f"  {row_text}")

    # Combine the header and rows into a single message
    message = header_row + "\n" + "-" * len(header_row) + "\n" + "\n".join(rows)
    message = "```diff\n" + message + "\n```"
    
    return message


class ResultSelectorView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    options = [nextcord.SelectOption(label=event, value=f"{event},{eventId}") for event, eventId in zip(
        events_data_list["name"], events_data_list["event_id"])]

    @nextcord.ui.select(
        placeholder="Select an option", options=options, custom_id="ResultSelectorView:dropdown"
    )
    async def dropdown(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):
        # Get the selected option's label and value
        event_name, event_id = interaction.data['values'][0].split(",")

        competition_id = competitions.loc[competitions['active_day'] != False, 'competition_id'].item()

        round_num = 1

        try:
            event_results = results[(results['competition_id'] == competition_id) & 
                                    (results['event_id'].astype(str) == str(event_id)) & 
                                    (results['round_num'] == round_num)]
                
            if not event_results.empty:
                message = generate_results_embed(event_name, event_results)
                await interaction.response.send_message(message, ephemeral=True)
            else:
                await interaction.response.send_message(f"The results for this {event_name} are not available yet", ephemeral=True)

        except IndexError:
            await interaction.response.send_message(f"The results for this {event_name} are not available yet", ephemeral=True)


def init_results_selector(bot):
    @bot.slash_command(name="leaderboard", description="Creates a private thread for the user who clicks the button in the dropdown")
    async def leaderboard(ctx):

        # Create an Embed object with information about the competition
        embed = Embed(title="Cubing Competition Information", color=0xffa500)
        embed.add_field(name="Event Selection", value="Select an event from the dropdown menu. Note that the events will change every day for each new round, so please check the dropdown menu regularly to see what events are available.")
        embed.add_field(name="Leaderboard", value="The leaderboard shows the results of each round for the selected event. To view the leaderboard, go to the private channel named `leaderboard [event name]` and select the round you want to view. If there are no results for a particular round, it means that the round hasn't happened yet, as results are only added after the round has finished.")
        embed.add_field(name="Good Luck!", value="Have fun competing! If you have any questions, feel free to ask in the designated discussion channel.")

        # Send the embed to a channel or user
        await ctx.send(embed=embed, view=ResultSelectorView())
import pandas as pd
from nextcord import SlashOption

competitions = pd.read_csv('data/Competitions.tsv', sep='\t')
events_data_df = pd.read_csv("data/Events.tsv", sep='\t')
schedule = pd.read_csv("data/Schedules.tsv", sep='\t')

def format_value(val):
    if pd.isna(val):
        return ""
    elif val == -1:
        return "DNF"
    else:
        return f"{str(val)[:-2]}.{str(val)[-2:]}"

async def generate_results_embed(bot, event_id, event_results, competition_id, round_type):

    event_results = event_results.sort_values(by="average", key=lambda x:x.astype(int), ascending=True)

    # Filter the schedules DataFrame based on the filtering criteria
    filtered_schedule = schedule[(schedule['competition_id'].astype(str) == str(competition_id)) &
                                (schedule['event_id'].astype(str) == str(event_id)) &
                                (schedule['round'].astype(str) == str(round_type))]

    num_highlight = filtered_schedule['advance'].values[0]

    if num_highlight < 1:
        num_highlight = int(num_highlight*len(event_results))

    # Define maximum width for each column
    max_rank_width = 3
    max_user_name_width = 20
    max_guild_name_width = 20
    max_value_width = 8

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
    for index, row in event_results.iterrows():

        value_1 = format_value(row['value_1'])
        value_2 = format_value(row['value_2'])
        value_3 = format_value(row['value_3'])
        value_4 = format_value(row['value_4'])
        value_5 = format_value(row['value_5'])
        average = format_value(row['average'])
        best = format_value(row['best'])

        row_text = f"{str(index+1).ljust(max_rank_width)}{user_names[index].ljust(max_guild_name_width)} {guild_names[index].ljust(max_guild_name_width)} {value_1.rjust(max_value_width)} {value_2.rjust(max_value_width)} {value_3.rjust(max_value_width)} {value_4.rjust(max_value_width)} {value_5.rjust(max_value_width)} {average.rjust(max_value_width)} {best.rjust(max_value_width)}"
        
        # Highlight the first num_highlight rows in green
        if index < num_highlight:
            rows.append(f"+ {row_text}")
        else:
            rows.append(f"  {row_text}")

    # Combine the header and rows into a single message
    message =  header_row + "\n" + "-" * len(header_row) + "\n" + "\n".join(rows)

    return message

    
event_choices = events_data_df.set_index('name').apply(lambda x: f"{x.name},{x.event_id}", axis=1).to_dict()



def init_results_command(bot):
    @bot.slash_command(name="results", description="Creates a private thread for the user who clicks the button in the dropdown")
    async def results_command(ctx, event_data: str = SlashOption(choices=event_choices), selected_round: str = SlashOption(choices={"First round": "1", "Second Round": "2", "Final": "f"})):
        if False:#not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message("You are not authorized to run this command.", ephemeral=True)
        else:
            event_name, event_id = event_data.split(",")
            
            competition_id = competitions[competitions["active_day"] != 0].iloc[0]["competition_id"]

            results = pd.read_csv('data/Results.tsv', dtype={'pos': int, 'value_2': 'Int64', 'value_3': 'Int64', 'value_4': 'Int64', 'value_5': 'Int64'}, sep='\t')

            event_results = results[(results['competition_id'].astype(str) == str(competition_id)) & 
                                    (results['event_id'].astype(str) == str(event_id)) & 
                                    (results['round_type'].astype(str) == str(selected_round))]

            if not event_results.empty:
                await ctx.send(f"Producing results for {event_id} round {selected_round}", ephemeral=True)
                message = await generate_results_embed(bot, event_id, event_results, competition_id, selected_round)

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
                        await ctx.channel.send(f"**{event_name} Results**")

                    await ctx.channel.send(f"```diff\n{message}```")

            else:
                await ctx.send(f"Results dont exist for {event_id} round {selected_round}", ephemeral=True)


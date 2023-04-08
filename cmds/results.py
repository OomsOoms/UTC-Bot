import pandas as pd
from nextcord import SelectOption
from nextcord.ui import Select, View
from nextcord import Embed
from nextcord.embeds import Embed
from .submit import submit

results = pd.read_csv('data/Results.tsv', sep='\t')
competitions = pd.read_csv('data/Competitions.tsv', sep='\t')


def generate_results_embed(event_name, event_results, num_highlight=5):
    
    # Define maximum width for each column
    max_rank_width = 5
    max_user_id_width = 10
    max_guild_name_width = 10
    max_average_width = 8
    max_best_width = 8
    
    # Find the widest data in each column
    for i, row in event_results.iterrows():
        max_rank_width = max(max_rank_width, len(str(i+1)))
        max_user_id_width = max(max_user_id_width, len(str(row['user_id'])))
        
        #guild = next((g for g in bot.guilds if g.id == row['guild_id']), None)
        guild_name = "Guild"#guild.name if guild else "Unknown guild"
        max_guild_name_width = max(max_guild_name_width, len(guild_name))

        max_average_width = max(max_average_width, len("{:.2f}".format(row['average'])))
        max_best_width = max(max_best_width, len("{:.2f}".format(row['best'])))
        
    # Truncate guild names and user IDs longer than their respective max width
    event_results['guild_id'] = event_results['guild_id'].apply(lambda x: x[:max_guild_name_width])
    event_results['user_id'] = event_results['user_id'].apply(lambda x: x[:max_user_id_width])
    
    # Add padding to guild names and user IDs to match their respective max width
    event_results['guild_id'] = event_results['guild_id'].apply(lambda x: x.ljust(max_guild_name_width))
    event_results['user_id'] = event_results['user_id'].apply(lambda x: x.ljust(max_user_id_width))
    
    # Define the column headers
    header_row = f"{'Rank'.ljust(max_rank_width)}  {'User ID'.ljust(max_user_id_width)}  {'Guild Name'.ljust(max_guild_name_width)}  {'Average'.ljust(max_average_width)}  {'Best'.ljust(max_best_width)}"

    # Define the rows
    rows = []
    for i, row in event_results.iterrows():
        #guild = next((g for g in bot.guilds if g.id == row['guild_id']), None)
        guild_name = "Guild"#guild.name if guild else "Unknown guild"
        row_text = f"{str(i+1).ljust(max_rank_width)}  {str(row['user_id']).ljust(max_user_id_width)}  {guild_name.ljust(max_guild_name_width)}  {'{:.2f}'.format(row['average']).ljust(max_average_width)}  {'{:.2f}'.format(row['best']).ljust(max_best_width)}"
        
        # Highlight the first num_highlight rows in green
        if i < num_highlight:
            rows.append(f"+ {row_text}")
        else:
            rows.append(f"  {row_text}")

    # Combine the header and rows into a single message
    message = header_row + "\n" + "-" * len(header_row) + "\n" + "\n".join(rows)

    message = "```diff\n" + message + "\n```"

    return message










async def dropdown_callback(interaction):
    # Stop interaction failed message

    # Get the selected option's label and value
    event_name, event_id = interaction.data['values'][0].split(",")

    competition_id = competitions.loc[competitions['active'] == 1, 'competition_id'].item()

    round_num = 1

    try:
        event_results = results[(results['competition_id'] == competition_id) & 
                                (results['event_id'].astype(str) == str(event_id)) & 
                                (results['round_num'] == round_num)]
            
        if not event_results.empty:
            embed = generate_results_embed(event_name, event_results)
            await interaction.response.send_message(embed)
        else:
            await interaction.response.send_message(f"The results for this {event_name} are not available yet", ephemeral=True)

    except IndexError:
        await interaction.response.send_message(f"The results for this {event_name} are not available yet", ephemeral=True)


async def results_dropdown(message):
    """
    Updates the given message with a dropdown view containing options
    for each event in the events_data.csv file.
    """
    # Read the events data from the CSV file
    events_data_list = pd.read_csv("data/Events.tsv", sep='\t').to_dict("list")

    if len(events_data_list["name"]) > 0:
        # Create SelectOption objects for each event
        options = [SelectOption(label=event, value=f"{event},{eventId}") for event, eventId in zip(events_data_list["name"], events_data_list["event_id"])]


        # Create a Select object with the options
        dropdown = Select(placeholder="Select an option", options=options)

        # Set the dropdown callback function to the dropdown_callback function
        dropdown.callback = dropdown_callback

        # Create a View object and add the dropdown to it
        view = View()
        view.add_item(dropdown)

        # Edit the message with the new content and view
        await message.edit(view=view)
    else:
        # If no events are found in the CSV file, remove the view from the message
        await message.edit(view=None)


def init_results(bot):
    @bot.slash_command(name="leaderboard", description="Creates a private thread for the user who clicks the button in the dropdown")
    async def leaderboard(ctx):

        # Create an Embed object with information about the competition
        embed = Embed(title="Cubing Competition Information", color=0xffa500)
        embed.add_field(name="Event Selection", value="Select an event from the dropdown menu. Note that the events will change every day for each new round, so please check the dropdown menu regularly to see what events are available.")
        embed.add_field(name="Leaderboard", value="The leaderboard shows the results of each round for the selected event. To view the leaderboard, go to the private channel named `leaderboard [event name]` and select the round you want to view. If there are no results for a particular round, it means that the round hasn't happened yet, as results are only added after the round has finished.")
        embed.add_field(name="Good Luck!", value="Have fun competing! If you have any questions, feel free to ask in the designated discussion channel.")

        # Send the embed to a channel or user
        msg = await ctx.send(embed=embed)

        # Fetch the message so I can get the ID because of a mysterious partial interaction message error 
        msg = await msg.fetch()

        # Update the message with the dropdown
        await results_dropdown(msg)

        # Write the guild ID, channel ID, message ID and the to the .tsv file
        with open('data/Messages.tsv', 'a') as file:
            file.write(f"{ctx.guild.id}\t{ctx.channel.id}\t{msg.id}\tresults_dropdown\n")
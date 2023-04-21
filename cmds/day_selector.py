from nextcord import SlashOption
import nextcord
import pandas as pd

from .event_selector import EventSelectorView

def init_day_selector(bot):
    @bot.slash_command(name="day-selector", description="Creates a private thread for the user who clicks the button in the dropdown")
    async def day_selector(ctx, day_number: int = SlashOption(choices={1:1, 2:2, 3:3, 4:4, 5:5, 6:6})):

        # Read the competitions file
        competitions = pd.read_csv('data/Competitions.tsv', sep='\t')

        # Find the competition with the active day
        active_competition = competitions.loc[competitions["active_day"] != 0, "competition_id"].iloc[0]

        # Update the active competition based on user's selection
        competitions.loc[competitions["competition_id"] == active_competition, "active_day"] = day_number
        competitions.to_csv("data/Competitions.tsv", sep='\t', index=False)

        # Send a response message
        await ctx.send(f"Active day has been changed to {day_number}", ephemeral=True)

        #messages = pd.read_csv('data/Messages.tsv', sep='\t')
        #for index, row in messages.iterrows():
        #    channel = bot.get_channel(int(row["channel_id"]))
        #    message = await channel.fetch_message(int(row["message_id"]))
#
        #    # Get the select menu component
        #    select_menu = message.components[0].components[0]
#
        #    # Change the options
        #    new_options = [nextcord.SelectOption(label="Option 1", value="option1"), nextcord.SelectOption(label="Option 2", value="option2")]
        #    select_menu.options = new_options
#
        #    # Update the message
        #    await message.edit(components=[nextcord.ActionRow(select_menu)])



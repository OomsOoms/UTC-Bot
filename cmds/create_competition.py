import sqlite3
import pickle
import nextcord
from datetime import datetime


class Competition:

    def __init__(self, competition_name):

        self.competition_name = competition_name

        self.competitors = [] # List of competitor objects specific to each competition

        self.settings = {"host_users":[], "round_length":0, "live_results":False, "video_evidence":False, "start_date":0, "guilds":[]}

    def write(self):
        # Store the serialized data in the database
        with sqlite3.connect('data/utc_cubing_database.db') as conn:
            cursor = conn.cursor()

            # Get unique ID
            cursor.execute("SELECT COUNT(*) FROM competitions")
            row_count = cursor.fetchone()[0]
            number = str(row_count).zfill(3)

            # Standardise names into PascalCase
            words = [word.capitalize() for word in self.competition_name.lower().split()]
            id = ''.join(words)

            # Get the date in format mmyy
            current_date = datetime.now()
            year = current_date.year
            month = current_date.month

            # Create competition ID
            self.competition_id = f"{id}{month:02d}{str(year)[-2:]}{number}"

            # Insert the serialized object into the database
            serialized_data = pickle.dumps(self)
            cursor.execute("INSERT INTO competitions (competition_id, serialized_data) VALUES (?, ?)", (self.competition_id, serialized_data))
            conn.commit()


class CompetitionOrganiser(nextcord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


    @nextcord.ui.button(
        label="Hosts", style=nextcord.ButtonStyle.primary, custom_id="ResultSelectorView:hosts"
    )
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.send("pressed", ephemeral=True)


    @nextcord.ui.button(
        label="Round length", style=nextcord.ButtonStyle.primary, custom_id="ResultSelectorView:round_length"
    )
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.send("pressed", ephemeral=True)


    @nextcord.ui.button(
        label="Live results", style=nextcord.ButtonStyle.primary, custom_id="ResultSelectorView:live_results"
    )
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.send("pressed", ephemeral=True)

        
def init_competition_organiser(bot):
    @bot.slash_command(name="organise-competition", description="Create a competition")
    async def organise_competition(ctx):
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message("You are not authorized to run this command.", ephemeral=True)
        else:
            await ctx.send("test", view=CompetitionOrganiser())

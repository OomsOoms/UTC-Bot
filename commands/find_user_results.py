import nextcord

from utils.database import conn

def find_results(bot):
    @bot.user_command(name="Find user results")
    async def find_results_context_menu(interaction, member: nextcord.member):

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM results WHERE user_id = ? AND guild_id = ?", (interaction.user.id, interaction.guild.id))

        results = cursor.fetchone()

        cursor.close()

        if results:
            await interaction.response.send_message(results, ephemeral=True)
        else:
            await interaction.response.send_message("results NOT found", ephemeral=True)
            
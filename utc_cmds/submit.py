from nextcord.ui.view import View
import nextcord
import sqlite3

conn = sqlite3.connect('data/utc_database.db')

class SubmitModal(nextcord.ui.Modal):

    def __init__(self):
        super().__init__("Solve X")

        self.competition_id = nextcord.ui.TextInput(label="Time", min_length=4, max_length=10, required=True, placeholder="mm:ss")
        self.add_item(self.competition_id)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        await interaction.response.defer()

        submitted_button = nextcord.ui.Button(label="Submitted", style=nextcord.ButtonStyle.primary, disabled=True)
        view = View()
        view.add_item(submitted_button)

        await interaction.message.edit(view=view)

        await submit(interaction.channel)


class SubmitButton(nextcord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label="Submit", style=nextcord.ButtonStyle.primary, custom_id="ResultSelectorView:submit"
    )
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(SubmitModal())


async def submit(thread):

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM threads WHERE thread_id = ?", (thread.id,))
    user_event = cursor.fetchone()

    query = """
    SELECT formats.solve_count
    FROM threads
    JOIN events ON threads.event_id = events.event_id
    JOIN formats ON events.average_id = formats.average_id
    WHERE threads.competition_id = ? AND threads.user_id = ?
    """

    cursor.execute(query, (user_event[1] , user_event[3])) # competition_id, user_id

    solve_count = cursor.fetchone()[0]

    if not solve_count <= user_event[5]: # solve_num
        cursor.execute("UPDATE threads SET solve_num = solve_num + 1 WHERE thread_id = ?", (thread.id,))

        await thread.send("Scramble", view=SubmitButton())

        conn.commit()

    cursor.close()
    

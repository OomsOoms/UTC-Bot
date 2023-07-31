from nextcord.ui.view import View
import nextcord
import re

from utils.database import execute_query


def parse_time(time_str):
    # Regex match groups: ([minutes:])[seconds][milliseconds]
    match = re.fullmatch(r'^(\d{1,2}:)?(\d{1,2})?(\.\d{0,2})?$', time_str)
    if match:
        minutes_string = match.group(1) or "0:"  
        seconds_string = match.group(2) or "0"  
        milliseconds_string = match.group(3) or ".00"  
        
        minutes, seconds = list(map(int, (minutes_string[:-1] + ":" + seconds_string).split(":")))
        milliseconds = milliseconds_string[1:].ljust(2, '0')

        final_time = f"{minutes*60+seconds}{milliseconds}"

        return final_time
    else:
        return
    

class SubmitModal(nextcord.ui.Modal):

    def __init__(self, thead_id):
        self.solve_num = execute_query("SELECT_solve_num", (thead_id,)).fetchone()[0]
        super().__init__(f"Solve {self.solve_num}")

        self.solve_time = nextcord.ui.TextInput(label="Time", min_length=3, max_length=8, required=True, placeholder="mm:ss")
        self.add_item(self.solve_time)
        

    async def callback(self, interaction: nextcord.Interaction) -> None:
        time = parse_time(self.solve_time.value)

        if time:
            await interaction.response.defer()
            
            execute_query("UPDATE_threads_value", (time, interaction.channel.id), f"value_{self.solve_num}")

            submitted_button = nextcord.ui.Button(label="Submitted", style=nextcord.ButtonStyle.primary, disabled=True)
            view = View()
            view.add_item(submitted_button)

            
            await interaction.message.edit(view=view)
            await submit(interaction.channel)

        else:
            await interaction.response.send_message("Invalid format", ephemeral=True)


class SubmitSolveButton(nextcord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label="Submit", style=nextcord.ButtonStyle.primary, custom_id="SubmitSolveButton:submit"
    )
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(SubmitModal(interaction.channel.id))

class SubmitAverageButton(nextcord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label="Submit", style=nextcord.ButtonStyle.success, custom_id="SubmitAverageButton:submit"
    )
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        times_list = execute_query("SELECT_thread_values", (interaction.channel.id,)).fetchone()
        competition_id, event_id, round_type, value_1, value_2, value_3, value_4, value_5 = execute_query("SELECT_thread_data", (interaction.channel.id,)).fetchone()
        solve_count, trim_average_num = execute_query("SELECT_solve_count_trim", (competition_id, interaction.user.id)).fetchone()
        times_list = [value for value in times_list if value is not None] # Remove any None values if the average contains less than 5 values
        trimmed_times = sorted(times_list)[:len(times_list)-trim_average_num][trim_average_num:]
        average = str(round(sum(trimmed_times)/len(trimmed_times)))
        execute_query("INSERT_result", (competition_id, event_id, interaction.user.id, interaction.guild.id, "average_id", round_type, average, value_1, value_2, value_3, value_4, value_5))

        view = View()
        submitted_button = nextcord.ui.Button(label="Submitted", style=nextcord.ButtonStyle.success, disabled=True)
        submitted_button = nextcord.ui.Button(label="Request assistance", style=nextcord.ButtonStyle.primary, disabled=True)
        view.add_item(submitted_button)

        await interaction.message.edit(view=view)
        await interaction.channel.send("**You can now leave this thread**")

        execute_query("DELETE_thread_data", (interaction.channel.id,))


    @nextcord.ui.button(
        label="Request assistance", style=nextcord.ButtonStyle.primary, custom_id="RequestAssistanceButton:request", disabled=True
    )
    async def request_assistance(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        pass
    

async def submit(thread):
    competition_id, event_id, user_id, round_type, solve_num = execute_query("SELECT_thread_info", (thread.id,)).fetchone()
    solve_count, trim_average_num = execute_query("SELECT_solve_count_trim", (competition_id, user_id)).fetchone()

    if not solve_count <= solve_num: # solve_num
        execute_query("UPDATE_thread_solve_num", (thread.id,))
        scramble = execute_query("SELECT_scramble", (competition_id, event_id, solve_num+1, round_type)).fetchone()

        if not scramble:
            scramble = ["`An error occurred and no scramble was found`"]
        
        await thread.send(f"_ _\n{scramble[0]}", view=SubmitSolveButton())

    else:
        times_list = execute_query("SELECT_thread_values", (thread.id,)).fetchone()

        times_list = [value for value in times_list if value is not None] # Remove any None values if the average contains less than 5 values
        trimmed_times = sorted(times_list)[:len(times_list)-trim_average_num][trim_average_num:]
        average = str(round(sum(trimmed_times)/len(trimmed_times)))
        
        formatted_times = ["{:.2f}".format(time / 100) for time in times_list]
        fastest_indices = sorted(range(len(formatted_times)), key=lambda i: float(formatted_times[i]))[:trim_average_num]
        slowest_indices = sorted(range(len(formatted_times)), key=lambda i: float(formatted_times[i]), reverse=True)[:trim_average_num]

        for index in fastest_indices + slowest_indices:
            formatted_times[index] = f"({formatted_times[index]})"

        result_string = " ".join(formatted_times)

        embed = nextcord.Embed(title=f"Your {event_id} Results", color=0xffa500)
        embed.add_field(name="Average", value=average, inline=False)
        embed.add_field(name="Times", value=result_string, inline=False)

        await thread.send(embed=embed, view=SubmitAverageButton())

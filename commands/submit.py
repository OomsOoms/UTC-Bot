from nextcord.ui.view import View
import nextcord
import re
import os
import requests

from utils.database import execute_query

# TODO: Need to remove and None values, need to check the average type before formatting, for events like fmc and mbld, same goes for the submit code where the format should be checked plus anything with a leading 0 gets removed, for example: 6 => 0.06 instead its doing 0.6
# TODO: As this is used in multiple files it should be on its own file, possibly in utils
def format_time(input_time): 
    input_str = str(input_time)
    if input_time < 100:
        return '0.' + input_str
    elif input_time < 6000:
        return input_str[:-2] + '.' + input_str[-2:]
    else:
        minutes = input_time // 6000
        remaining = input_time % 6000
        seconds = remaining // 100
        milliseconds = remaining % 100
        return f"{minutes}:{str(seconds).zfill(2)}.{str(milliseconds).zfill(2)}"


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
        request_assistance_button = nextcord.ui.Button(label="Request assistance", style=nextcord.ButtonStyle.primary, disabled=True)
        view.add_item(submitted_button)
        view.add_item(request_assistance_button)

        await interaction.message.edit(view=view)

        execute_query("DELETE_thread_data", (interaction.channel.id,))

        # use requests and ani API endpoint to remove the user cuz idk how else to do this
        
        # Construct the API endpoint URL
        api_url = f"https://discord.com/api/v9/channels/{interaction.channel.id}/thread-members/{interaction.user.id}"

        # Set the headers including the Authorization token
        headers = {"Authorization": f"Bot {os.getenv('BOT_TOKEN')}"}

        # Send a DELETE request to remove the user from the thread
        requests.delete(api_url, headers=headers)

    @nextcord.ui.button(
        label="Request assistance", style=nextcord.ButtonStyle.primary, custom_id="RequestAssistanceButton:request", disabled=True
    )
    async def request_assistance(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        pass # TODO: Make this send a message with a channel link to a mod channel

# TODO: If the video evidence is true for the event add info for that
async def submit(thread):
    competition_id, event_id, user_id, round_type, solve_num = execute_query("SELECT_thread_info", (thread.id,)).fetchone()
    solve_count, trim_average_num = execute_query("SELECT_solve_count_trim", (competition_id, user_id)).fetchone()

    if not solve_count <= solve_num:
        execute_query("UPDATE_thread_solve_num", (thread.id,))
        scramble = execute_query("SELECT_scramble", (competition_id, event_id, solve_num+1, round_type)).fetchone()

        if not scramble:
            scramble = ["`An error occurred and no scramble was found`"]
        
        await thread.send(f"_ _\n{scramble[0]}", view=SubmitSolveButton())

    else:
        times_list = execute_query("SELECT_thread_values", (thread.id,)).fetchone()

        times_list = [value for value in times_list if value is not None] # Remove any None values if the average contains less than 5 values
        trimmed_times = sorted(times_list)[:len(times_list)-trim_average_num][trim_average_num:]
        average = round(sum(trimmed_times)/len(trimmed_times))
        
        formatted_times = [format_time(time) for time in times_list]
        fastest_indices = sorted(range(len(times_list)), key=lambda i: float(times_list[i]))[:trim_average_num]
        slowest_indices = sorted(range(len(times_list)), key=lambda i: float(times_list[i]), reverse=True)[:trim_average_num]

        for index in fastest_indices + slowest_indices:
            formatted_times[index] = f"({formatted_times[index]})"

        result_string = " ".join(formatted_times)

        event_name = execute_query("SELECT_event_name", (event_id,)).fetchone()[0]

        embed = nextcord.Embed(title=f"Your {event_name} Results", color=0xffa500)
        embed.add_field(name="Average", value=format_time(average), inline=False)
        embed.add_field(name="Times", value=result_string, inline=False)

        await thread.send(embed=embed, view=SubmitAverageButton())

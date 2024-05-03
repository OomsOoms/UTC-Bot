from nextcord.ui.view import View
import nextcord

import os
#import requests

#from database.execute_query import execute
#from utils.format_times import parse_time, format_time
execute = 1

format_time = lambda x: x
parse_time = lambda x: x
requests = 1

async def submit(thread): # TODO: Needs to change lots of things depending on the event, so solve count etc
    competition_id, event_id, round_type, solve_num = execute("select thread info", (thread.id,))[0]
    solve_count, trim_n = execute("select format", (event_id,))[0]

    if solve_count >= solve_num:
        scramble = execute("select scramble", (competition_id, event_id, solve_num, round_type))[0]
        await thread.send(f"**Solve {solve_num}**\n\n{scramble[0]}", view=SubmitSolveButton())
    else:
        times_list = [value for value in execute("select thread values", (thread.id,))[0] if value is not None]
        trimmed_times = sorted(times_list)[trim_n:-trim_n]
        average = round(sum(trimmed_times) / len(trimmed_times))
        
        min_time_index = times_list.index(min(times_list))
        max_time_index = times_list.index(max(times_list))

        formatted_times = [f"({format_time(time)})" if i == min_time_index or i == max_time_index else format_time(time) for i, time in enumerate(times_list)]
        event_name = execute("select event name", (event_id,))[0][0]

        embed = nextcord.Embed(title=f"Your {event_name} Results", color=0xffa500)
        embed.add_field(name="Average", value=format_time(average), inline=False)
        embed.add_field(name="Times", value=" ".join(formatted_times), inline=False)

        await thread.send(embed=embed, view=SubmitAverageButton())
        

class SubmitSolveButton(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="Submit", style=nextcord.ButtonStyle.primary, custom_id="SubmitSolveButton:submit")
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(SubmitTimeModal(interaction.channel.id))
        
class SubmitTimeModal(nextcord.ui.Modal):
    def __init__(self, thread_id):
        self.solve_num = execute("select solve num", (thread_id,))[0][0]
        super().__init__(f"Solve {self.solve_num}")

        self.solve_time = nextcord.ui.TextInput(label="Time", min_length=3, max_length=8, required=True, placeholder="mm:ss")
        self.add_item(self.solve_time)
        
    async def callback(self, interaction: nextcord.Interaction) -> None:
        time = parse_time(self.solve_time.value)

        if time:
            await interaction.response.defer()

            values_tuple = execute("select thread values", (interaction.channel.id,))[0]
            index = values_tuple.index(None)
            new_tuple = values_tuple[:index] + (time,) + values_tuple[index + 1:] + (interaction.channel.id,)
            execute("update thread", new_tuple)

            view = View()
            submitted_button = nextcord.ui.Button(label="Submitted", style=nextcord.ButtonStyle.primary, disabled=True)
            view.add_item(submitted_button)

            await interaction.message.edit(view=view)
            await submit(interaction.channel)
        else:
            await interaction.response.send_message("Invalid format", ephemeral=True)


async def save_average(interaction, video=None):
        await interaction.response.defer()
        times_list = execute("select thread values", (interaction.channel.id,))[0]
        times_list = [value for value in times_list if value is not None]

        competition_id, event_id, round_type = execute("select thread data", (interaction.channel.id,))[0]
        solve_count, trim_n = execute("select format", (event_id,))[0]
        
        trimmed_times = sorted(times_list)[:len(times_list)-trim_n][trim_n:]
        average = str(round(sum(trimmed_times)/len(trimmed_times)))
        execute("insert result", (competition_id, event_id, interaction.user.id, interaction.guild.id, round_type, average) + tuple(times_list) + (video,))
        execute("delete thread record", (interaction.channel.id,))

        view = View()
        submitted_button = nextcord.ui.Button(label="Submitted", style=nextcord.ButtonStyle.success, disabled=True)
        submitted_button2 = nextcord.ui.Button(label="Submitted", style=nextcord.ButtonStyle.success, disabled=True)
        view.add_item(submitted_button)
        view.add_item(submitted_button2)
        await interaction.message.edit(view=view)
        
        api_url = f"https://discord.com/api/v9/channels/{interaction.channel.id}/thread-members/{interaction.user.id}"
        headers = {"Authorization": f"Bot {os.getenv('BOT_TOKEN')}"}
        requests.delete(api_url, headers=headers)

class SubmitVideoModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(f"Submit with video evidence")

        self.link = nextcord.ui.TextInput(label="Link to video evidence", min_length=8, max_length=128, required=True, placeholder="https://example.com or WCA ID")
        self.add_item(self.link)
        
    async def callback(self, interaction: nextcord.Interaction) -> None:
        await save_average(interaction, self.link.value)

class SubmitAverageButton(nextcord.ui.View): # TODO: Make the submit video options only show if the event requires evidence
    def __init__(self):
        super().__init__(timeout=None)
    
    @nextcord.ui.button(label="Submit", style=nextcord.ButtonStyle.success, custom_id="SubmitAverageButton:submit")
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await save_average(interaction)

    @nextcord.ui.button(label="Submit with Video", style=nextcord.ButtonStyle.success, custom_id="SubmitAverageButton:submit_video")
    async def submit_video(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(SubmitVideoModal())


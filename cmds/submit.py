import nextcord
from nextcord.ui.view import View

async def confirm_callback(interaction: nextcord.Interaction):
    # create "Cancel" and "Event Added" buttons, both disabled
    await interaction.send("Pressed")

async def plus_two_callback(interaction: nextcord.Interaction):
    # create "Cancel" and "Event Added" buttons, both disabled
    await interaction.send("Pressed")

async def dnf_callback(interaction: nextcord.Interaction):
    # create "Cancel" and "Event Added" buttons, both disabled
    await interaction.send("Pressed")

async def update_button(message):

    # create "Cancel" and "Confirm" buttons
    confirml_button = nextcord.ui.Button(label="OK", style=nextcord.ButtonStyle.green)
    confirml_button.callback = confirm_callback

    # create "Cancel" and "Confirm" buttons
    plus_two_button = nextcord.ui.Button(label="+2", style=nextcord.ButtonStyle.grey)
    plus_two_button.callback = plus_two_callback
        
    # create "Cancel" and "Confirm" buttons
    dnf_button = nextcord.ui.Button(label="DNF", style=nextcord.ButtonStyle.red)
    dnf_button.callback = dnf_callback

    # add buttons to a view
    view = View()
    view.add_item(confirml_button)
    view.add_item(plus_two_button)
    view.add_item(dnf_button)

    await message.edit(view=view)

async def submit(ctx, thread):

    await thread.send("an image of the scramble")
    
    msg = await thread.send("L' R2 U2 L2 D' L2 D' B2 D' R2 B2 L2 D' B' L2 U R2 U F R")

    #msg = await msg.fetch()

    await update_button(msg)

    # Write the guild ID, channel ID, and message ID to the file
    with open('message_ids.txt', 'a') as file:
        file.write(f"{ctx.guild.id},{thread.id},{msg.id},update_button\n")


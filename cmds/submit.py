import nextcord
from nextcord.ui.view import View
import asyncio
import csv





class EmbedModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("<Event name> - <Round type>")
        
        # create TextInput for Scramble1
        self.Scramble1 = nextcord.ui.TextInput(label="<Scramble1>", min_length=2, max_length=128, required=True, placeholder="mm:ss.ms")
        self.add_item(self.Scramble1)
        
        # create TextInput for Scramble2
        self.Scramble2 = nextcord.ui.TextInput(label="<Scramble2>", min_length=2, max_length=128, required=True, placeholder="mm:ss.ms")
        self.add_item(self.Scramble2)
        
        # create TextInput for Scramble3
        self.Scramble3 = nextcord.ui.TextInput(label="<Scramble3>", min_length=2, max_length=128, required=True, placeholder="mm:ss.ms")
        self.add_item(self.Scramble3)
        
        # create TextInput for Scramble4
        self.Scramble4 = nextcord.ui.TextInput(label="<Scramble4>", min_length=2, max_length=128, required=True, placeholder="mm:ss.ms")
        self.add_item(self.Scramble4)
        
        # create TextInput for Scramble5
        self.Scramble5 = nextcord.ui.TextInput(label="<Scramble5>", min_length=2, max_length=128, required=True, placeholder="mm:ss.ms")
        self.add_item(self.Scramble5)
    
    async def on_interaction_init(self, interaction: nextcord.Interaction) -> None:
        # set the description attribute of the Embed
        self.embed.description = "Please enter the scrambles for the event below:"
        await super().on_interaction_init(interaction)




    async def callback(self, interaction: nextcord.Interaction) -> None:
        # get event title and scrambles list from user input
        desc = str(self.emTitle.value)
        scrambles = str(self.emScram.value).split(",")

        # format the scrambles list in the description
        for i, x in enumerate(scrambles):
            desc += f"\n**Scramble {i}**\n{x}"

        # create embed with the event details
        em = nextcord.Embed(title="Confirm new event", description=desc)

        # create "Cancel" and "Confirm" buttons
        cancel_button = nextcord.ui.Button(label="Cancel", style=nextcord.ButtonStyle.red, custom_id="cancel_button")
        cancel_button.callback = self.cancel_callback

        confirm_button = nextcord.ui.Button(label="Confirm", style=nextcord.ButtonStyle.green, custom_id="confirm_button", disabled=False)
        confirm_button.callback = self.confirm_callback

        # add buttons to a view
        view = View()
        view.add_item(cancel_button)
        view.add_item(confirm_button)

        # send the embed with the view and buttons to the user
        await interaction.response.send_message(embed=em, view=view)

    async def confirm_callback(self, interaction: nextcord.Interaction) -> None:
        # create "Cancel" and "Event Added" buttons, both disabled
        cancel_button = nextcord.ui.Button(label="Cancel", style=nextcord.ButtonStyle.danger, custom_id="cancel_button", disabled=True)
        confirm_button = nextcord.ui.Button(label="Event Added", style=nextcord.ButtonStyle.success, custom_id="confirm_button", disabled=True)

        # add buttons to a view
        view = nextcord.ui.View()
        view.add_item(cancel_button)
        view.add_item(confirm_button)

        # edit the message with the view and buttons to show that the event was added
        message = interaction.message
        
        await message.edit(view=view) # type: ignore

        # write the new event data to the CSV file
        with open("events_data.csv", "a", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Place holder", "Place holder", "Place holder"])

        #await fix_interactions(bot)

    async def cancel_callback(self, interaction: nextcord.Interaction) -> None:
        # create "Cancelling" and "Confirm" buttons, both disabled
        cancel_button = nextcord.ui.Button(label="Cancelling", style=nextcord.ButtonStyle.danger, custom_id="cancel_button", disabled=True)
        confirm_button = nextcord.ui.Button(label="Confirm", style=nextcord.ButtonStyle.success, custom_id="confirm_button", disabled=True)

        # add buttons to a view
        view = nextcord.ui.View()
        view.add_item(cancel_button)
        view.add_item(confirm_button)

        # edit the message with the view and buttons to show that the cancellation was successful
        message = interaction.message
        await interaction.response.defer()
        await message.edit(view=view) # type: ignore

        # wait 2 seconds
        await asyncio.sleep(2)
        await interaction.message.delete() # type: ignore


async def submit(interaction, event_name, event_id):
    # display the modal dialog to the user
    await interaction.response.send_modal(EmbedModal())

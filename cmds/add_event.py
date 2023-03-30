import nextcord
from nextcord.ui.view import View
import asyncio

def init_add_event(bot):

    class EmbedModal(nextcord.ui.Modal):
        def __init__(self):
            super().__init__(
                "Embed Maker",
            )

            # create TextInput for event title
            self.emTitle = nextcord.ui.TextInput(label="Add new event", min_length=2, max_length=128, required=True, placeholder="Event name")
            self.add_item(self.emTitle)

            # create TextInput for scrambles list
            self.emScram = nextcord.ui.TextInput(label="Srcambles list", min_length=5, max_length=4000, required=True, placeholder="Separate each scramble with a `,`", style=nextcord.TextInputStyle.paragraph)
            self.add_item(self.emScram)

        async def callback(self, interaction: nextcord.Interaction) -> None:
            # get event title and scrambles list from user input
            desc = self.emTitle.value
            scrambles = self.emScram.value.split(",")

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
            confirm_button.disabled = False

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
            await interaction.response.defer()
            await message.edit(view=view)

            # add the data to the events_data.csv file 

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
            await message.edit(view=view)

            # wait 2 seconds
            await asyncio.sleep(2)
            await interaction.message.delete()
    
    # register the slash command with the bot
    @bot.slash_command(name="add_event", description="Modal", guild_ids=[988085977719402536])
    async def add_event(ctx):
        # display the modal dialog to the user
        await ctx.response.send_modal(EmbedModal())

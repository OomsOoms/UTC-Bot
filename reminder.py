import requests

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
BOT_TOKEN = 'BOT_TOKEN'

# Replace 'CHANNEL_ID' with the desired channel ID
CHANNEL_ID = 'CHANNEL_ID'

# Replace 'USER_ID' with the user's ID
USER_ID = 'USER_ID'

# URL to send a message in a channel
url = f'https://discord.com/api/v10/channels/{CHANNEL_ID}/messages'

# Headers with authorization
headers = {
    'Authorization': f'Bot {BOT_TOKEN}',
    'Content-Type': 'application/json',
}

# Message content
message_content = (
    f'Hey <@{USER_ID}>, you made this thread a while ago. '
    'Just a friendly reminder: **don\'t forget to compete!**'
)

# Data for the POST request
data = {
    'content': message_content
}

# Make the POST request
response = requests.post(url, json=data, headers=headers)

# Check the response
if response.status_code == 200:
    print('Message sent successfully')
else:
    print('Error sending message:', response.status_code, response.text)

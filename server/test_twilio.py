from twilio.rest import Client
import os
from pathlib import Path

# Clear any existing env variables first
os.environ.pop('TWILIO_ACCOUNT_SID', None)
os.environ.pop('TWILIO_AUTH_TOKEN', None)
os.environ.pop('TWILIO_PHONE_NUMBER', None)

# Get absolute path to .env file
# env_path = Path.home() / "Documents" / "Projects" / "mqueue" / ".env"
# ... existing code ...
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
print(f"Looking for .env file at: {env_path}")

# Load the values directly
with open(env_path, 'r') as f:
    for line in f:
        if '=' in line:
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

# Get credentials from environment
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_number = os.getenv('TWILIO_PHONE_NUMBER')

print("\nValues loaded:")
print(f"TWILIO_ACCOUNT_SID: {account_sid}")
print(f"TWILIO_AUTH_TOKEN: {auth_token}")
print(f"TWILIO_PHONE_NUMBER: {twilio_number}")

# Initialize Twilio client and try to send a message
try:
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body='rahhhhhhhhh.',
        from_=twilio_number,
        to='+18777804236'  # Your verified number
    )
    print(f"\nSuccess! Message sent with SID: {message.sid}")
except Exception as e:
    print(f"\nError: {e}")
from dataclasses import Field
from wsgiref.validate import validator
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from twilio.rest import Client
from dotenv import load_dotenv
import os
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv()

# Get Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Debug logging
print("Twilio Configuration:")
print(f"Account SID exists: {bool(TWILIO_ACCOUNT_SID)}")
print(f"Auth Token exists: {bool(TWILIO_AUTH_TOKEN)}")
print(f"Phone Number: {TWILIO_PHONE_NUMBER}")

# Initialize router and state
router = APIRouter(prefix="/api/v1")
queue = []
curr_players = []


from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, validator, constr
from typing import Optional
import re
# ... other imports remain the same ...

class Player(BaseModel):
    name: str
    phoneNumber: str

    @validator('phoneNumber')
    def validate_phone(cls, value):
        """Validate phone number format"""
        # Remove any non-digit characters
        phone_num = re.sub(r'\D', '', value)
        
        # Add country code if needed
        if not value.startswith('+'):
            phone_num = '1' + phone_num if not phone_num.startswith('1') else phone_num
            phone_num = '+' + phone_num

        # Validate length
        if len(re.sub(r'\D', '', phone_num)) != 11:
            raise ValueError('Phone number must be 10 digits (excluding country code)')

        # Validate format
        if not re.match(r'^\+1[2-9]\d{2}[2-9]\d{2}\d{4}$', phone_num):
            raise ValueError('Invalid phone number format')

        return phone_num

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "phoneNumber": "+11234567890"
            }
        }


def get_twilio_client():
    """Get or create Twilio client"""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN]):
        print("Warning: Missing Twilio credentials")
        return None
    try:
        return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    except Exception as e:
        print(f"Error initializing Twilio client: {e}")
        return None

async def send_sms(to_number: str, message: str):
    """Send SMS using Twilio"""
    try:
        # Get Twilio client
        twilio_client = get_twilio_client()
        if not twilio_client:
            print("Warning: Could not initialize Twilio client")
            return

        # Format phone number
        if not to_number.startswith('+'):
            to_number = f'+1{to_number}'

        # Send SMS in thread pool
        def send():
            return twilio_client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=to_number
            )

        with ThreadPoolExecutor() as executor:
            await asyncio.get_event_loop().run_in_executor(executor, send)
            
        print(f"SMS sent successfully to {to_number}")
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")

@router.get("/queue")
async def get_queue():
    """Get all players in queue"""
    return queue

@router.post("/queue")
async def add_to_queue(player: Player):
    """Add a player to the queue"""
    try:
        if any(p["phoneNumber"] == player.phoneNumber for p in queue):
            raise HTTPException(
                status_code=400,
                detail="This phone number is already in the queue"
            )

        if any(p["phoneNumber"] == player.phoneNumber for p in curr_players):
            raise HTTPException(
                status_code=400,
                detail="This phone number is already playing"
            )
        
        print(f"Adding player: {player.name} ({player.phoneNumber})")
        queue.append({"name": player.name, "phoneNumber": player.phoneNumber})
        position = len(queue)

        # Send SMS notification
        await send_sms(
            player.phoneNumber,
            f"Hi {player.name}! You are number {position} in the queue."
        )

        await remove_player()
        return {"message": "Player added successfully", "position": position}
    except Exception as e:
        print(f"Error adding player: {str(e)}")
        return {"error": str(e)}

@router.get("/players")
async def get_curr_players():
    """Get current players"""
    return curr_players

@router.post("/stop")
async def handle_sms_webhook(request: Request):
    """Handle SMS webhook for stopping the game"""
    try:
        form_data = await request.form()
        message_body = form_data.get("Body", "").strip().upper()
        from_number = form_data.get("From", "")

        if message_body == "STOP":
            curr_players.clear()
            await remove_player()
            return {"message": "Game ended, next players notified"}
        
        return {"message": "Message received"}
    except Exception as e:
        print(f"Error in webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def remove_player():
    """Remove players and notify next group"""
    print(f"curr_players: {curr_players}")
    print(f"queue: {queue}")

    if len(curr_players) == 0 and len(queue) >= 4:
        try:
            for _ in range(4):
                player = queue[0]
                await send_sms(
                    player["phoneNumber"],
                    f"Hi {player['name']}! Your court is ready! Please proceed to the courts."
                )
                curr_players.append(queue.pop(0))
            return {"message": "Players moved to current players"}
        except Exception as e:
            print(f"Error moving players: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    return {"message": "No players to move"}

# Optional: Add test endpoint
@router.get("/test-sms")
async def test_sms():
    """Test endpoint for SMS sending"""
    try:
        await send_sms(
            "+1234567890",  # Replace with your test number
            "Test message from FastAPI"
        )
        return {"message": "Test SMS sent"}
    except Exception as e:
        return {"error": str(e)}
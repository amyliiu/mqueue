from dataclasses import Field
from wsgiref.validate import validator
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from twilio.rest import Client
from dotenv import load_dotenv
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

print("Twilio Configuration:")
print(f"Account SID exists: {bool(TWILIO_ACCOUNT_SID)}")
print(f"Auth Token exists: {bool(TWILIO_AUTH_TOKEN)}")
print(f"Phone Number: {TWILIO_PHONE_NUMBER}")

router = APIRouter(prefix="/api/v1")
queue = []
curr_players = []

class Player(BaseModel):
    name: str
    phoneNumber: str

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
        print(f"Adding player: {player.name} ({player.phoneNumber})")
        queue.append({"name": player.name, "phoneNumber": player.phoneNumber})
        position = len(queue)

        await send_sms(
            player.phoneNumber,
            f"Hi {player.name}! You are number {position} in the queue. {player.phoneNumber}."
        )

        await remove_player()
        return {"message": "Player added successfully", "position": position}
    except Exception as e:
        print(f"Error adding player: {str(e)}")
        return {"error": str(e)}

@router.get("/players")
async def get_curr_players():
    return curr_players

@router.post("/done")
async def handle_sms_webhook(request: Request):
    """Handle SMS webhook for responding to messages"""
    form_data = await request.form()
    message_body = form_data.get("Body", "").strip().upper()
    from_number = form_data.get("From", "")

    # Create a Twilio MessagingResponse object
    response = MessagingResponse()

    # Respond based on the message content
    if message_body == "DONE":
        response.message("Thank you!")
    else:
        response.message("Sorry, I didn't understand that. Please send 'DONE' to proceed.")

    # Return the TwiML response
    return Response(content=str(response), media_type="text/xml")

async def remove_player():
    print(f"curr_players: {curr_players}")
    print(f"queue: {queue}")

    if len(curr_players) == 0 and len(queue) >= 4:
        try:
            for _ in range(4):
                player = queue[0]
                await send_sms(
                    player["phoneNumber"],
                    f"Hi {player['name']}, your court is ready! Please proceed to the courts. Remember to text ''DONE'' to end your game."
                )
                curr_players.append(queue.pop(0))
            return {"message": "Players moved to current players"}
        except Exception as e:
            print(f"Error moving players: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    return {"message": "No players to move"}

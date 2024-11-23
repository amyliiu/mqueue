from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Body, Request
from pydantic import BaseModel
from twilio.rest import Client
from dotenv import load_dotenv
import os
import asyncio
from pathlib import Path

load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

router = APIRouter(prefix="/api/v1")  

queue = []
curr_players = []

class Player(BaseModel):
    name: str
    phoneNumber: str

async def send_sms(to_number: str, message: str):
    """Send SMS using Twilio in an async-safe way"""
    if not client:
        print("Warning: Twilio client not initialized - SMS will not be sent")
        return
    try:
        # Format phone number if it doesn't start with +
        if not to_number.startswith('+'):
            to_number = f'+1{to_number}'  # Assuming US numbers

        with ThreadPoolExecutor() as executor:
            await asyncio.get_event_loop().run_in_executor(
                executor,
                lambda: client.messages.create(
                    body=message,
                    from_=TWILIO_PHONE_NUMBER,
                    to=to_number
                )
            )
        print(f"SMS sent successfully to {to_number}")
    except Exception as e:
        print(f"Error sending SMS to {to_number}: {str(e)}")
        raise

@router.post("/queue") 
async def add_to_queue(player: Player):
    try:
        queue.append({"name": player.name, "phoneNumber": player.phoneNumber})
        position = len(queue)

        await send_sms(
            player.phoneNumber,
            f"Hi {player.name}! You are number {position} in the queue."
        )
        await remove_player()
        return {"message": "Player added successfully"}
    except Exception as e:
            print(f"Error adding player to queue: {str(e)}")
            return {"error": str(e)}, 500

@router.get("/queue")
async def get_queue():
    return queue

@router.get("/players") 
async def get_curr_players():
    return curr_players

@router.post("/stop")
async def handle_sms_webhook(request: Request):
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
        return {"error": str(e)}, 500


async def remove_player():
    print(f"curr_players: {curr_players}")
    print(f"queue: {queue}")

    if len(curr_players) == 0 and len(queue) >= 4:
        for i in range(4):
            player = queue[0]
            await send_sms(
                player["phoneNumber"],
                f"Hi {player['name']}! Your court is ready! Please proceed to the courts."
            )
            curr_players.append(queue.pop(0))
        return {"message": "Players moved to current players"}
    return {"message": "No players to move"}


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
PORT = os.getenv('PORT')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

router = APIRouter(prefix="/api/v1")  

queue = []
curr_players = []

class Player(BaseModel):
    name: str
    phoneNumber: str

async def send_sms_v2(number:str, message:str):
    # need to fix this
    env_path = '/Users/amyliu/Projects/mqueue/.env'
    print(f"Looking for .env file at: {env_path}")

    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_number = os.getenv('TWILIO_PHONE_NUMBER')

    print("\nValues loaded:")
    print(f"TWILIO_ACCOUNT_SID: {account_sid}")
    print(f"TWILIO_AUTH_TOKEN: {auth_token}")
    print(f"TWILIO_PHONE_NUMBER: {twilio_number}")

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body='hi.',
            from_=twilio_number,
            to='+16504059992'
        )
        print(f"\nSuccess! Message sent with SID: {message.sid}")
    except Exception as e:
        print(f"\nError: {e}")

@router.post("/queue") 
async def add_to_queue(player: Player):
    queue.append({"name": player.name, "phoneNumber": player.phoneNumber})
    position = len(queue)
    # Send position in queue message
    await send_sms_v2(
        player.phoneNumber,
        f"Hi {player.name}! You are number {position} in the queue."
    )
    await remove_player()
    return {"message": "Player added successfully"}

@router.get("/queue")
async def get_queue():
    return queue

@router.get("/players") 
async def get_curr_players():
    return curr_players

@router.post("/stop")
async def handle_sms_webhook(request: Request):
    form_data = await request.form()
    message_body = form_data.get("Body", "").strip().upper()
    from_number = form_data.get("From", "")

    if message_body == "STOP":
        curr_players.clear()
        await remove_player()
        
        return {"message": "Game ended, next players notified"}
    
    return {"message": "Message received"}

async def remove_player():
    print(f"curr_players: {curr_players}")
    print(f"queue: {queue}")

    if len(curr_players) == 0 and len(queue) >= 4:
        for i in range(4):
            player = queue[0]
            await send_sms_v2(
                player["phoneNumber"],
                f"Hi {player['name']}! Your court is ready! Please proceed to the courts."
            )
            curr_players.append(queue.pop(0))
        return {"message": "Players moved to current players"}
    return {"message": "No players to move"}


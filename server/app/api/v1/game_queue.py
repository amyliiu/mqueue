from fastapi import APIRouter, Body
from pydantic import BaseModel
from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

router = APIRouter(prefix="/api/v1")  

queue = []
curr_players = []

class Player(BaseModel):
    name: str
    phoneNumber: str

async def send_sms(to_number: str, message: str):
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )
    except Exception as e:
        print(f"Error sending SMS: {e}")

@router.post("/queue") 
async def add_to_queue(player: Player):
    queue.append({"name": player.name, "phoneNumber": player.phoneNumber})
    position = len(queue)
    # Send position in queue message
    await send_sms(
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


from fastapi import APIRouter, Body
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1")  

queue = []
curr_players = []

class Player(BaseModel):
    name: str
    phoneNumber: str

@router.post("/queue") 
async def add_to_queue(player: Player):
    queue.append({"name": player.name, "phoneNumber": player.phoneNumber})
    print(f"added: {player.name} - {player.phoneNumber}")
    return {"message": "Player added successfully"}

@router.get("/queue")
async def get_queue():
    return queue

@router.get("/players") 
async def get_curr_players():
    return curr_players

async def remove_player():
    if len(curr_players) == 0 and len(queue) >= 4:
        for i in range(4):
            player = queue[0]
            # send_sms_endpoint(player["name"], "send message")
            curr_players.append(queue.pop(0))
        return {"message": "Players moved to current players"}
    return {"message": "No players to move"}


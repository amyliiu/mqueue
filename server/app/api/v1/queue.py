from fastapi import APIRouter, Body
from pydantic import BaseModel

# Remove the /api prefix from the routes since it's redundant
router = APIRouter(prefix="/api/queue")  # Add prefix here instead

queue = []
curr_players = []

class Player(BaseModel):
    name: str
    phoneNumber: str

@router.post("/add_to_queue")  # Remove /api/queue from here
async def add_to_queue(player: Player):
    queue.append({"name": player.name, "phoneNumber": player.phoneNumber})
    print(f"added: {player.name} - {player.phoneNumber}")
    return {"message": "Player added successfully"}

@router.get("/get_queue")  # Remove /api/queue from here
async def get_queue():
    return queue

@router.get("/get_curr_players")  # Remove /api/queue from here
async def get_curr_players():
    return curr_players

@router.get("/remove_player")  # Remove /api/queue from here
async def remove_player():
    if len(curr_players) == 0 and len(queue) >= 4:
        for i in range(4):
            player = queue[0]
            # send_sms_endpoint(player["name"], "send message")
            curr_players.append(queue.pop(0))
        return {"message": "Players moved to current players"}
    return {"message": "No players to move"}


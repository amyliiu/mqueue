from fastapi import APIRouter, FastAPI, Request, HTTPException
from pydantic import BaseModel
from twilio.rest import Client
from dotenv import load_dotenv
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
import logging

load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

print("Twilio Configuration:")
print(f"Account SID exists: {bool(TWILIO_ACCOUNT_SID)}")
print(f"Auth Token exists: {bool(TWILIO_AUTH_TOKEN)}")
print(f"Phone Number: {TWILIO_PHONE_NUMBER}")

router = APIRouter(prefix="/api/v1")
app = FastAPI()
queue_players = []
game_players = []

# Configure logging
logging.basicConfig(level=logging.INFO)

class Player(BaseModel):
    name: str
    phoneNumber: str
    groupSize: int

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

async def remove_player():
    global game_players
    global queue_players
    print(f"game_players: {game_players}")
    print(f"queue_players: {queue_players}")

    if len(game_players) == 0:
        total_players_in_queue = sum(player.get("groupSize", 1) for player in queue_players)
        print("total players in queue:" + str(total_players_in_queue))
        if total_players_in_queue >= 4:
            try:
                group_of_one = []
                group_of_two = []
                group_of_three = []
                curr_len_players = sum(player.get("groupSize", 1) for player in game_players)

                # Get the first player object
                first_player = queue_players[0]
                first_player_group_size = first_player.get("groupSize", 1)
                remaining_spots = 4 - first_player_group_size

                print(f"First player: {first_player}, Remaining spots: {remaining_spots}")

                if remaining_spots == 0:
                    game_players.append(first_player)  # Append the player object
                    queue_players.pop(0)  # Remove the player from the queue

                # Classify the remaining players
                for i in range(1, len(queue_players)):
                    player = queue_players[i]
                    if player.get("groupSize") == 1:
                        group_of_one.append(player)
                    elif player.get("groupSize") == 2:
                        group_of_two.append(player)
                    elif player.get("groupSize") == 3:
                        group_of_three.append(player)

                print(f"Group of one: {group_of_one}")
                print(f"Group of two: {group_of_two}")
                print(f"Group of three: {group_of_three}")

                # Logic for adding players based on remaining spots
                if remaining_spots == 1:
                    if len(group_of_one) != 0:
                        game_players.append(first_player)  # Append the player object
                        game_players.append(group_of_one[0])  # Append the player object
                        queue_players.pop(0)  # Remove the first player from the queue
                        queue_players.remove(group_of_one[0])  # Remove the group of one from the queue
                        print(f"Added {first_player['name']} and {group_of_one[0]['name']} to game_players")

                elif remaining_spots == 2:
                    if len(group_of_two) >= 1:
                        game_players.append(first_player)  # Append the player object
                        game_players.append(group_of_two[0])  # Append the player object
                        queue_players.pop(0)  # Remove the first player from the queue
                        queue_players.remove(group_of_two[0])  # Remove the group of two from the queue
                        print(f"Added {first_player['name']} and {group_of_two[0]['name']} to game_players")

                    elif len(group_of_one) >= 2:
                        game_players.append(first_player)  # Append the player object
                        game_players.append(group_of_one[0])  # Append the player object
                        game_players.append(group_of_one[1])  # Append the player object

                        queue_players.pop(0)  # Remove the first player from the queue
                        queue_players.remove(group_of_one[0])  # Remove the group of one from the queue
                        queue_players.remove(group_of_one[1])  # Remove the second group of one from the queue
                        print(f"Added {first_player['name']}, {group_of_one[0]['name']}, and {group_of_one[1]['name']} to game_players")

                elif remaining_spots == 3:
                    if len(group_of_three) != 0:
                        game_players.append(first_player)  # Append the player object
                        game_players.append(group_of_three[0])  # Append the player object
                        queue_players.pop(0)  # Remove the first player from the queue
                        queue_players.remove(group_of_three[0])  # Remove the group of three from the queue
                        print(f"Added {first_player['name']} and {group_of_three[0]['name']} to game_players")

                    elif len(group_of_two) >= 1 and len(group_of_one) >= 1:
                        game_players.append(first_player)  # Append the player object
                        game_players.append(group_of_one[0])  # Append the player object
                        game_players.append(group_of_two[0])  # Append the player object

                        queue_players.pop(0)  # Remove the first player from the queue
                        queue_players.remove(group_of_one[0])  # Remove the group of one from the queue
                        queue_players.remove(group_of_two[0])  # Remove the group of two from the queue
                        print(f"Added {first_player['name']}, {group_of_one[0]['name']}, and {group_of_two[0]['name']} to game_players")

                    elif len(group_of_one) >= 3:
                        game_players.append(first_player)  # Append the player object
                        game_players.append(group_of_one[0])  # Append the player object
                        game_players.append(group_of_one[1])  # Append the player object
                        game_players.append(group_of_one[2])  # Append the player object

                        queue_players.pop(0)  # Remove the first player from the queue
                        queue_players.remove(group_of_one[0])  # Remove the first group of one from the queue
                        queue_players.remove(group_of_one[1])  # Remove the second group of one from the queue
                        queue_players.remove(group_of_one[2])  # Remove the third group of one from the queue
                        print(f"Added {first_player['name']}, {group_of_one[0]['name']}, {group_of_one[1]['name']}, and {group_of_one[2]['name']} to game_players")

                curr_len_players = sum(player.get("groupSize", 1) for player in game_players)
                if curr_len_players == 4:
                    for player in game_players:
                        await send_sms(
                            player["phoneNumber"],
                            f"Hi {player['name']}, your court is ready! Please proceed with your group of {player.get('groupSize', 1)} to the courts. Remember to text 'DONE' to end your game."
                        )
                    return {"message": "Players moved to current players"}
                else:
                    return {"message": "No valid group of 4 could be formed."}

            except Exception as e:
                print(f"Error moving players: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
    return {"message": "No players to move"}

@router.get("/game")
async def get_game_players():
    """Get all players currently in the game"""
    return {"gamePlayers": game_players}

@router.get("/queue")
async def get_queue():
    """Get all players in queue with total count based on group sizes"""
    total_count = sum(player.get("groupSize", 1) for player in queue_players)
    return {
        "queue": queue_players,
        "total_count": total_count
    }

@router.post("/add-to-queue")
async def add_to_queue(player: Player):
    """Add a player to the queue"""
    try:
        print(f"Adding player: {player.name} ({player.phoneNumber}) with group size {player.groupSize}")
        queue_players.append({"name": player.name, "phoneNumber": player.phoneNumber, "groupSize": player.groupSize})
        position = sum(player.get("groupSize", 1) for player in queue_players)

        await send_sms(
            player.phoneNumber,
            f"Hi {player.name}! You are number {position - player.groupSize + 1} in the queue with a group of {player.groupSize} people."
        )
        if len(game_players) == 0:
            await remove_player()
        return {"message": "Player added successfully", "position": position - player.groupSize + 1}
    except Exception as e:
        print(f"Error adding player: {str(e)}")
        return {"error": str(e)}

async def fetch_twilio_message():
    """Fetch the latest Twilio message"""
    client = get_twilio_client()
    if not client:
        raise HTTPException(status_code=500, detail="Twilio client not initialized")

    messages = client.messages.list(limit=1)  # Fetch the latest messages
    return [{"from": msg.from_, "body": msg.body, "date_sent": msg.date_sent} for msg in messages]

@router.post("/done")
async def handle_sms_webhook(request: Request):
    """Handle SMS webhook for responding to messages"""
    try:
        form_data = await request.form()
        message_body = form_data.get("Body", "").strip().upper()
        from_number = form_data.get("From", "")
        from_number = from_number[2:]
 
        # Log the incoming message
        logging.info(f"Received message: {message_body} from {from_number}")

        # Create a Twilio MessagingResponse object
        response = MessagingResponse()

        # Respond based on the message content
        if message_body == "DONE":
            # Logic to remove the player from the queue
            if any(player["phoneNumber"] == from_number for player in game_players):
                # Call remove_player function
                await remove_player()
                response.message("Thank you! You have been removed from the queue.")
            else:
                response.message("You are not in the queue.")
        else:
            response.message("Sorry, I didn't understand that. Please send 'DONE' to proceed.")

        # Return the TwiML response
        return Response(content=str(response), media_type="text/xml")
    
    except Exception as e:
        logging.error(f"Error handling SMS webhook: {e}")
        return Response(content="Internal Server Error", status_code=500)

app.include_router(router)
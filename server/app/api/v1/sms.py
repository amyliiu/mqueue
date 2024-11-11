# server/app/api/v1/sms.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, StringConstraints
from typing_extensions import Annotated
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
import logging

router = APIRouter()

# Set up logging
logger = logging.getLogger("sms_api")

# Get Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Verify credentials
# if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
#     raise ValueError("Twilio credentials are not set in environment variables")

# # Initialize Twilio client
# twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

PhoneNumber = Annotated[str, StringConstraints(pattern=r'^\+?[1-9]\d{1,14}$')]

class SMSRequest(BaseModel):
    phoneNumber: PhoneNumber
    message: str

# # Create a router for version 1 of the SMS API
router = APIRouter()

@router.post("/send-sms")

async def send_sms_endpoint(sms_request: SMSRequest):
    """
    Endpoint to send an SMS message using Twilio.
    Expects a JSON payload with 'phoneNumber' and 'message'.
    """

    print("send message")

    # try:
    #     # Send SMS using Twilio
    #     message = twilio_client.messages.create(
    #         body=sms_request.message,
    #         from_=TWILIO_PHONE_NUMBER,
    #         to=sms_request.phoneNumber
    #     )
        
    #     # Return success response with message SID
    #     return {
    #         "success": True, 
    #         "message": "SMS sent successfully",
    #         "message_sid": message.sid
    #     }
    # except TwilioRestException as e:
    #     logger.error(f"Twilio error: {e}")
    #     raise HTTPException(status_code=400, detail="Failed to send SMS. Please check the phone number and message.")
    # except Exception as e:
    #     logger.error(f"Unexpected error: {e}")
    #     raise HTTPException(status_code=500, detail="Internal server error. Please try again later.")

# server/app/api/v1/sms.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, constr
from app.services.sms_service import send_sms

# Create a router for version 1 of the SMS API
router = APIRouter()

# Define the data structure for incoming SMS requests
class SMSRequest(BaseModel):
    phoneNumber: constr(regex=r'^\+?\d{10,15}$')  # A basic phone number pattern, allowing international formats
    message: constr(min_length=1, max_length=160)  # Limit message length to 160 characters for SMS

@router.post("/send-sms")
async def send_sms_endpoint(sms_request: SMSRequest):
    """
    Endpoint to send an SMS message.
    
    Expects a JSON payload with 'phoneNumber' and 'message'.
    """
    try:
        # Call the SMS service to send the message
        send_sms(sms_request.phoneNumber, sms_request.message)
        # If successful, return a success response
        return {"success": True, "message": "SMS sent successfully"}
    except Exception as e:
        # In case of error, raise an HTTPException
        raise HTTPException(status_code=500, detail=str(e))

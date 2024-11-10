# server/app/services/sms_service.py
def send_sms(phone_number: str, message: str):
    # Mock implementation for SMS sending
    print(f"Sending SMS to {phone_number}: {message}")
    # For a real implementation, integrate with an SMS provider here
    # e.g., using Twilio's API

// api.ts
export async function sendSMS(phoneNumber: string, message: string) {
    const response = await fetch('http://localhost:8000/api/v1/send-sms', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ phoneNumber, message }),
    });
    return response.json();
  }
  
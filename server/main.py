# server/app/main.py
from fastapi import FastAPI
# from slowapi import _rate_limit_exceeded_handler
# from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import sms  # Import the sms router
from app.api.v1 import queue  # Import the queue router
# from app.api.v1.sms import router, limiter

app = FastAPI()
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration to allow the frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust to your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the `v1` API routes
app.include_router(sms.router, prefix="/api/v1")
app.include_router(queue.router, prefix="/api/v1")

# Optional: Add a test endpoint
@app.get("/test")
async def test_endpoint():
    return {"message": "API is working"}
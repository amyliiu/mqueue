# server/app/main.py
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import sms  # Import the sms router
from app.api.v1 import game_queue  # Import the queue router
# from app.api.v1.sms import router, limiter

app = FastAPI()
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://mqueue.vercel.app",  # Add your actual Vercel domain
        "https://mqueue-git-main-amyliu1810.vercel.app",  # Add preview deployments
        "https://mqueue-amyliu1810.vercel.app"  # Add production deployment
    ],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    allow_credentials=False,
    max_age=3600,
)


app.include_router(sms.router)
app.include_router(game_queue.router)

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
        "https://mqueue-amyliius-projects.vercel.app",  # Add your actual Vercel domain
        "https://mqueue-git-mainv2-amyliius-projects.vercel.app",  # Add preview deployments
        "https://mqueue-ej80jgkq3-amyliius-projects.vercel.app"  # Add production deployment
    ],
    allow_methods=["*"],  # More permissive for testing
    allow_headers=["*"],  # More permissive for testing
    allow_credentials=True,  # Changed to True if you need to support credentials
    expose_headers=["*"],  # Expose all headers
    max_age=3600,
)

# edit

app.include_router(sms.router)
app.include_router(game_queue.router)

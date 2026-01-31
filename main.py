import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
import vertexai

# 1. Load environment variables at the very top
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 2. Initialize Vertex AI implicitly using .env variables
    # This works because the GOOGLE_APPLICATION_CREDENTIALS 
    # environment variable is set in the system.
    vertexai.init(
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    yield
    # Clean up resources if necessary

app = FastAPI(lifespan=lifespan)
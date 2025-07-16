import uvicorn
import os
from app import app
import os
from dotenv import load_dotenv

load_dotenv()
host = os.getenv("HOST", "0.0.0.0")
port = int(os.getenv("PORT", 3001))

def run():
    """Start the FastAPI server with uvicorn"""
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run()

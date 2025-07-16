from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi import APIRouter, UploadFile, File
from fastapi import HTTPException
from app import app
import os
import shutil
from dotenv import load_dotenv
from datetime import datetime
from utils import load_or_create_key_pair

# Load environment variables
load_dotenv()
mcp_server_name = os.getenv("MCP_SERVER_NAME")
mcp_version = os.getenv("MCP_SERVER_VERSION")
BASE_UPLOAD_DIR=os.getenv("BASE_UPLOAD_DIR","")

os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)

router = APIRouter(tags=["General"])

@router.get("/status")
async def status():
    """Status endpoint that returns the current server status"""
    return JSONResponse({
        "status": "running",
        "server": mcp_server_name,
        "version": mcp_version,
    })

@router.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    """Upload multiple files with timestamped names to prevent duplicates"""
    saved_files = []
    for file in files:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        filename = f"{os.path.splitext(file.filename)[0]}_{timestamp}{os.path.splitext(file.filename)[1]}" # type: ignore
        filepath = os.path.join(BASE_UPLOAD_DIR, filename)
        
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        saved_files.append(filename)
    
    return JSONResponse({"uploaded_files": saved_files})

@router.get("/files/{walletId}/{filename}")
async def get_file(filename: str, walletId: str):
    """Download a file by its name"""
    filepath = os.path.join(BASE_UPLOAD_DIR, walletId, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(filepath, media_type="application/octet-stream", filename=filename)

@router.post("/create-wallet/{walletId}")
async def create_payment_keys(walletId: str):
    """Create or load wallet key pair and return file links"""
    try:
        skey, vkey = load_or_create_key_pair(walletId, "payment")
        skey_filename = "payment.skey"
        vkey_filename = "payment.vkey"
        skey_url = f"/files/{walletId}/{skey_filename}"
        vkey_url = f"/files/{walletId}/{vkey_filename}"
        return JSONResponse({
            "success": True,
            "walletId": walletId,
            "message": "wallet created/loaded successfully",
            "skey_url": skey_url,
            "vkey_url": vkey_url
        })
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error creating payment keys: {str(e)}")

# Include router in main app
app.include_router(router)

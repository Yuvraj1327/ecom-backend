




#gemini

import os
import uuid
import mimetypes
import httpx
import hmac
import hashlib

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Optional

# Load environment variables
load_dotenv()

# --- 1. Configuration ---
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "change-me")
STORAGE_BUCKET = "product"

# Initialize Supabase Client
if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: SUPABASE_URL or SUPABASE_KEY missing in .env")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. App Setup ---
app = FastAPI(title="Aqua Skincare API", version="1.0.0")

# CORS Middleware (Frontend se connect karne ke liye zaroori hai)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Sabhi origins (3006, 5173, etc.) ko allow karein
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, OPTIONS sab allow karein
    allow_headers=["*"],
)
# Static files for local storage (optional)
if not os.path.exists("static"):
    os.makedirs("static")
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    pass

# Include Admin Router (Make sure admin.py exists in same folder)
try:
    from admin import router as admin_router
    app.include_router(admin_router)
except ImportError:
    print("⚠️ WARNING: admin.py not found. Admin routes might not work.")

# --- 3. Auth Helper ---
def verify_admin(x_admin_token: str = Header(...)):
    if x_admin_token != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid admin token")

# --- 4. Schemas (Data Models) ---
class CartItem(BaseModel):
    id: str
    name: str
    qty: int
    price: int

class CreateOrderRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    amount: int
    items: List[CartItem] = []

# --- 5. Image Upload Endpoint ---
@app.post("/admin/upload-image")
async def upload_image(file: UploadFile = File(...), x_admin_token: str = Header(...)):
    # Admin Security Check
    if x_admin_token != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid admin token")

    # File Type Validation
    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/avif"}
    content_type = file.content_type
    if content_type not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")

    data = await file.read()
    
    # Filename generation
    ext = mimetypes.guess_extension(content_type) or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"

    # Supabase Storage Upload logic
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{filename}"
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                upload_url,
                content=data,
                headers={
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": content_type,
                    "x-upsert": "true",
                },
                timeout=15.0
            )
            
            if resp.status_code not in (200, 201):
                print(f"❌ Storage Error: {resp.text}")
                raise HTTPException(status_code=500, detail="Failed to upload to Supabase Storage")

            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{filename}"
            return {"url": public_url, "filename": filename}

        except Exception as e:
            print(f"❌ Upload Exception: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# --- 6. Public Store Routes ---

@app.get("/")
def health():
    return {"status": "ok", "message": "Aqua API is running"}

@app.get("/products")
def get_products():
    """Fetch all active products for the frontend"""
    try:
        result = supabase.table("products").select("*").eq("active", True).order("created_at", desc=True).execute()
        return {"products": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-order")
async def create_order(body: CreateOrderRequest):
    """Bypassed Razorpay: Directly creates a pending order in Supabase"""
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid order amount")
    
    # Generate a Test Order ID
    fake_order_id = f"order_test_{uuid.uuid4().hex[:12]}"
    
    try:
        # Save order to Supabase 'purchases' table
        supabase.table("purchases").insert({
            "razorpay_order_id": fake_order_id,
            "customer_name":     body.name,
            "customer_email":    body.email,
            "customer_phone":    body.phone,
            "amount":            body.amount,
            "currency":          "INR",
            "items":             [i.model_dump() for i in body.items],
            "status":            "pending",
        }).execute()
        
        return {
            "order_id": fake_order_id, 
            "amount": body.amount, 
            "currency": "INR", 
            "message": "Order placed successfully (Test Mode)"
        }
    except Exception as e:
        print(f"❌ Database Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not save order")

# --- 7. Run Server ---
if __name__ == "__main__":
    import uvicorn
    # Change port to 8007 if you are using that in Frontend
    uvicorn.run(app, host="0.0.0.0", port=8007)
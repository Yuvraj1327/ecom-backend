




# #gemini

# import os
# import uuid
# import mimetypes
# import httpx
# import hmac
# import hashlib

# from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Depends, Header
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel, EmailStr
# from supabase import create_client, Client
# from dotenv import load_dotenv
# from typing import List, Optional

# # Load environment variables
# load_dotenv()

# # --- 1. Configuration ---
# SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
# SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
# ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "change-me")
# STORAGE_BUCKET = "product"

# # Initialize Supabase Client
# if not SUPABASE_URL or not SUPABASE_KEY:
#     print("❌ ERROR: SUPABASE_URL or SUPABASE_KEY missing in .env")
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# # --- 2. App Setup ---
# app = FastAPI(title="Aqua Skincare API", version="1.0.0")

# # CORS Middleware (Frontend se connect karne ke liye zaroori hai)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Sabhi origins (3006, 5173, etc.) ko allow karein
#     allow_credentials=True,
#     allow_methods=["*"],  # GET, POST, OPTIONS sab allow karein
#     allow_headers=["*"],
# )
# # Static files for local storage (optional)
# if not os.path.exists("static"):
#     os.makedirs("static")
# try:
#     app.mount("/static", StaticFiles(directory="static"), name="static")
# except:
#     pass

# # Include Admin Router (Make sure admin.py exists in same folder)
# try:
#     from admin import router as admin_router
#     app.include_router(admin_router)
# except ImportError:
#     print("⚠️ WARNING: admin.py not found. Admin routes might not work.")

# # --- 3. Auth Helper ---
# def verify_admin(x_admin_token: str = Header(...)):
#     if x_admin_token != ADMIN_SECRET:
#         raise HTTPException(status_code=401, detail="Invalid admin token")

# # --- 4. Schemas (Data Models) ---
# class CartItem(BaseModel):
#     id: str
#     name: str
#     qty: int
#     price: int

# class CreateOrderRequest(BaseModel):
#     name: str
#     email: EmailStr
#     phone: str
#     amount: int
#     items: List[CartItem] = []

# # --- 5. Image Upload Endpoint ---
# @app.post("/admin/upload-image")
# async def upload_image(file: UploadFile = File(...), x_admin_token: str = Header(...)):
#     # Admin Security Check
#     if x_admin_token != ADMIN_SECRET:
#         raise HTTPException(status_code=401, detail="Invalid admin token")

#     # File Type Validation
#     allowed = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/avif"}
#     content_type = file.content_type
#     if content_type not in allowed:
#         raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")

#     data = await file.read()
    
#     # Filename generation
#     ext = mimetypes.guess_extension(content_type) or ".jpg"
#     filename = f"{uuid.uuid4().hex}{ext}"

#     # Supabase Storage Upload logic
#     upload_url = f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{filename}"
    
#     async with httpx.AsyncClient() as client:
#         try:
#             resp = await client.post(
#                 upload_url,
#                 content=data,
#                 headers={
#                     "Authorization": f"Bearer {SUPABASE_KEY}",
#                     "Content-Type": content_type,
#                     "x-upsert": "true",
#                 },
#                 timeout=15.0
#             )
            
#             if resp.status_code not in (200, 201):
#                 print(f"❌ Storage Error: {resp.text}")
#                 raise HTTPException(status_code=500, detail="Failed to upload to Supabase Storage")

#             public_url = f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{filename}"
#             return {"url": public_url, "filename": filename}

#         except Exception as e:
#             print(f"❌ Upload Exception: {str(e)}")
#             raise HTTPException(status_code=500, detail=str(e))

# # --- 6. Public Store Routes ---

# @app.get("/")
# def health():
#     return {"status": "ok", "message": "Aqua API is running"}

# @app.get("/products")
# def get_products():
#     """Fetch all active products for the frontend"""
#     try:
#         result = supabase.table("products").select("*").eq("active", True).order("created_at", desc=True).execute()
#         return {"products": result.data}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/create-order")
# async def create_order(body: CreateOrderRequest):
#     """Bypassed Razorpay: Directly creates a pending order in Supabase"""
#     if body.amount <= 0:
#         raise HTTPException(status_code=400, detail="Invalid order amount")
    
#     # Generate a Test Order ID
#     fake_order_id = f"order_test_{uuid.uuid4().hex[:12]}"
    
#     try:
#         # Save order to Supabase 'purchases' table
#         supabase.table("purchases").insert({
#             "razorpay_order_id": fake_order_id,
#             "customer_name":     body.name,
#             "customer_email":    body.email,
#             "customer_phone":    body.phone,
#             "amount":            body.amount,
#             "currency":          "INR",
#             "items":             [i.model_dump() for i in body.items],
#             "status":            "pending",
#         }).execute()
        
#         return {
#             "order_id": fake_order_id, 
#             "amount": body.amount, 
#             "currency": "INR", 
#             "message": "Order placed successfully (Test Mode)"
#         }
#     except Exception as e:
#         print(f"❌ Database Error: {str(e)}")
#         raise HTTPException(status_code=500, detail="Could not save order")

# # --- 7. Run Server ---
# if __name__ == "__main__":
#     import uvicorn
#     # Change port to 8007 if you are using that in Frontend
#     uvicorn.run(app, host="0.0.0.0", port=8007)







#claude


"""
Prottiva Nutrition — Unified Backend API
==========================================
Combines:
  1. E-commerce API  (products, orders, image upload) → port 8007
  2. AI Face Glow-Up (Replicate nano-banana)          → /glowup endpoint

Run:  uvicorn main:app --host 0.0.0.0 --port 8007 --reload
"""

import asyncio
import base64
import io
import logging
import mimetypes
import os
import uuid

import httpx
import replicate
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, HTTPException, Request, UploadFile, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import List, Optional

# Try to load dotenv (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Try to load Supabase (optional — disable if not needed)
try:
    from supabase import create_client, Client as SupabaseClient
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: SupabaseClient = create_client(SUPABASE_URL, SUPABASE_KEY)
        SUPABASE_ENABLED = True
        print("✅ Supabase connected")
    else:
        SUPABASE_ENABLED = False
        print("⚠️  Supabase not configured — using in-memory store")
except ImportError:
    SUPABASE_ENABLED = False
    print("⚠️  supabase-py not installed — using in-memory store")

# ── Config ────────────────────────────────────────────────────────────────────
ADMIN_SECRET        = os.environ.get("ADMIN_SECRET", "prottiva-admin-secret")
STORAGE_BUCKET      = "product"
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")
GLOWUP_MODEL        = "google/nano-banana"
GLOWUP_PROMPT       = (
    "Glow up this person's face naturally. "
    "Keep the exact same person, same face, same identity, same skin tone, same hair. "
    "Only enhance: smooth the skin, improve brightness, add natural radiance, "
    "enhance eyes slightly, improve lighting to be soft and flattering. "
    "Do not change who the person is. Natural beauty enhancement only."
)

# In-memory fallback stores (used when Supabase is not configured)
_products_store: List[dict] = []
_orders_store:   List[dict] = []

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
logger = logging.getLogger("prottiva")


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app):
    logger.info("🚀 Prottiva API starting…")
    if not REPLICATE_API_TOKEN:
        logger.warning("⚠️  REPLICATE_API_TOKEN not set — /glowup will fail")
    else:
        logger.info("✅ Replicate token OK  |  model: %s", GLOWUP_MODEL)
    yield
    logger.info("👋 Prottiva API shutting down")


# ── App Setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Prottiva Nutrition API",
    version="2.0.0",
    description="Unified ecommerce + AI face glow-up backend",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (optional local storage)
os.makedirs("static", exist_ok=True)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception:
    pass

# Include optional admin router
try:
    from admin import router as admin_router
    app.include_router(admin_router)
    logger.info("✅ Admin router loaded")
except ImportError:
    logger.warning("⚠️  admin.py not found — admin routes skipped")


# ── Auth Helper ───────────────────────────────────────────────────────────────
def verify_admin(x_admin_token: str = Header(...)):
    if x_admin_token != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid admin token")


# ── Pydantic Models ───────────────────────────────────────────────────────────
class CartItem(BaseModel):
    id:    str
    name:  str
    qty:   int
    price: int

class CreateOrderRequest(BaseModel):
    name:   str
    email:  EmailStr
    phone:  str
    amount: int
    items:  List[CartItem] = []

class ProductCreate(BaseModel):
    name:        str
    description: Optional[str] = ""
    price:       int
    mrp:         Optional[int] = None
    category:    Optional[str] = "Skincare"
    cat:         Optional[str] = None          # alias
    tag:         Optional[str] = "New"
    rating:      Optional[float] = 5.0
    rev:         Optional[int] = 0
    ml:          Optional[str] = ""
    ingredients: Optional[str] = ""
    image_url:   Optional[str] = None
    active:      Optional[bool] = True

class GlowUpResponse(BaseModel):
    imageUrl: str
    message:  str = "Glow-up complete! ✨"


# ════════════════════════════════════════════════════════════════════════════
#  HEALTH
# ════════════════════════════════════════════════════════════════════════════
@app.get("/")
def health():
    return {
        "status":   "ok",
        "message":  "Prottiva API is running 🌿",
        "supabase": SUPABASE_ENABLED,
        "replicate": bool(REPLICATE_API_TOKEN),
    }

@app.get("/health")
def health_detail():
    return {
        "api":      "ok",
        "supabase": SUPABASE_ENABLED,
        "replicate": bool(REPLICATE_API_TOKEN),
        "glowup_model": GLOWUP_MODEL,
    }


# ════════════════════════════════════════════════════════════════════════════
#  PRODUCTS  (public)
# ════════════════════════════════════════════════════════════════════════════
@app.get("/products")
def get_products():
    """Fetch all active products"""
    if SUPABASE_ENABLED:
        try:
            result = (
                supabase.table("products")
                .select("*")
                .eq("active", True)
                .order("created_at", desc=True)
                .execute()
            )
            return {"products": result.data}
        except Exception as e:
            logger.error("Supabase fetch error: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    else:
        return {"products": [p for p in _products_store if p.get("active", True)]}


@app.get("/products/{product_id}")
def get_product(product_id: str):
    """Fetch single product by ID"""
    if SUPABASE_ENABLED:
        try:
            result = supabase.table("products").select("*").eq("id", product_id).single().execute()
            if not result.data:
                raise HTTPException(status_code=404, detail="Product not found")
            return result.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        p = next((p for p in _products_store if str(p["id"])==product_id), None)
        if not p:
            raise HTTPException(status_code=404, detail="Product not found")
        return p


# ════════════════════════════════════════════════════════════════════════════
#  ORDERS
# ════════════════════════════════════════════════════════════════════════════
@app.post("/create-order")
async def create_order(body: CreateOrderRequest):
    """
    Creates an order and saves to Supabase (or in-memory store).
    Returns order_id for confirmation page.
    """
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid order amount")

    order_id = f"PN-{uuid.uuid4().hex[:10].upper()}"
    order_data = {
        "id":               order_id,
        "customer_name":    body.name,
        "customer_email":   body.email,
        "customer_phone":   body.phone,
        "amount":           body.amount,
        "currency":         "INR",
        "items":            [i.model_dump() for i in body.items],
        "status":           "confirmed",
    }

    if SUPABASE_ENABLED:
        try:
            supabase.table("purchases").insert({
                **order_data,
                "razorpay_order_id": order_id,
            }).execute()
        except Exception as e:
            logger.error("❌ DB error: %s", e)
            raise HTTPException(status_code=500, detail="Could not save order")
    else:
        _orders_store.append(order_data)
        logger.info("📦 Order saved in-memory: %s", order_id)

    return {
        "order_id":  order_id,
        "amount":    body.amount,
        "currency":  "INR",
        "status":    "confirmed",
        "message":   "Order placed successfully ✅",
    }


@app.get("/orders")
def get_orders(_: str = Depends(verify_admin)):
    """Admin: list all orders"""
    if SUPABASE_ENABLED:
        try:
            result = supabase.table("purchases").select("*").order("created_at", desc=True).execute()
            return {"orders": result.data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        return {"orders": _orders_store}


# ════════════════════════════════════════════════════════════════════════════
#  ADMIN: IMAGE UPLOAD
# ════════════════════════════════════════════════════════════════════════════
@app.post("/admin/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    x_admin_token: str = Header(...),
):
    if x_admin_token != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid admin token")

    allowed = {"image/jpeg","image/png","image/webp","image/gif","image/avif"}
    content_type = file.content_type or ""
    if content_type not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")

    data = await file.read()
    ext      = mimetypes.guess_extension(content_type) or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"

    if SUPABASE_ENABLED:
        upload_url = f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{filename}"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    upload_url,
                    content=data,
                    headers={
                        "Authorization": f"Bearer {SUPABASE_KEY}",
                        "Content-Type":  content_type,
                        "x-upsert":      "true",
                    },
                    timeout=20.0,
                )
                if resp.status_code not in (200, 201):
                    raise HTTPException(status_code=500, detail="Supabase upload failed")
                public_url = f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{filename}"
                return {"url": public_url, "filename": filename}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    else:
        # Fallback: save to local static folder
        local_path = f"static/{filename}"
        with open(local_path, "wb") as f_out:
            f_out.write(data)
        return {"url": f"/static/{filename}", "filename": filename}


# ════════════════════════════════════════════════════════════════════════════
#  ADMIN: PRODUCTS CRUD
# ════════════════════════════════════════════════════════════════════════════
@app.post("/admin/products")
async def create_product(body: ProductCreate, _: str = Depends(verify_admin)):
    """Admin: create a new product"""
    product = body.model_dump()
    if not product.get("cat"):
        product["cat"] = product.get("category", "Skincare")

    if SUPABASE_ENABLED:
        try:
            result = supabase.table("products").insert(product).execute()
            return {"product": result.data[0] if result.data else product}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        product["id"] = len(_products_store) + 1
        _products_store.append(product)
        return {"product": product}


@app.patch("/admin/products/{product_id}")
async def update_product(product_id: str, body: dict, _: str = Depends(verify_admin)):
    """Admin: update product fields"""
    if SUPABASE_ENABLED:
        try:
            result = supabase.table("products").update(body).eq("id", product_id).execute()
            return {"product": result.data[0] if result.data else body}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        for p in _products_store:
            if str(p["id"]) == product_id:
                p.update(body)
                return {"product": p}
        raise HTTPException(status_code=404, detail="Product not found")


@app.delete("/admin/products/{product_id}")
async def delete_product(product_id: str, _: str = Depends(verify_admin)):
    """Admin: soft-delete product"""
    if SUPABASE_ENABLED:
        try:
            supabase.table("products").update({"active": False}).eq("id", product_id).execute()
            return {"message": "Product deactivated"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        for p in _products_store:
            if str(p["id"]) == product_id:
                p["active"] = False
                return {"message": "Product deactivated"}
        raise HTTPException(status_code=404, detail="Product not found")


# ════════════════════════════════════════════════════════════════════════════
#  AI GLOW-UP  (Replicate nano-banana)
# ════════════════════════════════════════════════════════════════════════════
ALLOWED_MIME = {"image/jpeg","image/png","image/webp","image/gif"}
MAX_BYTES     = 10 * 1024 * 1024   # 10 MB


def _validate_image(file: UploadFile, data: bytes) -> str:
    mime = file.content_type or ""
    if mime not in ALLOWED_MIME:
        guessed, _ = mimetypes.guess_type(file.filename or "")
        mime = guessed or mime
    if mime not in ALLOWED_MIME:
        raise HTTPException(415, f"Unsupported type: {mime}. Use JPEG, PNG or WebP.")
    if not data:
        raise HTTPException(400, "File is empty.")
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File too large. Max 10 MB.")
    return mime


async def _run_glowup(image_bytes: bytes, mime: str) -> str:
    """Call Replicate google/nano-banana and return the output image URL."""
    if not REPLICATE_API_TOKEN:
        raise HTTPException(503, "REPLICATE_API_TOKEN is not configured on the server.")

    image_file      = io.BytesIO(image_bytes)
    image_file.name = "face.jpg"

    logger.info("→ Calling %s  size=%d bytes", GLOWUP_MODEL, len(image_bytes))

    try:
        loop   = asyncio.get_event_loop()
        output = await loop.run_in_executor(
            None,
            lambda: replicate.run(
                GLOWUP_MODEL,
                input={
                    "prompt":         GLOWUP_PROMPT,
                    "image_input":    [image_file],
                    "aspect_ratio":   "match_input_image",
                    "output_format":  "jpg",
                },
            ),
        )
    except replicate.exceptions.ReplicateError as exc:
        logger.error("Replicate error: %s", exc)
        raise HTTPException(502, f"Replicate error: {exc}")
    except Exception as exc:
        logger.exception("Unexpected glow-up error")
        raise HTTPException(500, f"Error: {exc}")

    logger.info("← Raw output: %s  %r", type(output).__name__, str(output)[:120])

    # Resolve output URL
    url = None
    if hasattr(output, "url"):
        url = str(output.url)
    elif isinstance(output, list) and output:
        item = output[0]
        if hasattr(item, "url"):
            url = str(item.url)
        elif isinstance(item, str):
            url = item
        else:
            try:
                raw = item.read()
                url = "data:image/jpeg;base64," + base64.b64encode(raw).decode()
            except Exception:
                url = str(item)
    elif isinstance(output, str):
        url = output
    else:
        try:
            raw = output.read()
            url = "data:image/jpeg;base64," + base64.b64encode(raw).decode()
        except Exception:
            url = str(output)

    if not url:
        raise HTTPException(502, "Replicate returned empty output.")

    logger.info("✓ Glow-up URL: %s", url[:80])
    return url


@app.post("/glowup", response_model=GlowUpResponse)
async def glowup(image: UploadFile = File(...)):
    """
    Accept a face photo → run Replicate nano-banana glow-up → return enhanced image URL.
    """
    logger.info("Glow-up request: %s  %s", image.filename, image.content_type)
    try:
        data = await image.read()
    except Exception as exc:
        raise HTTPException(400, f"Cannot read file: {exc}")
    finally:
        await image.close()

    mime = _validate_image(image, data)
    url  = await _run_glowup(data, mime)
    return GlowUpResponse(imageUrl=url)


# ════════════════════════════════════════════════════════════════════════════
#  AI SKIN ANALYSIS  (Replicate nano-banana — text + optional image)
# ════════════════════════════════════════════════════════════════════════════

# Skin analysis prompt — nano-banana ke liye structured JSON output
SKIN_ANALYSIS_PROMPT_TEMPLATE = """You are an expert AI dermatologist for Prottiva Nutrition, a premium science-backed Indian skincare brand.

A customer has answered a skin quiz. Based on their answers{image_note}, provide a detailed, personalised skin analysis.

QUIZ ANSWERS:
{quiz_answers}

Return ONLY a valid JSON object — no markdown, no extra text, no explanation. Exactly this schema:
{{
  "skinType": "one of: Oily | Dry | Combination | Normal | Sensitive",
  "skinScore": <integer 50-95>,
  "headline": "<catchy 1-line summary of their skin, max 10 words>",
  "topConcerns": ["<concern 1>", "<concern 2>", "<concern 3>"],
  "routine": {{
    "morning": ["<step 1>", "<step 2>", "<step 3>", "<step 4>"],
    "evening": ["<step 1>", "<step 2>", "<step 3>", "<step 4>"]
  }},
  "ingredientsToSeek": ["<ingredient 1>", "<ingredient 2>", "<ingredient 3>", "<ingredient 4>"],
  "ingredientsToAvoid": ["<ingredient 1>", "<ingredient 2>"],
  "lifestyleTip": "<one actionable daily tip for their skin>",
  "imageObservation": "<if photo analysed: one sentence skin observation from the image, else empty string>",
  "recommendedProductIds": [<3 integers from 1-8 best matching this skin profile>]
}}"""

SKIN_ANALYSIS_MODEL = "google/nano-banana"


class SkinAnalysisRequest(BaseModel):
    """
    Frontend sends quiz answers as key-value dict.
    Optionally sends a base64-encoded selfie image.
    """
    answers: dict                        # e.g. {"type": "Very oily / shiny", ...}
    image_base64: Optional[str] = None   # pure base64, no data-URI prefix
    image_mime: Optional[str] = "image/jpeg"


class SkinAnalysisResponse(BaseModel):
    skinType:             str
    skinScore:            int
    headline:             str
    topConcerns:          List[str]
    routine:              dict
    ingredientsToSeek:    List[str]
    ingredientsToAvoid:   List[str]
    lifestyleTip:         str
    imageObservation:     str = ""
    recommendedProductIds: List[int]


async def _run_skin_analysis(prompt: str, image_bytes: Optional[bytes] = None) -> str:
    """
    Call nano-banana with a text prompt (+ optional image) and return raw text output.
    nano-banana is a vision-language model — it can process both text and images.
    """
    if not REPLICATE_API_TOKEN:
        raise HTTPException(503, "REPLICATE_API_TOKEN is not configured on the server.")

    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

    logger.info("→ Skin analysis via %s  (image=%s)", SKIN_ANALYSIS_MODEL, image_bytes is not None)

    def _call_replicate():
        inp: dict = {
            "prompt": prompt,
            "max_new_tokens": 800,
            "temperature": 0.2,       # low temp = more deterministic JSON
            "top_p": 0.9,
        }
        # Attach image if provided
        if image_bytes:
            img_file      = io.BytesIO(image_bytes)
            img_file.name = "skin.jpg"
            inp["image_input"] = [img_file]

        return replicate.run(SKIN_ANALYSIS_MODEL, input=inp)

    try:
        loop   = asyncio.get_event_loop()
        output = await loop.run_in_executor(None, _call_replicate)
    except replicate.exceptions.ReplicateError as exc:
        logger.error("Replicate skin analysis error: %s", exc)
        raise HTTPException(502, f"Replicate error: {exc}")
    except Exception as exc:
        logger.exception("Unexpected skin analysis error")
        raise HTTPException(500, f"Internal error: {exc}")

    # Collect text output
    text = ""
    if isinstance(output, str):
        text = output
    elif isinstance(output, list):
        # streaming list of tokens
        text = "".join(str(t) for t in output)
    elif hasattr(output, "__iter__"):
        text = "".join(str(t) for t in output)
    else:
        text = str(output)

    logger.info("✓ Skin analysis raw output (%d chars): %s…", len(text), text[:120])
    return text.strip()


def _extract_json(raw: str) -> dict:
    """Extract the first valid JSON object from raw model output."""
    import json, re

    # Try direct parse first
    clean = raw.strip()
    # Strip markdown fences
    clean = re.sub(r"```json\s*", "", clean)
    clean = re.sub(r"```\s*", "", clean)
    clean = clean.strip()

    # Find JSON object boundaries
    start = clean.find("{")
    end   = clean.rfind("}") + 1
    if start != -1 and end > start:
        candidate = clean[start:end]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # Last resort — try the full cleaned string
    try:
        return json.loads(clean)
    except Exception:
        raise ValueError(f"Could not parse JSON from model output:\n{raw[:400]}")


@app.post("/skin-analysis", response_model=SkinAnalysisResponse)
async def skin_analysis(body: SkinAnalysisRequest):
    """
    AI Skin Test endpoint:
      - Accepts quiz answers (dict) + optional base64 selfie
      - Sends to Replicate nano-banana for skin profiling
      - Returns structured JSON skin analysis
    """
    if not body.answers:
        raise HTTPException(400, "Quiz answers are required.")

    # Format quiz answers into readable text
    quiz_text = "\n".join(f"  • {q}: {a}" for q, a in body.answers.items())

    # Build prompt
    image_note = " and their skin photo" if body.image_base64 else ""
    prompt = SKIN_ANALYSIS_PROMPT_TEMPLATE.format(
        image_note=image_note,
        quiz_answers=quiz_text,
    )

    # Decode image if provided
    img_bytes: Optional[bytes] = None
    if body.image_base64:
        try:
            img_bytes = base64.b64decode(body.image_base64)
            logger.info("Image received: %d bytes", len(img_bytes))
        except Exception as e:
            logger.warning("Could not decode base64 image: %s", e)
            img_bytes = None   # proceed without image rather than failing

    # Call Replicate
    raw_output = await _run_skin_analysis(prompt, img_bytes)

    # Parse JSON from model output
    try:
        result = _extract_json(raw_output)
    except ValueError as e:
        logger.error("JSON parse failed: %s", e)
        raise HTTPException(502, f"Model returned invalid JSON. Raw: {raw_output[:300]}")

    # Validate / fill defaults for missing keys
    defaults = {
        "skinType":             "Combination",
        "skinScore":            72,
        "headline":             "Your skin has unique needs",
        "topConcerns":          ["Hydration", "Barrier health", "UV protection"],
        "routine":              {"morning": ["Cleanser", "Toner", "Moisturiser", "SPF"], "evening": ["Cleanser", "Serum", "Moisturiser", "Eye cream"]},
        "ingredientsToSeek":   ["Hyaluronic Acid", "Niacinamide", "Ceramides", "SPF"],
        "ingredientsToAvoid":  ["Alcohol", "Fragrances"],
        "lifestyleTip":        "Drink at least 8 glasses of water daily.",
        "imageObservation":    "",
        "recommendedProductIds": [1, 3, 4],
    }
    for k, v in defaults.items():
        if k not in result or result[k] is None:
            result[k] = v

    # Clamp skinScore to valid range
    try:
        result["skinScore"] = max(50, min(95, int(result["skinScore"])))
    except (TypeError, ValueError):
        result["skinScore"] = 72

    # Ensure recommendedProductIds is a list of ints (max 3)
    try:
        result["recommendedProductIds"] = [int(x) for x in result["recommendedProductIds"]][:3]
    except Exception:
        result["recommendedProductIds"] = [1, 3, 4]

    logger.info("✅ Skin analysis complete — skinType=%s score=%s", result.get("skinType"), result.get("skinScore"))
    return SkinAnalysisResponse(**result)


# ════════════════════════════════════════════════════════════════════════════
#  SEED (dev helper — adds demo products to in-memory store)
# ════════════════════════════════════════════════════════════════════════════
@app.post("/dev/seed")
def seed_demo_products():
    """DEV ONLY: seed in-memory store with demo products"""
    if SUPABASE_ENABLED:
        return {"message": "Using Supabase — seed from Supabase dashboard instead."}

    demo = [
        {"id":1,"name":"Hydra Boost Serum",       "cat":"Serum",       "price":1899,"mrp":2499,"emoji":"💧","tag":"Bestseller","description":"Tri-peptide & HA complex for 72hr hydration.","rating":4.9,"rev":2140,"active":True},
        {"id":2,"name":"Vitamin C Radiance Glow",  "cat":"Serum",       "price":1599,"mrp":1999,"emoji":"🍊","tag":"New",        "description":"15% Vitamin C with ferulic acid.","rating":4.7,"rev":980, "active":True},
        {"id":3,"name":"Barrier Repair Moisturiser","cat":"Moisturiser", "price":1299,"mrp":1699,"emoji":"🧴","tag":"Sensitive",  "description":"Ceramide + niacinamide fortified barrier cream.","rating":4.8,"rev":1560,"active":True},
        {"id":4,"name":"SPF 50 PA++++ Sunfluid",   "cat":"Sunscreen",   "price":999, "mrp":1299,"emoji":"☀️","tag":"SPF 50",     "description":"Invisible mineral-chemical hybrid SPF.","rating":4.8,"rev":3350,"active":True},
        {"id":5,"name":"Retinol Night Renewal",     "cat":"Treatment",   "price":2199,"mrp":2799,"emoji":"🌙","tag":"Anti-age",   "description":"0.3% encapsulated retinol with bakuchiol.","rating":4.6,"rev":760, "active":True},
        {"id":6,"name":"Peptide Eye Elixir",        "cat":"Eye Care",    "price":1799,"mrp":2299,"emoji":"👁️","tag":"Anti-age",   "description":"Matrixyl 3000 + caffeine eye treatment.","rating":4.9,"rev":2070,"active":True},
        {"id":7,"name":"AHA BHA Exfoliating Toner", "cat":"Toner",       "price":899, "mrp":1199,"emoji":"✨","tag":"Exfoliant",  "description":"5% glycolic & 2% salicylic acid toner.","rating":4.7,"rev":1200,"active":True},
        {"id":8,"name":"Overnight Repair Mask",     "cat":"Mask",        "price":1099,"mrp":1399,"emoji":"🍯","tag":"Hydrating",  "description":"Manuka honey + ceramide sleeping mask.","rating":4.6,"rev":870, "active":True},
    ]
    _products_store.clear()
    _products_store.extend(demo)
    return {"message": f"Seeded {len(demo)} demo products ✅"}


# ════════════════════════════════════════════════════════════════════════════
#  RUN
# ════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8007, reload=True)
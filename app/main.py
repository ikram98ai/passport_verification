from fastapi import FastAPI, UploadFile, HTTPException, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from mangum import Mangum
from .ai import extract_info, verify_passport, FaceNotFoundException
from .utils import get_base64_url
import traceback

app = FastAPI(version="1.0.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse("/index")


@app.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    context = {
        "request": request,
        "extraction_output": None,
        "extraction_error": None,
        "verification_result": None,
        "verification_error": None,
    }
    return templates.TemplateResponse("index.html", context)


@app.post("/extraction", response_class=HTMLResponse)
async def passport_info_extraction(
    request: Request,
    passport_img: UploadFile = File(
        ..., description="Upload an image of passport for verification."
    ),
):
    output = None
    error = None
    try:
        passport_base64_url = await get_base64_url(passport_img)
        output = await extract_info(passport_base64_url)

    except HTTPException as e:
        traceback.print_exc()
        error = str(e.detail)
    except Exception as e:
        print(f"Error during extracting data: {e}")
        traceback.print_exc()
        error = str(e)
        
    context = {
        "request": request,
        "extraction_output": output.model_dump() if output else None,
        "extraction_error": error,
        "verification_result": None,
        "verification_error": None,
    }
    return templates.TemplateResponse("index.html", context)


@app.post("/verification", response_class=HTMLResponse)
async def passport_verification(
    request: Request,
    passport_img: UploadFile = File(
        ..., description="Upload an image of passport for verification."
    ),
    capture_img: UploadFile = File(
        ..., description="Upload your image to verify your passport."
    ),
):
    verification_result = None
    error = None
    try:
        verification_result = await verify_passport(capture_img, passport_img)
    except (FaceNotFoundException, ValueError) as e:
        error = str(e)
    except HTTPException as e:
        traceback.print_exc()
        error = str(e.detail)
    except Exception as e:
        print(f"Error during passport verification: {e}")
        traceback.print_exc()
        error = str(e)
        
    context = {
        "request": request,
        "extraction_output": None,
        "extraction_error": None,
        "verification_result": verification_result,
        "verification_error": error,
    }
    return templates.TemplateResponse("index.html", context)


handler = Mangum(app)
from fastapi import FastAPI, UploadFile, HTTPException, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from mangum import Mangum
from ai import extract_info, extract_image, verify_passport
from utils import get_base64_urls
import traceback

app = FastAPI(version="0.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse("/index")


@app.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/verification", response_class=HTMLResponse)
async def passport_verification(
    request: Request,
    passport_img: UploadFile = File(
        ..., description="Upload an image of passport for verification."
    ),
):
    try:
        passport_base64 = await get_base64_urls(passport_img)
        output = await extract_info(passport_base64)

    except HTTPException as e:
        traceback.print_exc()
        raise e
    except Exception as e:
        print(f"Error during compliance verification: {e}")
        traceback.print_exc()
        raise HTTPException(500, str(e))
    return templates.TemplateResponse(
        "verification_result.html", {"request": request, "output": output}
    )


@app.post("/extraction", response_class=HTMLResponse)
async def passport_info_extraction(
    request: Request,
    passport_img: UploadFile = File(
        ..., description="Upload an image of passport for verification."
    ),
    capture_img: UploadFile = File(
        ..., description="Upload your image to verify your passport."
    ),
):
    try:
        passport_base64 = await get_base64_urls(passport_img)
        capture_base64 = await get_base64_urls(capture_img)

        extract_base64 = await extract_image(passport_base64)
        output = await verify_passport(extract_base64, capture_base64)

    except HTTPException as e:
        traceback.print_exc()
        raise e
    except Exception as e:
        print(f"Error during compliance verification: {e}")
        traceback.print_exc()
        raise HTTPException(500, str(e))
    return templates.TemplateResponse(
        "extraction_result.html", {"request": request, "output": output}
    )


handler = Mangum(app)

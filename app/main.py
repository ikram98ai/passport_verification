from fastapi import FastAPI, UploadFile, HTTPException, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from mangum import Mangum
from ai import extract_info, verify_passport, FaceNotMatchedException
from utils import get_base64_url
import traceback

app = FastAPI(version="1.0.0")
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


@app.post("/extraction", response_class=HTMLResponse)
async def passport_info_extraction(
    request: Request,
    passport_img: UploadFile = File(
        ..., description="Upload an image of passport for verification."
    ),
):
    try:
        passport_base64_url = await get_base64_url(passport_img)
        output = await extract_info(passport_base64_url)

    except HTTPException as e:
        traceback.print_exc()
        raise e
    except Exception as e:
        print(f"Error during extracting data: {e}")
        traceback.print_exc()
        raise HTTPException(500, str(e))
    return templates.TemplateResponse(
        "extraction_result.html", {"request": request, "output": output.model_dump()}
    )


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
    try:
        similarity, matched_face = await verify_passport(capture_img, passport_img)
        return templates.TemplateResponse(
            "verification_result.html",
            {
                "request": request,
                "similarity": similarity,
                "matched_face": matched_face,
            },
        )
    except FaceNotMatchedException as e:
        return templates.TemplateResponse(
            "verification_result.html",
            {"request": request, "error": str(e)},
        )
    except HTTPException as e:
        traceback.print_exc()
        raise e
    except Exception as e:
        print(f"Error during passport verification: {e}")
        traceback.print_exc()
        raise HTTPException(500, str(e))


handler = Mangum(app)

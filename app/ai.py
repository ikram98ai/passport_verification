from pydantic import BaseModel
from fastapi import UploadFile
from prompts import INFO_EXTRACTION_PROMPT, IMAGE_EXTRACTION_PROMPT, PERSON_VERIFICATION_PROMPT
from utils import get_completion, get_content_list, get_base64_url, crop_image


class PassportInfo(BaseModel):
    nationality: str
    full_name: str
    surname: str
    passport_type: str
    date_of_birth: str
    personal_number: str
    gender: str
    expiration_date: str


async def extract_info(passport_base64_url) -> PassportInfo:
    content = get_content_list(
        [passport_base64_url], "Extract information from this passport."
    )
    info = await get_completion(
        instruction=INFO_EXTRACTION_PROMPT, content=content, output_type=PassportInfo
    )
    return info


class Bbox(BaseModel):
    x: int
    y: int
    width: float
    height: float


async def extract_image(passport_img: UploadFile) -> bytes:
    passport_base64_url = await get_base64_url(passport_img)
    content = get_content_list(
        [passport_base64_url], "Extract the bounding box from the given passport."
    )

    bbox = await get_completion(
        instruction=IMAGE_EXTRACTION_PROMPT,
        content=content,
        output_type=Bbox,
        model="gemini-2.5-flash",
    )

    print("Extracted Bounding Box: ", bbox)

    base64_url = await crop_image(passport_img, bbox)
    return base64_url


async def verify_passport(extracted_base64_url, capture_base64_url):
    content = get_content_list(
        [extracted_base64_url,capture_base64_url], "Verify that if the first image has the same person as in the second image."
    )

    output = await get_completion(
        instruction=PERSON_VERIFICATION_PROMPT,
        content=content,
        output_type=Bbox,
        model="gemini-2.5-flash",
    )

    return output

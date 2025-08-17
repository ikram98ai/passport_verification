from pydantic import BaseModel
from prompts import INFO_EXTRACTION_PROPMPT
from utils import get_completion


class PassportInfo(BaseModel):
    nationality: str
    full_name: str
    surname: str
    passport_type: str
    date_of_birth: str
    personal_number: str
    gender: str
    expiration_date: str


async def extract_info(passport_base64) -> PassportInfo:
    content = [
        {
            "type": "text",
            "text": "Extract information from this passport.",
        },
        {
            "type": "image_url",
            "image_url": {"url": passport_base64},
        },
    ]

    info = await get_completion(
        instruction=INFO_EXTRACTION_PROPMPT, content=content, output_type=PassportInfo
    )
    return info


async def extract_image(passport: bytes):
    pass


async def verify_passport(extracted_img, capture_img):
    pass

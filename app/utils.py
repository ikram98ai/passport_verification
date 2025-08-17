from fastapi import UploadFile, HTTPException
from openai import AsyncOpenAI
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
from typing import List
import base64
import os

load_dotenv()


async def get_completion(
    instruction: str, content: dict, output_type=None, model="gemini-2.0-flash-lite"
):
    client = AsyncOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    if output_type:
        completion = await client.chat.completions.parse(
            model=model,
            messages=[{"role": "system", "content": instruction}]
            + [{"role": "user", "content": content}],
            response_format=output_type,
        )
        return completion.choices[-1].message.parsed

    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": instruction}]
        + [{"role": "user", "content": content}],
    )
    return response.choices[-1].message.content


async def get_base64_url(file: UploadFile) -> str:
    # If UploadFile instances are provided, convert to base64
    try:
        print(f"Processing file: {file.filename}")
        content = await file.read()
        media_type = file.content_type or "image/jpeg"
        base64_image = base64.b64encode(content).decode("utf-8")
        base64_url = f"data:{media_type};base64,{base64_image}"
        return base64_url
    except Exception as e:
        print(f"Error processing file {file.filename}: {e}")
        raise HTTPException(400, f"Error processing file {file.filename}: {str(e)}")


async def crop_image(passport_img: UploadFile, bbox) -> str:
    await passport_img.seek(0)
    img = await passport_img.read()
    image = Image.open(BytesIO(img))

    # Crop the image
    cropped_image = image.crop(
        (bbox.x, bbox.y, bbox.x + bbox.width, bbox.y + bbox.height)
    )

    # Save the cropped image to a byte stream
    byte_stream = BytesIO()
    cropped_image.save(byte_stream, format="PNG")
    content = byte_stream.getvalue()

    media_type = "image/PNG"
    base64_image = base64.b64encode(content).decode("utf-8")
    base64_url = f"data:{media_type};base64,{base64_image}"
    return base64_url


def get_content_list(base64_urls: List[str], prompt):
    content = [
            {
                "type": "text",
                "text": prompt,
            }
        ] + [
            {
                "type": "image_url",
                "image_url": {"url": base64_url},
            }
            for base64_url in base64_urls
        ]
    return content

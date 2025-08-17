from fastapi import UploadFile, HTTPException
import base64

from openai import AsyncOpenAI
from dotenv import load_dotenv
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

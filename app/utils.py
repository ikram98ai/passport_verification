from fastapi import UploadFile, HTTPException
import base64


async def get_base64_urls(file: UploadFile) -> str:
    base64_urls = []
    # If UploadFile instances are provided, convert to base64
    try:
        print(f"Processing file: {file.filename}")
        content = await file.read()
        media_type = file.content_type or "image/jpeg"
        base64_image = base64.b64encode(content).decode("utf-8")
        base64_urls.append(f"data:{media_type};base64,{base64_image}")

    except Exception as e:
        print(f"Error processing file {file.filename}: {e}")
        raise HTTPException(400, f"Error processing file {file.filename}: {str(e)}")

    return base64_urls

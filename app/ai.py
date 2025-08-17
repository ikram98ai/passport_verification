from pydantic import BaseModel
from fastapi import UploadFile
from prompts import INFO_EXTRACTION_PROMPT
from utils import get_completion, get_content_list, get_base64, crop_image
import boto3


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
    content = get_content_list(
        [passport_base64], "Extract information from this passport."
    )
    info = await get_completion(
        instruction=INFO_EXTRACTION_PROMPT, content=content, output_type=PassportInfo
    )
    return info

async def verify_passport(capture_img, passport_img):

    rekognition_client = boto3.client('rekognition')

    # Assuming images are in S3
    source_image = await get_base64(capture_img)
    target_image = await get_base64(passport_img)

    response = rekognition_client.compare_faces(
        SourceImage={'Bytes': source_image},
        TargetImage={'Bytes': target_image},
        SimilarityThreshold=90 # Set your desired threshold
    )
    for face_match in response['FaceMatches']:
        similarity = face_match['Similarity']
        bbox = face_match['Face']['BoundingBox']

        print(f"Face matched with {similarity:.2f}% similarity.")
        return similarity, crop_image(passport_img,bbox)
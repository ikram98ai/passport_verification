from pydantic import BaseModel
from .utils import get_completion, get_content_list, crop_image
import boto3
from botocore.exceptions import ClientError


class PassportInfo(BaseModel):
    nationality: str
    full_name: str
    surname: str
    passport_type: str
    date_of_birth: str
    personal_number: str
    gender: str
    expiration_date: str


INFO_EXTRACTION_PROMPT = """Extract all info from the given passport image"""


async def extract_info(passport_base64) -> PassportInfo:
    content = get_content_list(
        [passport_base64], "Extract information from this passport."
    )
    info = await get_completion(
        instruction=INFO_EXTRACTION_PROMPT, content=content, output_type=PassportInfo
    )
    return info


class FaceNotFoundException(Exception):
    pass


async def verify_passport(capture_img, passport_img):
    rekognition_client = boto3.client("rekognition")

    # Assuming images are in S3
    source_image = await capture_img.read()
    target_image = await passport_img.read()

    try:
        response = rekognition_client.compare_faces(
            SourceImage={"Bytes": source_image},
            TargetImage={"Bytes": target_image},
            SimilarityThreshold=90,  # Set your desired threshold
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidParameterException':
            raise ValueError("Could not detect a face in one of the images, or the image format is not supported. Please use a clear, well-lit image.")
        else:
            raise e
            
    print("Response: ", response)
    if response["FaceMatches"]:
        face_match = response["FaceMatches"][0]
        score = face_match["Similarity"]
        bbox = face_match["Face"]["BoundingBox"]
        matched_face = await crop_image(passport_img, bbox)
        return {"confidence_score":score, "detected_face":matched_face, "is_match": True}

    if response["UnmatchedFaces"]:
        face_unmatch = response["UnmatchedFaces"][0]
        score = face_unmatch["Confidence"]
        bbox = face_unmatch['BoundingBox']
        unmatched_face = await crop_image(passport_img, bbox)
        return {"confidence_score":score, "detected_face":unmatched_face, "is_match": False}

    raise FaceNotFoundException("Face is not found")
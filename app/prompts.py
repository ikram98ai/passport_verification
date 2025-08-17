INFO_EXTRACTION_PROMPT = """Extract all info from the given passport image"""

IMAGE_EXTRACTION_PROMPT = """
Identify the photo of the passport holder in the provided passport image. 
Return the bounding box of the face as pixel coordinates in the format:

{
  "x": <int>,
  "y": <int>,
  "width": <int>,
  "height": <int>
}

- Coordinates must be relative to the top-left corner of the image.
- If no face is detected, return null.
"""

PERSON_VERIFICATION_PROMPT = """
Compare the two provided images and determine whether they belong to the same person. 
Return the result in JSON format:

{
  "same_person": true/false,
  "confidence_score": <0.0–1.0>,
  "reasoning": "<short explanation>"
}

- Consider facial features, not background or image quality.
- Be strict: minor differences like hairstyle or lighting should not reduce confidence if the core features match.
"""
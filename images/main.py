from pathlib import Path
import boto3
from mypy_boto3_rekognition.type_defs import (
    CelebrityTypeDef,
    RecognizeCelebritiesResponseTypeDef,
)
from PIL import Image, ImageDraw, ImageFont

def get_client():
    return boto3.client("rekognition")

def get_path(file_name: str) -> Path:
    return Path(__file__).parent / "images" / file_name

def recognize_celebrities(photo: Path) -> RecognizeCelebritiesResponseTypeDef:
    client = get_client()
    try:
        with photo.open("rb") as image:
            return client.recognize_celebrities(Image={"Bytes": image.read()})
    except Exception as e:
        print(f"Error recognizing celebrities in {photo}: {e}")
        return {"CelebrityFaces": []}

def draw_boxes(image_path: Path, output_path: Path, face_details: list[CelebrityTypeDef]):
    try:
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("Ubuntu-R.ttf", 20)
        width, height = image.size

        for face in face_details:
            box = face.get("Face", {}).get("BoundingBox", {})
            left, top = int(box.get("Left", 0) * width), int(box.get("Top", 0) * height)
            right = int((box.get("Left", 0) + box.get("Width", 0)) * width)
            bottom = int((box.get("Top", 0) + box.get("Height", 0)) * height)

            confidence = face.get("MatchConfidence", 0)
            if confidence > 90:
                draw.rectangle([left, top, right, bottom], outline="red", width=3)
                text = face.get("Name", "Unknown")
                bbox = draw.textbbox((left, top - 20), text, font=font)
                draw.rectangle(bbox, fill="red")
                draw.text((left, top - 20), text, font=font, fill="white")
        
        image.save(output_path)
        print(f"Image saved with results at: {output_path}")
    except Exception as e:
        print(f"Error drawing boxes on {image_path}: {e}")

if __name__ == "__main__":
    photo_paths = [
        get_path("bbc.jpg"),
        get_path("msn.jpg"),
        get_path("neymar-torcedores.jpg"),
    ]
    
    for photo_path in photo_paths:
        response = recognize_celebrities(photo_path)
        faces = response.get("CelebrityFaces", [])
        if not faces:
            print(f"No celebrities found in image: {photo_path}")
            continue
        output_path = get_path(f"{photo_path.stem}-resultado.jpg")
        draw_boxes(photo_path, output_path, faces)

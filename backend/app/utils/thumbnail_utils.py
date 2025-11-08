import os
from pdf2image import convert_from_bytes
from fastapi import HTTPException


def generate_thumbnail(stream: bytes, book_data: dict) -> str:
    """
    Generate a thumbnail from the first page of a PDF
    """
    try:
        # Create thumbnails directory if it doesn't exist
        os.makedirs('./thumbnails', exist_ok=True)

        # Convert first page of PDF to image
        image_list = convert_from_bytes(stream, first_page=1, last_page=1, fmt='jpg')
        thumbnail = image_list[0]

        thumbnail_path = f'./thumbnails/{book_data["id"]}.jpg'
        thumbnail.save(thumbnail_path)
        return thumbnail_path
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        raise
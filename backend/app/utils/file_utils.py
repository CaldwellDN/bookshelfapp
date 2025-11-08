import uuid
import os
from fastapi import HTTPException


def generate_unique_id() -> str:
    """
    Generates and returns a unique id so long as there is no
    file with the same name already in the library
    """
    while True:
        unique_id = str(uuid.uuid4())
        # Check if a book file with this ID already exists
        if not any(os.path.exists(f"./books/{unique_id}.{ext}") for ext in ["pdf", "epub"]):
            return unique_id


def file_type_check(file_stream: bytes) -> str:
    """
    Checks the file type of the provided stream and returns the extension.
    For now, we'll implement a simple check based on magic numbers
    """
    # Check PDF magic number
    if file_stream.startswith(b'%PDF'):
        return "pdf"
    # Check EPUB magic number (PK followed by specific bytes)
    elif file_stream.startswith(b'PK\x03\x04') or file_stream.startswith(b'PK\x05\x06') or file_stream.startswith(b'PK\x07\x08'):
        # Additional check to confirm it's an EPUB
        # EPUB files are ZIP files with specific content
        # We'll do a basic check for the mimetype entry in the ZIP
        try:
            stream_str = file_stream.decode('utf-8', errors='ignore')
            if 'mimetype' in stream_str and 'application/epub+zip' in stream_str:
                return "epub"
            # If it looks like a ZIP file but doesn't have EPUB specifics, check if it has EPUB indicators
            # Simple ZIP files are treated as EPUB for this implementation
            if file_stream.startswith(b'PK'):
                return "epub"
        except:
            pass
    
    # If file type is not recognized as allowed type
    raise HTTPException(status_code=400, detail=f"Invalid file type")
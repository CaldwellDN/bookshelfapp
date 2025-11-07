from typing import Dict, Union
from fastapi import FastAPI, UploadFile, HTTPException, Depends 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os
from magic import from_file # This uses libmagic at the moment, but
# I want to make it use something else for less dependency
import shutil
import librarytools
from auth import router as auth_router
from auth import verify_refresh_token, get_current_userID

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/books", StaticFiles(directory="books"), name="books")
app.mount("/thumbnails", StaticFiles(directory="thumbnails"), name="thumbnails")

app.include_router(auth_router, prefix='/auth')

allowed_extensions = ['pdf', 'epub', 'zip']

class BookMetadataUpdate(BaseModel):
    title: str = None
    author: str = None

class BookData(BaseModel):
    id: str
    title: str
    author: Optional[str] = None
    file_type: str
    user_id: int

class BookUploadResponse(BaseModel):
    bookData: BookData
    message: str

@app.get('/')
def main():
    return {"message": "Backend is Running!"}


@app.post("/upload")
async def upload(
    file: UploadFile,
    current_user = Depends(get_current_userID)
) -> BookUploadResponse:
    '''
    Upload a book file and register it in the user's library.
    '''
    # Quick base check for the file type.
    if not any(ext in file.content_type.lower() for ext in allowed_extensions):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    # More thorough file-type check
    sample = await file.read()
    await file.seek(0)  # Reset file pointer after reading
    file_extension = librarytools.file_type_check(sample[:2048])

    # Generate Book Data
    bookData = {
        "id": librarytools.generate_unique_id(),
        "title": file.filename,
        "author": None,
        "file_type": file_extension,
        "user_id": current_user.user_id
    }

    # Generate a Thumbnail
    try:
        thumbnailPath = librarytools.generate_thumbnail(sample, bookData)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Thumbnail creation failed: {e}")

    # Upload the book
    try:
        os.makedirs("./books", exist_ok=True)
        file_location = f"./books/{bookData['id']}.{file_extension}"
        file.file.seek(0)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        librarytools.create_library_entry(bookData)

        response_data = BookUploadResponse(
            bookData=BookData(**bookData),
            message="File uploaded successfully!"
        )
        return response_data

    except Exception as e:
        if os.path.exists(thumbnailPath):
            os.remove(thumbnailPath)
        if os.path.exists(file_location):
            os.remove(file_location)
        librarytools.delete_library_entry(bookData["id"])
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")



@app.get('/library/{user_id}')
def library(user_id : int) -> Dict:
    '''
    Fetch the selected user's library.
    '''
    bookList = librarytools.get_library_list(user_id)
    return {"books": bookList}

# Unused endpoint, remove soon.
@app.get('/books')
def books() -> Dict:
    books = os.listdir('./books')
    book_types = [from_file(f"./books/{book}", mime=True) for book in books]
    bookAndType = zip(books, book_types)
    return {"books": bookAndType}

@app.delete('/delete/{book_id}')
def delete_book(book_id: str) -> Dict:
    deleteBookEntry = librarytools.delete_library_entry(book_id)
    if not deleteBookEntry:
        return {"message": "Error: Book entry could not be removed"}
    deleteBookFile = librarytools.delete_library_file(book_id)
    if not deleteBookFile:
        return {"message": "Error: Book entry could not be removed"}
    return {"message": "Success, book entry and files removed."}

@app.put('/edit/{book_id}')
def edit_book_metadata(book_id: str, data: BookMetadataUpdate):
    # Check if at least one field is provided
    if data.title is None and data.author is None:
        raise HTTPException(status_code=400, detail="Error: At least one field (title or author) must be provided.")
    return librarytools.edit_library_entry(book_id, data.dict(exclude_unset=True))

@app.get("/protected")
def protected_route(current_user: dict = Depends(verify_refresh_token)):
    return {"message": f"Welcome {current_user['username']}."}
from typing import Dict, List, Optional
from app.database.repositories.book_repo import BookRepository
from app.database.models.book import Book
from app.utils.file_utils import generate_unique_id
from app.utils.thumbnail_utils import generate_thumbnail
from app.database.repositories.user_repo import UserRepository
import os
import shutil
from fastapi import HTTPException, UploadFile


class BookService:
    def __init__(self, book_repo: BookRepository, user_repo: UserRepository):
        self.book_repo = book_repo
        self.user_repo = user_repo

    async def upload_book(
        self, 
        file: UploadFile, 
        user_id: int,
        allowed_extensions: List[str] = ['pdf', 'epub', 'zip']
    ) -> Dict:
        """
        Upload a book file and register it in the user's library.
        """
        # Quick base check for the file type
        if not any(ext in file.content_type.lower() for ext in allowed_extensions):
            raise HTTPException(status_code=400, detail="Invalid file type.")

        # More thorough file-type check
        sample = await file.read()
        await file.seek(0)  # Reset file pointer after reading
        # Note: We'll need to implement file type checking in utils
        from app.utils.file_utils import file_type_check
        file_extension = file_type_check(sample[:2048])

        # Generate Book Data
        book_data = {
            "id": generate_unique_id(),
            "title": file.filename,
            "author": None,
            "file_type": file_extension,
            "user_id": user_id
        }

        # Generate a Thumbnail
        try:
            thumbnail_path = generate_thumbnail(sample, book_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Thumbnail creation failed: {e}")

        # Save the book file
        try:
            os.makedirs("./books", exist_ok=True)
            file_location = f"./books/{book_data['id']}.{file_extension}"
            
            file.file.seek(0)
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Create database entry
            book = Book(
                id=book_data["id"],
                title=book_data["title"],
                author=book_data.get("author"),
                file_type=book_data["file_type"],
                user_id=book_data["user_id"]
            )
            
            created_book = self.book_repo.create(book)

            response_data = {
                "bookData": {
                    "id": created_book.id,
                    "title": created_book.title,
                    "author": created_book.author,
                    "file_type": created_book.file_type,
                    "user_id": created_book.user_id
                },
                "message": "File uploaded successfully!"
            }
            return response_data

        except Exception as e:
            # Clean up on error
            if 'thumbnail_path' in locals() and os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
            if 'file_location' in locals() and os.path.exists(file_location):
                os.remove(file_location)
            # Attempt to delete db entry if it was created
            try:
                self.book_repo.delete(book_data["id"])
            except:
                pass  # Ignore error if deletion fails
            raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")

    def get_user_library(self, user_id: int) -> List[Dict]:
        """
        Fetch the selected user's library.
        """
        books = self.book_repo.get_by_user_id(user_id)
        return [
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "file_type": book.file_type,
                "user_id": book.user_id
            }
            for book in books
        ]

    def delete_book(self, book_id: str) -> Dict:
        """
        Delete a book and its associated files.
        """
        # Delete database entry
        deleted_book = self.book_repo.delete(book_id)
        if not deleted_book:
            return {"message": "Error: Book entry could not be removed"}

        # Delete book file and thumbnail
        import glob
        files = glob.glob(f'./books/{book_id}.*')
        thumbnails = glob.glob(f'./thumbnails/{book_id}.*')
        
        flag = True
        for file in files:
            try:
                os.remove(file)
            except:
                print(f"Error deleting book file.")
                flag = False
        for thumbnail in thumbnails:
            try:
                os.remove(thumbnail)
            except:
                print("Error deleting thumbnail.")
                flag = False
                
        if not flag:
            return {"message": "Error: Book entry and files could not be completely removed"}
            
        return {"message": "Success, book entry and files removed."}

    def edit_book_metadata(self, book_id: str, data: Dict) -> Dict:
        """
        Update book metadata in the database.
        """
        editable_columns = ['title', 'author']
        final_data = {key: value for key, value in data.items() if key in editable_columns and value is not None}

        if not final_data:
            return {"message": "No valid fields to update"}

        try:
            # Get existing book to check if it exists
            existing_book = self.book_repo.get_by_id(book_id)
            if not existing_book:
                return {"message": f"Book with ID '{book_id}' not found. No update performed."}

            # Update the book with provided data
            update_data = {}
            if 'title' in final_data:
                update_data['title'] = final_data['title']
            if 'author' in final_data:
                update_data['author'] = final_data['author']

            updated_book = self.book_repo.update(book_id, **update_data)
            
            if updated_book:
                return {"message": "metadata updated successfully"}
            else:
                return {"message": f"Book with ID '{book_id}' not found. No update performed."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
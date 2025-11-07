from typing import Dict, List
import uuid
import os
import sqlite3
import magic
from pdf2image import convert_from_bytes
from fastapi import HTTPException
import glob
import time
from requests import Request

class UserTable:
    def __init__(self):
        self.database = 'library.db'

    def usernameCheck(self, username : str) -> tuple | None:
        try:
            with sqlite3.connect(self.database) as con:
                cursor = con.cursor()
                cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
                return cursor.fetchone()
        except Exception as e:
            raise
        return ()
    
    def addUser(self, username : str, password: str):
        try:
            with sqlite3.connect(self.database) as con:
                cursor = con.cursor()
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                con.commit()
        except Exception as e:
            raise

# Refresh Tokens Table Class
class RTT:
    def __init__(self):
        self.database = 'library.db'
    
    def store_refresh_token(self, jti: str, username: str, expires_at: int):
        try:
            with sqlite3.connect(self.database) as con:
                cursor = con.cursor()
                cursor.execute("INSERT INTO refresh_tokens (jti, username, expires_at, revoked) VALUES (?, ?, ?, ?)", (jti, username, expires_at, 0))
                con.commit()
        except Exception as e:
            raise
    
    def revoke_refresh_token(self, jti: str):
        try:
            with sqlite3.connect(self.database) as con:
                cursor = con.cursor()
                cursor.execute("UPDATE refresh_tokens SET revoked = 1 WHERE jti = ?", (jti,))
                con.commit
        except Exception as e:
            raise
    
    def is_refresh_token_active(self, jti: str) -> bool:
        try:
            with sqlite3.connect(self.database) as con:
                cursor = con.cursor()
                cursor.execute("SELECT revoked, expires_at FROM refresh_tokens WHERE jti = ?", (jti,))
                row = cursor.fetchone()
                if not row:
                    return False
                revoked, expires_at = row
                if revoked:
                    return False
                return int(time.time()) < int(expires_at)
        except Exception as e:
            raise

def generate_unique_id() -> str:
    '''
    Generates and returns a unique id so long as there is no
    PDF with the same name already in the library
    '''
    while True:
        unique_id = str(uuid.uuid4())
        if not os.path.exists(f"./books/{unique_id}.pdf"):
            return unique_id
        
def file_type_check(stream: str) -> str:
    mime_type = magic.from_buffer(stream, mime=True)
    if mime_type not in ["application/pdf", "application/epub+zip"]:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {mime_type}")
    if mime_type == "application/pdf":
        return "pdf"
    elif mime_type == "application/epub+zip":
        return "epub"
    
def generate_thumbnail(stream: str, bookData: Dict) -> str:
    try:
        image_list = convert_from_bytes(stream, first_page=1, last_page=1, fmt='jpg') 
        thumbnail = image_list[0]
        os.makedirs('./thumbnails', exist_ok=True)

        thumbnailPath = f'./thumbnails/{bookData['id']}.jpg'

        thumbnail.save(thumbnailPath)
        return thumbnailPath
    except Exception as e:
        print(f"Error: {e}")
        raise

def create_library_entry(bookData: Dict) -> bool: # NOTE: Use transactions later maybe?
    """
    Creates or updates a library entry for a given book.
    Safely inserts data into the SQLite database.
    """
    print(f"BookData: ", bookData)
    try:
        with sqlite3.connect("library.db") as con:
            cursor = con.cursor()

            # Ensure table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    author TEXT,
                    file_type TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
            """)

            # Insert new book entry
            cursor.execute("""
                INSERT INTO books (id, title, author, file_type, user_id)
                VALUES (?, ?, ?, ?, ?);
            """, (
                bookData["id"],
                bookData["title"],
                bookData.get("author", None),
                bookData["file_type"],
                bookData["user_id"]
            ))

            con.commit()
            return True

    except sqlite3.IntegrityError as e:
        print(f"Error: {e}")
        raise

    except Exception as e:
        print(f"Database error: {e}")
        raise
    
def delete_library_entry(uuid: str) -> bool:
    try:
        with sqlite3.connect('library.db') as con:
            cursor = con.cursor()
            cursor.execute(f"DELETE FROM books WHERE id = '{uuid}';")
            con.commit()
            return True
    except Exception as e:
        print(f'Error: {e}')
        return False
    
def delete_library_file(uuid: str) -> bool:
    flag = True
    files = glob.glob(f'./books/{uuid}.*')
    thumbnails = glob.glob(f'./thumbnails/{uuid}.*')
    for file in files:
        try:
            os.remove(file)
        except:
            print(f"Error deleting file.")
            flag = False
    for thumbnail in thumbnails:
        try:
            os.remove(thumbnail)
        except:
            print("Error deleting thumbnail.")
            flag = False
    return flag
    
def get_library_list(user_id: int) -> List[Dict]:
    keys = ['id', 'title', 'author', 'file_type', "user_id"]
    finalBookList = []
    try:
        with sqlite3.connect('library.db') as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM books WHERE user_id = ?;", (user_id,))
            books = cursor.fetchall()
            for book in books:
                bookDict = dict(zip(keys, book))
                finalBookList.append(bookDict)
    except Exception as e:
        print(f'Error: {e}') 

    return finalBookList

def edit_library_entry(id: str, data: dict):
    editableColumns = ['title', 'author']
    finalData = {key: value for key, value in data.items() if key in editableColumns}

    if not finalData:
        return None

    set_clause = ', '.join([f"{k} = ?" for k in finalData.keys()])
    sqlStatement = f"UPDATE books SET {set_clause} WHERE id = ?"

    values_to_bind = tuple(finalData.values()) + (id,)

    try:
        with sqlite3.connect('library.db') as con:
            cursor = con.cursor()
            cursor.execute(sqlStatement, values_to_bind)
        if cursor.rowcount == 0:
            return {"message": f"Book with ID '{id}' not found. No update performed."}
        con.commit() 
        return {"message": "metadata updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")



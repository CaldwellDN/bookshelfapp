# Bookshelf App Prototype

Work In Progress Self-Hosting Bookshelf App, built with React for the frontend and FastAPI/Python on the Backend.

What works:
- Book upload feature
- Edit metadata tab
- Delete Book button
- Auth (Note: I have not tested authentication that much, what I have seen works at the moment)
- PDF files are the only format currently supported.

Goals:
- Create a more coherent, better looking web interface.
- Pivot from SQLite to a better database solution (SQLAlchemy?)
- Support more file formats (epub, txt, ...)
- Metadata Extraction 
- Refactoring of 'librarytools'
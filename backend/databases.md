This file describes the databases for the library program and just how they work

Currently, this project uses SQLite as a database solution, this should be updated to a more
usable solution such as PostgreSQL at a later point.

The books database is implemented as follows:
    ID - Primary Key, UUID.
    Title - Name of the book
    Author - Author of the Book
    File Type - File Type Of The Book
Note: A user-list of some sort should be added for each book, so as to track who's books are whos

The users database is implemented as follows:
    ID - numeric, sequential
    username - name
    password - hashed password in table

The refresh_tokens database is implemented as follows:
    jwt - uuid-token, primary key
    username - string of the username the token belongs to
    expires_at - unix time value when the token will expire
    revoked - integer/boolean to list if the token has been revoked yet
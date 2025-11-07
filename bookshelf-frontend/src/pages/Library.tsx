import { useEffect, useState } from "react";
import BookCard from "../components/BookCard";
import UploadButton from "../components/UploadButton";
import type { Book } from '../types/book'
import EditMetadataModal from "../components/EditMetadataModal";
import { getIDFromToken } from "../auth";


export default function Library() {
  const [books, setBooks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingBook, setEditingBook] = useState<Book | null>(null);
  const token = localStorage.getItem('access_token');
  const user_id = getIDFromToken(token);

  const fetchBooks = async () => {
    try {
      setLoading(true); // start loading
      const response = await fetch(`http://localhost:8000/library/${user_id}`);
      const data = await response.json();
      setBooks(data.books || []);
    } catch (error) {
      console.error("Error fetching books:", error);
    } finally {
      setLoading(false); // stop loading, even on error
    }
  };

  useEffect(() => {
    fetchBooks();
  }, []);

  const handleDelete = async (id : number) => {
    if (!window.confirm("Are you sure you want to delete this book?")) return;

    try {
        await fetch(`http://localhost:8000/delete/${id}`, { method: "DELETE" });
        fetchBooks();
      } catch (error) {
        console.error("Error deleting book:", error);
      }
  }

  const handleEdit = (book : Book) => {
    setEditingBook(book);
  };

  return (
    <div className="container">
      <div
        style={{
          textAlign: "center",
          color: "gray",
          lineHeight: "0.9",
        }}
      >
        <h1>Your Library</h1>
        <p>All your uploaded books will appear here.</p>
        <div style={{ marginTop: "0.75rem" }}>
            <UploadButton onFileSelected={() => fetchBooks()} />
        </div>
        <hr />
      </div>

      {loading ? (
        <p style={{ textAlign: "center", marginTop: "2rem" }}>Loading...</p>
      ) : (
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "center",
            alignItems: "flex-start",
            gap: "0.1rem",
            marginTop: "2rem",
          }}
        >
          {books.length > 0 ? (
            books.map((book) => <BookCard key={book.id} book={book} onDelete={handleDelete} onEdit={handleEdit} />)
          ) : (
            <p style={{ textAlign: "center", color: "gray" }}>
              No books uploaded yet.
            </p>
          )}
        </div>
      )}
      {editingBook && (
            <EditMetadataModal
                book={editingBook}
                onClose={() => setEditingBook(null)}
                onSave={fetchBooks}
            />
       )}
    </div>
  );
}

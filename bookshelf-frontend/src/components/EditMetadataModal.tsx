import { useState } from "react";
import type { Book } from "../types/book";

interface EditMetadataModalProps {
  book: Book;
  onClose: () => void;
  onSave: () => void; // triggers a refresh in the library after saving
}

export default function EditMetadataModal({ book, onClose, onSave }: EditMetadataModalProps) {
  const [title, setTitle] = useState(book.title);
  const [author, setAuthor] = useState(book.author || "");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const response = await fetch(`http://localhost:8000/edit/${book.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ title, author }),
      });

      if (!response.ok) {
        throw new Error("Failed to update book metadata");
      }

      onSave(); // refresh book list
      onClose(); // close modal
    } catch (error) {
      console.error("Error updating book:", error);
      alert("Failed to update metadata");
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(0, 0, 0, 0.4)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: "#fff",
          padding: "1.5rem",
          borderRadius: "8px",
          width: "320px",
          boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
        }}
        onClick={(e) => e.stopPropagation()} // prevent closing when clicking inside
      >
        <h3>Edit Metadata</h3>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          <label>
            Title:
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              style={{ width: "100%", padding: "0.4rem" }}
            />
          </label>

          <label>
            Author:
            <input
              type="text"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              style={{ width: "100%", padding: "0.4rem" }}
            />
          </label>

          <div style={{ marginTop: "1rem", textAlign: "right" }}>
            <button
              type="button"
              onClick={onClose}
              style={{ marginRight: "0.5rem", padding: "0.4rem 0.8rem" }}
            >
              Cancel
            </button>
            <button type="submit" style={{ padding: "0.4rem 0.8rem" }}>
              Save
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

import type { Book } from '../types/book'
import { Link } from 'react-router-dom'
import { useState } from 'react'

interface BookCardProps {
    book: Book;

    onDelete: (id: number) => Promise<void>;
    onEdit: (book: Book) => void;
}

export default function BookCard({ book, onDelete, onEdit }: BookCardProps) {
    const [showMenu, setShowMenu] = useState(false);

    const toggleMenu = (e: any) => {
        e.preventDefault();
        e.stopPropagation();
        setShowMenu(!showMenu);
    }
    return (
        <Link to={`/reader/${book.id}`} style={{ textDecoration: "none", color: "inherit" }}>
        <div
            style={{
                border: "1px solid #ddd",
                borderRadius: "8px",
                padding: "12px",
                width: "180px", 
                height: "260px",
                textAlign: "center",
                backgroundColor: "#fff",
                boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
                position: "relative",
            }}
        >
        <img src={`http://localhost:8000/thumbnails/${book.id}.jpg`}
            alt={book.title}
            style={{
                  width: "100%",
                  height: "66%",      // fixed consistent height
                  objectFit: "contain", // shows full cover, letterboxed if needed
                  borderRadius: "6px",
                  display: "block",
                  backgroundColor: "#f7f7f7" // optional: fills empty letterbox space
            }}
            onError={(e) => {
                e.currentTarget.src = "/placeholder.png"; // Optional fallback
            }}
        />
        <h3 style={{
                overflow: "hidden",
                whiteSpace: "nowrap",
                textOverflow: "ellipsis",
                height: "2.0em",
                margin: "8px 0 4px 0",
            }}>{book.title}</h3>
        <p style={{
                margin: "0",
            }}>{book.author || "Unknown Author"}</p>
        <button style={{
                position: "absolute",
                bottom: "10px",
                right: "10px",
            }}
            onClick={toggleMenu}
            >⋮
        </button>

        {showMenu && (
            <div style={{
                position: "absolute",
                bottom: "35px",
                right: "10px",
                backgroundColor: "white",
                border: "1px solid #ccc",
                borderRadius: "4px",
                zIndex: "10",
            }}>
                <button onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setShowMenu(false);
                    onEdit(book);
                }}
                style={{
                    display: "block",
                    padding: "8px 12px",
                    width: "100%",
                    background: "none",
                    border: "none",
                    textAlign: "left",
                    cursor: "pointer",
                }}>✎ Edit</button>

                <button onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setShowMenu(false);
                    onDelete(book.id);
                }}
                style={{
                    display: "block",
                    padding: "8px 12px",
                    width: "100%",
                    background: "none",
                    border: "none",
                    textAlign: "left",
                    cursor: "pointer",      
                }}>🗑 Delete</button>
            </div>
        )}

        </div>
        </Link>
    );
}
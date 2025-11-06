import { useState, useEffect } from "react"
import { useParams } from "react-router-dom"
import { Document, Page, pdfjs } from "react-pdf"
import "react-pdf/dist/Page/AnnotationLayer.css"
import "react-pdf/dist/Page/TextLayer.css"

// PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url
).toString()

export default function Reader() {
  const { bookId } = useParams<{ bookId: string }>()
  const [fileUrl, setFileUrl] = useState<string | null>(null)
  const [numPages, setNumPages] = useState<number>(0)
  const [pageNumber, setPageNumber] = useState<number>(1)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!bookId) return

    // Build URL to the file on your backend
    const url = `http://localhost:8000/books/${bookId}.pdf`
    setFileUrl(url)
  }, [bookId])

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages)
    setPageNumber(1)
  }

  const nextPage = () => setPageNumber((p) => Math.min(p + 1, numPages))
  const prevPage = () => setPageNumber((p) => Math.max(p - 1, 1))

  return (
    <div style={{ textAlign: "center", padding: "1rem" }}>
        <div
        style={{
          marginBottom: "1rem",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: "1rem",
        }}
      >
        <button onClick={prevPage} disabled={pageNumber <= 1}>
          ← Previous
        </button>
        <span>
          Page {pageNumber} of {numPages}
        </span>
        <button onClick={nextPage} disabled={pageNumber >= numPages}>
          Next →
        </button>
      </div>
      {fileUrl ? (
        <div style={{ display: "inline-block", border: "1px solid #ccc" }}>
          <Document
            file={fileUrl}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={(err) => {
              console.error(err)
              setError("Failed to load PDF.")
            }}
          >
            <Page pageNumber={pageNumber} width={800} />
          </Document>
        </div>
      ) : (
        <p>Loading PDF...</p>
      )}

      {error && (
        <p style={{ color: "red", marginTop: "1rem" }}>
          {error}
        </p>
      )}

      <div
        style={{
          marginTop: "1rem",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: "1rem",
        }}
      >
        <button onClick={prevPage} disabled={pageNumber <= 1}>
          ← Previous
        </button>
        <span>
          Page {pageNumber} of {numPages}
        </span>
        <button onClick={nextPage} disabled={pageNumber >= numPages}>
          Next →
        </button>
      </div>
    </div>
  )
}

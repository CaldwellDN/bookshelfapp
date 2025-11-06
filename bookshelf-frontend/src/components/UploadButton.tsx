import React, { useState } from "react";
import { fetchAPI } from "../apiClient";

interface UploadButtonProps {
  onFileSelected?: (file: File) => void; // callback so parent can handle the file
}

export default function UploadButton({ onFileSelected }: UploadButtonProps) {
  const [uploading, setUploading] = useState(false); // simple local state for UI

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
  
    setUploading(true);
  
    try {
      const formData = new FormData();
      formData.append("file", file);
  
      const response = await fetchAPI("upload", {
        method: "POST",
        body: formData,
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Upload failed");
      }
  
      const data = await response.json();
      console.log("Upload successful:", data);
  
  
      if (onFileSelected) onFileSelected(file);
  
      alert("File uploaded successfully!");
    } catch (err: any) {
      console.error("Error uploading file:", err);
      alert(`Upload failed: ${err.message}`);
      window.location.reload();
    } finally {
      setUploading(false);
      e.currentTarget.value = "";
    }
  };
 
  return (
    <label
      style={{
        display: "inline-block",
        padding: "0.5rem 0.9rem",
        backgroundColor: "#1f6feb",
        color: "#ffffff",
        borderRadius: 8,
        cursor: uploading ? "not-allowed" : "pointer",
        opacity: uploading ? 0.7 : 1,
        fontSize: 14,
      }}
    >
      {uploading ? "Uploading..." : "Upload Book"}
      <input
        type="file"
        accept=".pdf,.epub"
        onChange={handleFileChange}
        style={{ display: "none" }} // hide default ugly file input
        disabled={uploading}
      />
    </label>
  );
}

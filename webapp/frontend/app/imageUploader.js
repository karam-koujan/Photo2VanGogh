"use client";
import React, { useState } from "react";
import axios from "axios";
import styles from "./page.module.css";

const ImageUploader = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [serverImage, setServerImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    } else {
      alert("Please select an image!");
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert("Please select a file first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        "http://karamkaku.pythonanywhere.com/process-image",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          responseType: "arraybuffer",
        }
      );

      const base64String = Buffer.from(response.data, "binary").toString(
        "base64"
      );
      const dataUrl = `data:image/png;base64,${base64String}`;
      setServerImage(dataUrl);
    } catch (err) {
      console.error(err);
      setError("Failed to upload image");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.transformImg}>
      <div className={styles.uploadContainer}>
        <input type="file" accept="image/jpeg" onChange={handleFileChange} />
        <button
          onClick={handleUpload}
          className={styles.button}
          disabled={loading}
        >
          {loading ? "Transforming..." : "Transform Photo"}
        </button>
      </div>
      <div className={styles.imgContainer}>
        {selectedFile ? (
          <div>
            <h2>Selected Photo:</h2>
            <img
              src={URL.createObjectURL(selectedFile)}
              alt="Selected"
              style={{ maxWidth: "100%" }}
            />
          </div>
        ) : (
          <div className={styles.placeholder}></div>
        )}
        {error && <p style={{ color: "red" }}>{error}</p>}
        {serverImage ? (
          <div>
            <h2>Painting:</h2>
            <img
              src={serverImage}
              alt="painting"
              style={{ maxWidth: "100%" }}
            />
          </div>
        ) : (
          <div className={styles.placeholder}></div>
        )}
      </div>
    </div>
  );
};

export default ImageUploader;

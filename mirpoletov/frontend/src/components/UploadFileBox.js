import { useState, useRef } from "react";
import "./UploadFileBox.css";

const UploadFileBox = ({ onFileUpload, acceptedTypes = "", onWrongFileUpload }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedFileName, setSelectedFileName] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const max_filename_len = 20;
  const ellipsis = "...";

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileSelect = (file) => {
    if (file) {
      const extension = file.name.split(".").pop().toLowerCase();
      const allowedTypes = acceptedTypes.split(",").map(type => type.replace(".", ""));
      
      if (allowedTypes.includes(extension)) {
        if (file.name.length <= max_filename_len)
            setSelectedFileName(file.name);
        else {
            const half_len = Math.floor((max_filename_len - extension.length - 1 - ellipsis.length) / 2);

            const filename = `${file.name.slice(0, half_len)}${ellipsis}${file.name.slice(file.name.length - extension.length - 1 - half_len, file.name.length - extension.length - 1)}.${extension}`;
            setSelectedFileName(filename);
        }
        setSelectedFile(file);

        if (onFileUpload) {
          onFileUpload(file);
        }
      }
      else onWrongFileUpload();
    }
  };

  const handleAreaClick = () => {
    fileInputRef.current?.click();
  };

  const handleInputChange = (e) => {
    const file = e.target.files[0];
    handleFileSelect(file);
  };

  return (
    <div className="file-upload-container">
      <div 
        className={`upload-area ${isDragging ? "dragging" : ""}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleAreaClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={acceptedTypes}
          onChange={handleInputChange}
          style={{ display: "none" }}
        />
        
        {selectedFile ? (
          <p className="file-info">{`${selectedFileName}`}</p>
        ) : (
          <p className="file-info">Загрузить файл</p>
        )}
      </div>
    </div>
  );
};

export default UploadFileBox;
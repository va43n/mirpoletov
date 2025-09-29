import "./ErrorWindow.css";

const ErrorWindow = ({ isOpen, onClose, message }) => {
  const handleBackdropClick = (event) => {
    if (event.target === event.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="error-backdrop" onClick={handleBackdropClick}>
      <div className="error-container">
        <div className="error-header">
          <p className="error-title">Предупреждение</p>
          <button className="error-close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="error-content">
          {message && <p className="error-message">{message}</p>}
        </div>
      </div>
    </div>
  );
};

export default ErrorWindow;
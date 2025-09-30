import "./ModalWindow.css";

const ModalWindow = ({ isOpen, onClose, message, title, style }) => {
  const handleBackdropClick = (event) => {
    if (event.target === event.currentTarget && style === "error") {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={handleBackdropClick}>
      <div className="modal-container">
        <div className={`modal-header ${style}-header`}>
          <p className="modal-title">{title}</p>
          {style === "error" && 
            <button className="modal-close-btn" onClick={onClose}>
              ×
            </button>
          }
        </div>

        <div className="modal-content">
          {message && <p className="modal-message">{message}</p>}
        </div>
      </div>
    </div>
  );
};

export default ModalWindow;
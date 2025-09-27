import { useState, useRef, useEffect } from "react";
import "./ChoiceBox.css";

const ChoicesBox = ({ 
  onSelectionChange,
  data = {},
  title = ""
 }) => {
  const [isChoicesOpen, setIsChoicesOpen] = useState(false);
  const [selectedChoices, setSelectedChoices] = useState([]);
  const dropdownRef = useRef(null);

  const generateOptionsFromDictionary = (dict) => {
    return Object.values(dict).map(item => ({
      id: item.id,
      name: item.name,
      description: item.description
    }));
  };
  const options = generateOptionsFromDictionary(data);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsChoicesOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (onSelectionChange) {
      onSelectionChange(selectedChoices);
    }
  }, [selectedChoices, onSelectionChange]);

  const handleChoiceToggle = (choiceId) => {
    setSelectedChoices(prev => {
      const newSelection = prev.includes(choiceId)
        ? prev.filter(id => id !== choiceId)
        : [...prev, choiceId];
      
      return newSelection;
    });
  };

  const handleDropdownClick = () => {
    setIsChoicesOpen(!isChoicesOpen);
  };

  const getDisplayText = () => {
    if (selectedChoices.length === 0) return title;
    if (selectedChoices.length === 1) {
      const choice = options.find(m => m.id === selectedChoices[0]);
      return choice?.name || title;
    }
    return `Выбрано: ${selectedChoices.length}`;
  };

  return (
    <div className="choices-dropdown-container" ref={dropdownRef}>
      <div 
        className={`choices-dropdown-field ${isChoicesOpen ? "open" : ""}`}
        onClick={handleDropdownClick}
      >
        <span className="choices-display-text">{getDisplayText()}</span>
        <span className={`dropdown-arrow ${isChoicesOpen ? "rotated" : ""}`}>▼</span>
      </div>

      {isChoicesOpen && (
        <div className="choices-dropdown-menu">
          <div className="choices-list">
            {options.map(choice => (
              <div
                key={choice.id}
                className={`choice-item ${selectedChoices.includes(choice.id) ? "selected" : ""}`}
                onClick={() => handleChoiceToggle(choice.id)}
              >
                <div className="choice-checkbox">
                  <div className={`checkbox ${selectedChoices.includes(choice.id) ? "checked" : ""}`}>
                    {selectedChoices.includes(choice.id) && "✓"}
                  </div>
                </div>
                <div className="choice-info">
                  <span className="choice-name">{choice.name}</span>
                  <span className="choice-description">{choice.description}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChoicesBox;
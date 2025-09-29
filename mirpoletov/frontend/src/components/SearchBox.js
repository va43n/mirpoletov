import { useState, useMemo, useRef, useEffect } from "react";
import "./SearchBox.css";

const SearchBox = ({ onRegionSelect, data = {} }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const searchResults = useMemo(() => {
    if (!searchTerm.trim()) return [];
    
    const term = searchTerm.toLowerCase();
    return Object.values(data)
      .filter(region => 
        region.name.toLowerCase().includes(term)
      )
      .slice(0, 5);
  }, [searchTerm]);

  const handleInputChange = (e) => {
    setSearchTerm(e.target.value);
    setIsDropdownOpen(true);
    setSelectedIndex(-1);
  };

  const handleRegionSelect = (region) => {
    setSearchTerm("");
    setIsDropdownOpen(false);
    setSelectedIndex(-1);
    onRegionSelect(region.id);
  };

  const handleKeyDown = (e) => {
    if (!isDropdownOpen) return;
    
    if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex(prev => prev > 0 ? prev - 1 : searchResults.length - 1);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex(prev => 
        prev < searchResults.length - 1 ? prev + 1 : 0
      );
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (selectedIndex >= 0 && searchResults[selectedIndex]) {
        handleRegionSelect(searchResults[selectedIndex]);
      }
    } else if (e.key === "Escape") {
      setIsDropdownOpen(false);
      setSelectedIndex(-1);
    }
  };

  return (
    <div className="search-container" ref={dropdownRef}>
      <div className="search-box">
        <input
          type="text"
          placeholder="Поиск..."
          value={searchTerm}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsDropdownOpen(true)}
          className="search-input"
        />
        
        {isDropdownOpen && searchResults.length > 0 && (
          <div className="dropdown">
            {searchResults.map((region, index) => (
              <div
                key={region.id}
                className={`dropdown-item ${index === selectedIndex ? "selected" : ""}`}
                onClick={() => handleRegionSelect(region)}
                onMouseEnter={() => setSelectedIndex(index)}
              >
                <span className="region-name">{region.name}</span>
              </div>
            ))}
          </div>
        )}
        
        {isDropdownOpen && searchTerm && searchResults.length === 0 && (
          <div className="dropdown">
            <div className="dropdown-item no-results">
              Ничего не найдено
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchBox;
import { useState, useRef, useEffect } from "react";
import "./DateTimePicker.css";

const DateTimePicker = ({ 
  value = "",
  title = "",
  onChange,
  placeholder = "ДД.ММ.ГГГГ ЧЧ:ММ",
  showTime = true
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState(value);
  const containerRef = useRef(null);

  const now = new Date();
  const [selectedDay, setSelectedDay] = useState(now.getDate());
  const [selectedMonth, setSelectedMonth] = useState(now.getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(now.getFullYear());
  const [selectedHour, setSelectedHour] = useState(now.getHours());
  const [selectedMinute, setSelectedMinute] = useState(now.getMinutes());

  const years = Array.from({
    length: Math.ceil((now.getFullYear() + 1 - 2020) / 1)
  }, (_, i) => 2020 + i * 1);
  const monthNames = [
      "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
      "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
  ];

  const getDaysInMonth = (month, year) => {
    return new Date(year, month, 0).getDate();
  };

  useEffect(() => {
    const daysInMonth = getDaysInMonth(selectedMonth, selectedYear);

    if (selectedDay > daysInMonth) {
      setSelectedDay(daysInMonth);
    }
    else {
      setSelectedDay(selectedDay);
    }
  }, [selectedMonth, selectedYear]);

  useEffect(() => {
    const day = selectedDay < 10 ? `0${selectedDay}` : `${selectedDay}`;
    const month = selectedMonth < 10 ? `0${selectedMonth}` : `${selectedMonth}`;
    const hour = selectedHour < 10 ? `0${selectedHour}` : `${selectedHour}`;
    const minute = selectedMinute < 10 ? `0${selectedMinute}` : `${selectedMinute}`;
    const input = `${day}.${month}.${selectedYear} ${hour}:${minute}`;
    setInputValue(input);
    onChange?.(input);
  }, [selectedDay, selectedMonth, selectedYear, selectedHour, selectedMinute]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const changeDay = (increment) => {
    setSelectedDay(prev => {
      const daysInMonth = getDaysInMonth(selectedMonth, selectedYear);
      let newDay = prev + increment;
      if (newDay > daysInMonth) newDay = 1;
      if (newDay < 1) newDay = daysInMonth;
      return newDay;
    });
  };

  const changeMonth = (increment) => {
    setSelectedMonth(prev => {
      let newMonth = prev + increment;
      if (newMonth > 12) newMonth = 1;
      if (newMonth < 1) newMonth = 12;
      return newMonth;
    });
  };

  const changeYear = (increment) => {
    setSelectedYear(prev => {
      const currentIndex = years.indexOf(prev);
      let newIndex = currentIndex + increment;
      if (newIndex >= years.length) newIndex = 0;
      if (newIndex < 0) newIndex = years.length - 1;
      return years[newIndex];
    });
  };

  const changeHour = (increment) => {
    setSelectedHour(prev => {
      let newHour = prev + increment;
      if (newHour > 23) newHour = 0;
      if (newHour < 0) newHour = 23;
      return newHour;
    });
  };

  const changeMinute = (increment) => {
    setSelectedMinute(prev => {
      let newMinute = prev + increment;
      if (newMinute > 59) newMinute = 0;
      if (newMinute < 0) newMinute = 59;
      return newMinute;
    });
  };

  const handleWheel = (e, changeFunction) => {
    const increment = e.deltaY > 0 ? -1 : 1;
    changeFunction(increment);
  };

  const getMonthName = (month) => {
    return monthNames[month - 1];
  };

  return (
    <div className="datetime-picker-container" ref={containerRef}>
      <p className="input-title">{title}</p>
      <div className="datetime-input-wrapper">
        <p
          type="text"
          className="datetime-input"
          onClick={() => setIsOpen(true)}
        >{inputValue}</p>
      </div>

      {isOpen && (
        <div className="datetime-dropdown">
          <div className="date-picker-section">
            <p className="choose-title">Выберите дату:</p>
            <div className="cyclic-selectors">
              <div 
                className="cyclic-col"
                onWheel={(e) => handleWheel(e, changeDay)}
              >
                <div className="cyclic-label">День</div>
                <button 
                  className="cyclic-btn up"
                  onClick={() => changeDay(1)}
                >
                  ▲
                </button>
                <div className="cyclic-value">
                  {String(selectedDay).padStart(2, "0")}
                </div>
                <button 
                  className="cyclic-btn down"
                  onClick={() => changeDay(-1)}
                >
                  ▼
                </button>
              </div>

              <div 
                className="cyclic-col"
                onWheel={(e) => handleWheel(e, changeMonth)}
              >
                <div className="cyclic-label">Месяц</div>
                <button 
                  className="cyclic-btn up"
                  onClick={() => changeMonth(1)}
                >
                  ▲
                </button>
                <div className="cyclic-value">
                  {getMonthName(selectedMonth)}
                </div>
                <button 
                  className="cyclic-btn down"
                  onClick={() => changeMonth(-1)}
                >
                  ▼
                </button>
              </div>

              <div 
                className="cyclic-col"
                onWheel={(e) => handleWheel(e, changeYear)}
              >
                <div className="cyclic-label">Год</div>
                <button 
                  className="cyclic-btn up"
                  onClick={() => changeYear(1)}
                >
                  ▲
                </button>
                <div className="cyclic-value">
                  {selectedYear}
                </div>
                <button 
                  className="cyclic-btn down"
                  onClick={() => changeYear(-1)}
                >
                  ▼
                </button>
              </div>
            </div>
          </div>

          {showTime && (
            <div className="time-picker-section">
              <p className="choose-title">Выберите время:</p>
              <div className="cyclic-selectors">
                <div 
                  className="cyclic-col"
                  onWheel={(e) => handleWheel(e, changeHour)}
                >
                  <div className="cyclic-label">Часы</div>
                  <button 
                    className="cyclic-btn up"
                    onClick={() => changeHour(1)}
                  >
                    ▲
                  </button>
                  <div className="cyclic-value">
                    {String(selectedHour).padStart(2, "0")}
                  </div>
                  <button 
                    className="cyclic-btn down"
                    onClick={() => changeHour(-1)}
                  >
                    ▼
                  </button>
                </div>

                <div 
                  className="cyclic-col"
                  onWheel={(e) => handleWheel(e, changeMinute)}
                >
                  <div className="cyclic-label">Минуты</div>
                  <button 
                    className="cyclic-btn up"
                    onClick={() => changeMinute(1)}
                  >
                    ▲
                  </button>
                  <div className="cyclic-value">
                    {String(selectedMinute).padStart(2, "0")}
                  </div>
                  <button 
                    className="cyclic-btn down"
                    onClick={() => changeMinute(-1)}
                  >
                    ▼
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DateTimePicker;
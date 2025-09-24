import React, { useState } from 'react';
import './App.css';

function App() {
  const [serverResponse, setServerResponse] = useState('');

  const handleClick = async () => {
    try {
      const response = await fetch('https://mirpoletov.ru:8000/api/button-click');
      const data = await response.json();
      setServerResponse(data.response);
    } catch (error) {
      console.error('Ошибка при запросе к серверу:', error);
      setServerResponse('Не удалось получить ответ от сервера.');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Мое React-приложение</h1>
        <button onClick={handleClick}>Нажми на меня</button>
        {serverResponse && <p>Ответ сервера: <strong>{serverResponse}</strong></p>}
      </header>
    </div>
  );
}

export default App;

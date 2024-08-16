"use client";

import styles from "./page.module.css";
import { useEffect, useState } from "react";

export default function Home() {
  const [initialState, setState] = useState([]);
  const [parseResponse, setParseResponse] = useState(null);
  const [prompt, setPrompt] = useState('badminton racket');
  const [loading, setLoading] = useState(false);
  const url = "/test";
  
  useEffect(() => {
    fetch(url).then(response => {
      if (response.status === 200) {
        return response.json();
      }
    }).then(data => setState(data));
  }, []);

  const handleParseClick = () => {
    setLoading(true);
    fetch('/parse?' + new URLSearchParams({ prompt }).toString())
      .then(response => {
        if (response.status === 200) {
          return response.json();
        }
      })
      .then(data => {
        setParseResponse(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error:', error);
        setLoading(false);
      });
  };

  return (
    <main className={styles.main}>
      <div className={styles.description}>
        <h1 className={styles.title}>One Stop Shop</h1>
        <div className={styles.inputContainer}>
          <input 
            type="text" 
            value={prompt} 
            onChange={(e) => setPrompt(e.target.value)} 
            placeholder="Enter your product here..."
            className={styles.promptInput}
          />
          <button 
            onClick={handleParseClick} 
            className={`${styles.parseButton} ${loading ? styles.hiddenButton : ''}`}
            disabled={loading}
          >Parse</button>
        </div>
        {loading && (
          <div>Loading...
            <div className={styles.loader}></div>
          </div>
          )}
        
        {parseResponse && (
          <div className={styles.responseContainer}>
            <h2 className={styles.responseTitle}>Parse Response</h2>
            <pre className={styles.responseText}>{JSON.stringify(parseResponse, null, 2)}</pre>
          </div>
        )}
      </div>
    </main>
  );
}

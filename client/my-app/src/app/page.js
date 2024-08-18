"use client";

import styles from "./page.module.css";
import { useEffect, useState } from "react";

export default function Home() {
  const [initialState, setState] = useState([]);
  const [parseResponse, setParseResponse] = useState(null);
  const [prompt, setPrompt] = useState('');
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
          >Research!</button>
        </div>
        {loading && (
          <div>Researching...
            <div className={styles.loader}></div>
          </div>
        )}
        
        {parseResponse && (
          <div className={styles.responseContainer}>
            <h2 className={styles.responseTitle}>Products</h2>
            <div className={styles.productList}>
              {parseResponse.products.map((product, index) => (
                <div key={index} className={styles.productCard}>
                  <h3 className={styles.productName}>{product['product-name']}</h3>
                  <p className={styles.productRating}>Rating: {product['product-rating']}</p>
                  <p className={styles.productHighlights}>{product.highlights}</p>
                  <p className={styles.productReview}>{product['product-review']}</p>
                  <div className={styles.reviewLinks}>
                    {product.reviewers.map((reviewer, i) => (
                      <a key={i} href={reviewer} target="_blank" rel="noopener noreferrer" className={styles.reviewLink}>
                        Review {i + 1}
                      </a>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

"use client";

import Image from "next/image";
import styles from "./page.module.css";
import { useEffect, useState } from "react";
import { Channel } from "../Components/Channel";

export default function Home() {
  const [initialState, setState] = useState([]);
  const [parseResponse, setParseResponse] = useState(null); // State to handle the parse response
  const url = "/test";
  
  useEffect(() => {
    fetch(url).then(response => {
      console.log(url);
      if (response.status === 200) {
        return response.json();
      }
    }).then(data => setState(data));
  }, []);

  const handleParseClick = () => {
    fetch('/parse?'+ new URLSearchParams({
      prompt: 'badminton racket',
  }).toString())
      .then(response => {
        if (response.status === 200) {
          return response.json();
        }
      })
      .then(data => setParseResponse(data)) // Set the response data to state
      .catch(error => console.error('Error:', error));
  };

  return (
    <main className={styles.main}>
      <div className={styles.description}>
        <h1>Channels 5</h1>
        <Channel data={initialState} />
        <button onClick={handleParseClick}>Parse</button> {/* Button to call the /parse endpoint */}
        {parseResponse && <div>{JSON.stringify(parseResponse)}</div>} {/* Display parse response if available */}
      </div>
    </main>
  );
}

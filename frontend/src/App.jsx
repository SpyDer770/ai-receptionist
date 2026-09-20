import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [status, setStatus] = useState("Checking...");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/health")
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "ok") {
          setStatus("Connected");
        } else {
          setStatus("Unexpected response");
        }
      })
      .catch(() => setStatus("Disconnected"));
  }, []);

  return (
    <div className="app">
      <h1>AI Receptionist</h1>
      <p>Backend Status: {status}</p>
    </div>
  );
}

export default App;
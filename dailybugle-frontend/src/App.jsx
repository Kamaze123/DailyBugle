import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import DigestPage from "./pages/DigestPage";
import ChatPage from "./pages/ChatPage";

export default function App() {
  const [chatHistory, setChatHistory] = useState([]);

  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<DigestPage />} />
        <Route path="/chat" element={
          <ChatPage chatHistory={chatHistory} setChatHistory={setChatHistory} />
        } />
      </Routes>
    </BrowserRouter>
  );
}
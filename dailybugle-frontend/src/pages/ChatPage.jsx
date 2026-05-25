import { useState, useRef, useEffect } from "react";
import { askQuestion } from "../api";
import "./ChatPage.css";

const SUGGESTIONS = [
  "What happened in tech today?",
  "Any major sports results?",
  "What's the latest in business?",
  "Top stories right now?",
];

function TypingIndicator() {
  return (
    <div className="message assistant">
      <div className="avatar">DB</div>
      <div className="bubble typing">
        <span /><span /><span />
      </div>
    </div>
  );
}

function Message({ msg }) {
  const isUser = msg.role === "user";
  return (
    <div className={`message ${msg.role} ${msg.noResult ? "no-result" : ""}`}>
      {!isUser && <div className="avatar">DB</div>}
      <div className="bubble-wrap">
        <div className="bubble">{msg.content}</div>
        {msg.sources && msg.sources.length > 0 && (
          <div className="sources">
            {msg.sources.map((s, i) => (
              <span key={i} className="source-pill">{s}</span>
            ))}
          </div>
        )}
        <span className="timestamp">{msg.time}</span>
      </div>
    </div>
  );
}

export default function ChatPage() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hey! Ask me anything about today's news. I'll search through the latest articles and give you a grounded answer.",
      time: now(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  function now() {
    return new Date().toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
    });
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async (text) => {
    const question = text || input.trim();
    if (!question || loading) return;

    setInput("");
    setMessages((prev) => [
      ...prev,
      { role: "user", content: question, time: now() },
    ]);
    setLoading(true);

    try {
      const res = await askQuestion(question);
      const noResult = res.answer.toLowerCase().includes("don't have recent news");
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.answer,
          sources: res.sources,
          time: now(),
          noResult,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Something went wrong. Make sure the backend is running.",
          time: now(),
          noResult: true,
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="chat-page">
      <div className="chat-header">
        <div className="chat-header-avatar">DB</div>
        <div>
          <p className="chat-header-name">Daily Bugle</p>
          <p className="chat-header-status">
            <span className="status-dot" />
            Answering from today's news
          </p>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((msg, i) => (
          <Message key={i} msg={msg} />
        ))}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {messages.length === 1 && (
        <div className="suggestions">
          {SUGGESTIONS.map((s, i) => (
            <button key={i} className="suggestion-pill" onClick={() => send(s)}>
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="chat-input-wrap">
        <div className="chat-input-inner">
          <textarea
            ref={inputRef}
            className="chat-input"
            rows={1}
            placeholder="Ask about today's news..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
          />
          <button
            className={`send-btn ${loading ? "loading" : ""} ${input.trim() ? "active" : ""}`}
            onClick={() => send()}
            disabled={loading || !input.trim()}
            aria-label="Send"
          >
            ↑
          </button>
        </div>
        <p className="chat-hint">Press Enter to send · Shift+Enter for new line</p>
      </div>
    </div>
  );
}
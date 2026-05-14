"use client";
import { useState, useRef, useEffect } from "react";

type Message = {
  role: "user" | "rabbi";
  content: string;
  sources?: string[];
};

const suggestions = [
  "Is it okay to be angry?",
  "How should I treat someone who wronged me?",
  "What does Judaism say about money?",
  "How do I find purpose in life?",
];

export default function RabbiChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [started, setStarted] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  function resetConversation() {
    setMessages([]);
    setStarted(false);
    setInput("");
}

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

async function sendMessage(question?: string) {
    const q = question || input.trim();
    if (!q || loading) return;
    setInput("");
    setStarted(true);

    const currentMessages = [...messages];
    setMessages((prev) => [...prev, { role: "user" as const, content: q }]);
    setLoading(true);

    // Build history from ALL prior pairs
    const history: { user: string; rabbi: string }[] = [];
    for (let i = 0; i < currentMessages.length; i++) {
      if (
        currentMessages[i]?.role === "user" &&
        currentMessages[i + 1]?.role === "rabbi"
      ) {
        history.push({
          user: currentMessages[i].content,
          rabbi: currentMessages[i + 1].content,
        });
        i++; // skip the rabbi message we just paired
      }
    }

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q, history }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "rabbi", content: data.answer, sources: data.sources },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "rabbi", content: "Something went wrong. Try again." },
      ]);
    }
    setLoading(false);
  }

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
          background: #faf8f5;
          font-family: 'DM Sans', sans-serif;
        }

        .container {
          max-width: 680px;
          margin: 0 auto;
          height: 100vh;
          display: flex;
          flex-direction: column;
        }

        .header {
          padding: 32px 24px 0;
          text-align: center;
        }

        .logo {
          font-family: 'DM Serif Display', serif;
          font-size: 28px;
          color: #1a1a1a;
          letter-spacing: -0.02em;
        }

        .logo span {
          font-style: italic;
          color: #b85c2a;
        }

        .tagline {
          font-size: 14px;
          color: #999;
          margin-top: 4px;
          font-weight: 300;
          letter-spacing: 0.02em;
        }

        .divider {
          width: 32px;
          height: 1px;
          background: #e0d9d0;
          margin: 16px auto 0;
        }

        .landing {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 0 24px 80px;
          gap: 32px;
        }

        .landing-headline {
          font-family: 'DM Serif Display', serif;
          font-size: clamp(32px, 6vw, 48px);
          color: #1a1a1a;
          text-align: center;
          line-height: 1.15;
          letter-spacing: -0.02em;
        }

        .landing-headline em {
          font-style: italic;
          color: #b85c2a;
        }

        .suggestions {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          justify-content: center;
          max-width: 500px;
        }

        .suggestion-btn {
          background: white;
          border: 1px solid #e8e2d9;
          color: #555;
          padding: 8px 16px;
          border-radius: 999px;
          font-size: 13px;
          cursor: pointer;
          font-family: 'DM Sans', sans-serif;
          font-weight: 400;
          transition: all 0.15s ease;
        }

        .suggestion-btn:hover {
          border-color: #b85c2a;
          color: #b85c2a;
          background: #fff8f5;
        }

        .messages {
          flex: 1;
          overflow-y: auto;
          padding: 24px 24px 0;
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .message-row {
          display: flex;
          flex-direction: column;
        }

        .message-row.user {
          align-items: flex-end;
        }

        .message-row.rabbi {
          align-items: flex-start;
        }

        .sender {
          font-size: 11px;
          font-weight: 500;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          margin-bottom: 6px;
          color: #aaa;
        }

        .bubble {
          max-width: 88%;
          padding: 14px 18px;
          border-radius: 18px;
          font-size: 14px;
          line-height: 1.75;
          font-weight: 300;
        }

        .bubble.user {
          background: #1a1a1a;
          color: #faf8f5;
          border-bottom-right-radius: 4px;
        }

        .bubble.rabbi {
          background: white;
          color: #2a2a2a;
          border: 1px solid #ede8e0;
          border-bottom-left-radius: 4px;
        }

        .sources {
          font-size: 11px;
          color: #b85c2a;
          margin-top: 8px;
          letter-spacing: 0.03em;
        }

        .thinking {
          background: white;
          border: 1px solid #ede8e0;
          border-bottom-left-radius: 4px;
          padding: 14px 18px;
          border-radius: 18px;
          display: flex;
          gap: 4px;
          align-items: center;
          width: fit-content;
        }

        .dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #ccc;
          animation: bounce 1.2s infinite;
        }

        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }

        @keyframes bounce {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-6px); background: #b85c2a; }
        }

        .input-area {
          padding: 16px 24px 28px;
        }

        .input-row {
          display: flex;
          gap: 10px;
          background: white;
          border: 1px solid #e0d9d0;
          border-radius: 16px;
          padding: 8px 8px 8px 18px;
          transition: border-color 0.15s;
        }

        .input-row:focus-within {
          border-color: #b85c2a;
        }

        input {
          flex: 1;
          border: none;
          outline: none;
          background: transparent;
          font-family: 'DM Sans', sans-serif;
          font-size: 14px;
          font-weight: 300;
          color: #1a1a1a;
        }

        input::placeholder { color: #bbb; }

        .send-btn {
          background: #1a1a1a;
          color: white;
          border: none;
          border-radius: 10px;
          padding: 10px 20px;
          font-family: 'DM Sans', sans-serif;
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.15s;
          white-space: nowrap;
        }

        .send-btn:hover { background: #b85c2a; }
        .send-btn:disabled { opacity: 0.35; cursor: default; background: #1a1a1a; }
      `}</style>

      <div className="container">
        <div className="header">
 <div className="logo">Ask <span>Rabbi Mikey</span></div>
<div className="tagline">Real answers from Mike's Jewish wisdom</div>
  {started && (
    <button onClick={resetConversation} style={{
      marginTop: "10px",
      background: "none",
      border: "1px solid #e0d9d0",
      borderRadius: "999px",
      padding: "5px 14px",
      fontSize: "12px",
      color: "#999",
      cursor: "pointer",
      fontFamily: "'DM Sans', sans-serif",
    }}>
      + New conversation
    </button>
  )}
  <div className="divider" />
</div>

        {!started ? (
          <div className="landing">
            <div className="landing-headline">
              Got a question?<br /><em>Just ask.</em>
            </div>
            <div className="suggestions">
              {suggestions.map((s) => (
                <button key={s} className="suggestion-btn" onClick={() => sendMessage(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="messages">
            {messages.map((m, i) => (
              <div key={i} className={`message-row ${m.role}`}>
                <div className="sender">{m.role === "user" ? "You" : "Rabbi Mikey"}</div>
                <div className={`bubble ${m.role}`}>{m.content}</div>
                {m.sources && m.sources.length > 0 && (
                  <div className="sources">📖 {m.sources.join(", ")}</div>
                )}
              </div>
            ))}
            {loading && (
              <div className="message-row rabbi">
                <div className="sender">Rabbi Mikey</div>
                <div className="thinking">
                  <div className="dot" />
                  <div className="dot" />
                  <div className="dot" />
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}

        <div className="input-area">
          <div className="input-row">
            <input
              placeholder="Ask anything..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              disabled={loading}
            />
            <button
              className="send-btn"
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
            >
              Ask
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
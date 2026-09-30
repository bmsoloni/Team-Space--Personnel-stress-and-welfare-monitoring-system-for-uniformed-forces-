import { useState, useRef, useEffect } from "react";
import { chatApi } from "../api/ragApi";
import { v4 as uuidv4 } from "uuid";
import { Send, Bot, User, AlertCircle, WifiOff } from "lucide-react";
import LoadingSpinner from "../components/common/LoadingSpinner";

const SUGGESTIONS = [
  "What leave entitlements apply to counter-terror zone personnel?",
  "What is the protocol for suicidal ideation reports?",
  "How many consecutive duty days are allowed before mandatory rest?",
  "What counseling services are available for field-deployed personnel?",
];

// Detect if an answer string is actually an error/warning from the LLM layer
const isLlmError = (text) =>
  text &&
  (text.startsWith("The AI model") ||
    text.startsWith("AI model error") ||
    text.startsWith("Gemini API key") ||
    text.startsWith("[Gemini Error") ||
    text.startsWith("[LLM Error"));

export default function WelfareChatbotPage() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I'm the Personnel Wellness AI Advisor. I can answer questions about welfare policies, SOPs, and protocols. All responses are grounded in official documentation. How can I help you today?",
      sources: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [networkError, setNetworkError] = useState(false);
  const [sessionId] = useState(uuidv4());
  const bottomRef = useRef();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (question) => {
    const q = question || input.trim();
    if (!q) return;
    setMessages((m) => [...m, { role: "user", content: q }]);
    setInput("");
    setLoading(true);
    setNetworkError(false);
    try {
      const res = await chatApi({ question: q, session_id: sessionId });
      const answer = res.data.answer;
      const hasError = isLlmError(answer);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: answer,
          sources: res.data.sources || [],
          isError: hasError,
        },
      ]);
    } catch (err) {
      const isSessionExpired = err.message === "Session expired";
      const isNetwork =
        !isSessionExpired &&
        (!err.response ||
          err.code === "ECONNABORTED" ||
          err.message === "Network Error");
      if (isSessionExpired) {
        // Interceptor already redirected to /login, nothing to show
      } else if (isNetwork) {
        setNetworkError(true);
        setMessages((m) => [
          ...m,
          {
            role: "assistant",
            content:
              "Cannot reach the server. Please ensure the backend is running and try again.",
            sources: [],
            isError: true,
          },
        ]);
      } else if (err.response?.status === 403) {
        setMessages((m) => [
          ...m,
          {
            role: "assistant",
            content:
              "Access denied. You don't have permission to use the AI Advisor. Please contact your administrator.",
            sources: [],
            isError: true,
          },
        ]);
      } else {
        setMessages((m) => [
          ...m,
          {
            role: "assistant",
            content:
              "Sorry, I couldn't process your request. Please try again.",
            sources: [],
            isError: true,
          },
        ]);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>🤖 AI Welfare Advisor</h1>
          <div className="breadcrumb">
            Answers grounded in official welfare documentation
          </div>
        </div>
        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          {networkError && (
            <div
              style={{
                padding: "6px 14px",
                background: "rgba(239,68,68,0.1)",
                border: "1px solid rgba(239,68,68,0.3)",
                borderRadius: "20px",
                fontSize: "12px",
                color: "#ef4444",
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <WifiOff size={12} /> Backend Offline
            </div>
          )}
          <div
            style={{
              padding: "6px 14px",
              background: "rgba(16,185,129,0.1)",
              border: "1px solid rgba(16,185,129,0.2)",
              borderRadius: "20px",
              fontSize: "12px",
              color: "var(--accent-green)",
            }}
          >
            🔒 Privacy Protected
          </div>
        </div>
      </div>

      <div style={{ display: "flex", gap: "20px", height: "calc(100vh - 220px)" }}>
        <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          <div
            className="card"
            style={{
              flex: 1,
              padding: 0,
              display: "flex",
              flexDirection: "column",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                flex: 1,
                overflowY: "auto",
                padding: "20px",
                display: "flex",
                flexDirection: "column",
                gap: "16px",
              }}
            >
              {messages.map((msg, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    gap: "12px",
                    alignItems: "flex-start",
                    flexDirection: msg.role === "user" ? "row-reverse" : "row",
                  }}
                >
                  <div
                    style={{
                      width: "32px",
                      height: "32px",
                      borderRadius: "50%",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      flexShrink: 0,
                      background:
                        msg.role === "user"
                          ? "var(--accent-blue)"
                          : msg.isError
                          ? "rgba(239,68,68,0.15)"
                          : "var(--bg-secondary)",
                      border: `1px solid ${
                        msg.isError
                          ? "rgba(239,68,68,0.4)"
                          : "var(--border)"
                      }`,
                    }}
                  >
                    {msg.role === "user" ? (
                      <User size={16} />
                    ) : msg.isError ? (
                      <AlertCircle size={16} color="#ef4444" />
                    ) : (
                      <Bot size={16} color="var(--accent-cyan)" />
                    )}
                  </div>
                  <div style={{ maxWidth: "75%" }}>
                    <div
                      className={`chat-bubble ${msg.role}`}
                      style={
                        msg.isError && msg.role === "assistant"
                          ? {
                              background: "rgba(239,68,68,0.08)",
                              border: "1px solid rgba(239,68,68,0.25)",
                              color: "#fca5a5",
                            }
                          : {}
                      }
                    >
                      {msg.content}
                    </div>
                    {msg.sources?.length > 0 && (
                      <div
                        style={{
                          marginTop: "8px",
                          display: "flex",
                          flexWrap: "wrap",
                          gap: "4px",
                        }}
                      >
                        {msg.sources.map((s, j) => (
                          <span
                            key={j}
                            className="source-chip"
                            title={s.chunk_preview}
                          >
                            📄 {s.document} p.{s.page}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div
                  style={{ display: "flex", gap: "12px", alignItems: "center" }}
                >
                  <div
                    style={{
                      width: "32px",
                      height: "32px",
                      borderRadius: "50%",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      background: "var(--bg-secondary)",
                      border: "1px solid var(--border)",
                    }}
                  >
                    <Bot size={16} color="var(--accent-cyan)" />
                  </div>
                  <div
                    style={{
                      padding: "12px 16px",
                      background: "var(--bg-card)",
                      border: "1px solid var(--border)",
                      borderRadius: "16px 16px 16px 4px",
                    }}
                  >
                    <LoadingSpinner center={false} />
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
            <div
              style={{
                padding: "16px",
                borderTop: "1px solid var(--border)",
                display: "flex",
                gap: "12px",
              }}
            >
              <input
                className="chat-input form-input"
                placeholder="Ask about welfare policies, SOPs, protocols..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) =>
                  e.key === "Enter" && !e.shiftKey && send()
                }
              />
              <button
                className="btn btn-primary"
                onClick={() => send()}
                disabled={loading || !input.trim()}
              >
                <Send size={16} />
              </button>
            </div>
          </div>
        </div>

        {/* Suggestions sidebar */}
        <div style={{ width: "280px", flexShrink: 0 }}>
          <div className="card">
            <h4
              style={{
                fontSize: "13px",
                fontWeight: "600",
                marginBottom: "12px",
                color: "var(--text-secondary)",
              }}
            >
              💡 Suggested Questions
            </h4>
            {SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                onClick={() => send(s)}
                style={{
                  width: "100%",
                  textAlign: "left",
                  padding: "10px",
                  background: "var(--bg-secondary)",
                  border: "1px solid var(--border)",
                  borderRadius: "8px",
                  color: "var(--text-secondary)",
                  fontSize: "12px",
                  lineHeight: "1.5",
                  cursor: "pointer",
                  marginBottom: "8px",
                  transition: "var(--transition)",
                }}
                onMouseEnter={(e) =>
                  (e.target.style.borderColor = "var(--accent-blue)")
                }
                onMouseLeave={(e) =>
                  (e.target.style.borderColor = "var(--border)")
                }
              >
                {s}
              </button>
            ))}
          </div>
          <div className="card" style={{ marginTop: "16px" }}>
            <h4
              style={{
                fontSize: "13px",
                fontWeight: "600",
                marginBottom: "8px",
                color: "var(--text-secondary)",
              }}
            >
              ⚙️ AI Backend
            </h4>
            <p
              style={{
                fontSize: "11px",
                color: "var(--text-muted)",
                lineHeight: "1.6",
              }}
            >
              The AI Advisor uses <strong>Ollama</strong> (local LLM) by
              default. To use <strong>Google Gemini</strong>, set{" "}
              <code>USE_GEMINI=true</code> and add your{" "}
              <code>GEMINI_API_KEY</code> in the backend <code>.env</code> file.
            </p>
          </div>
          <div className="card" style={{ marginTop: "16px" }}>
            <h4
              style={{
                fontSize: "13px",
                fontWeight: "600",
                marginBottom: "8px",
                color: "var(--text-secondary)",
              }}
            >
              🔒 Privacy Notice
            </h4>
            <p
              style={{
                fontSize: "11px",
                color: "var(--text-muted)",
                lineHeight: "1.6",
              }}
            >
              This AI advisor processes only official documentation. No personal
              personnel data is shared with the AI model. All responses are
              grounded in official welfare guidelines and SOPs.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

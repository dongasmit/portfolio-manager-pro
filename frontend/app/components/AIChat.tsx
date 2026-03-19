"use client";

import { useState, useRef, useEffect } from "react";
import { api, AgentResponse } from "../lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  actions?: Record<string, unknown>[];
  context?: string[];
}

interface AIChatProps {
  clientId?: string;
}

export default function AIChat({ clientId }: AIChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "I'm your AI Portfolio Assistant. I can help you with:\n\n" +
        "- **Portfolio queries:** \"Show me John's portfolio\"\n" +
        "- **Rebalancing:** \"Rebalance to 60% equity / 40% debt\"\n" +
        "- **Risk analysis:** \"Analyze portfolio risk\"\n" +
        "- **Compliance:** \"What do SEBI guidelines say about concentration?\"\n" +
        "- **Market updates:** \"Refresh market prices\"",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const response = await api.chatWithAgent(userMessage, clientId);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.response,
          actions: response.actions_taken,
          context: response.context_used,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Make sure the backend server is running on port 8000.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-[var(--accent)] rounded-full flex items-center justify-center text-white shadow-lg hover:bg-[var(--accent-light)] transition-colors z-50 pulse-glow"
      >
        {isOpen ? (
          <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        ) : (
          <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        )}
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-[420px] h-[600px] bg-[var(--card-bg)] border border-[var(--card-border)] rounded-2xl shadow-2xl flex flex-col z-50 animate-fade-in">
          {/* Header */}
          <div className="p-4 border-b border-[var(--card-border)] flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-[var(--accent)] flex items-center justify-center text-white text-xs font-bold">
              AI
            </div>
            <div>
              <p className="text-sm font-medium text-white">Portfolio AI Agent</p>
              <p className="text-xs text-[var(--success)]">Ready to assist</p>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[85%] rounded-xl p-3 text-sm ${
                    msg.role === "user"
                      ? "bg-[var(--accent)] text-white"
                      : "bg-[var(--card-border)] text-[var(--foreground)]"
                  }`}
                >
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                  {msg.actions && msg.actions.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-white/20">
                      <p className="text-xs opacity-70">Actions taken: {msg.actions.length}</p>
                    </div>
                  )}
                  {msg.context && msg.context.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-white/20">
                      <p className="text-xs opacity-70">RAG sources: {msg.context.length}</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-[var(--card-border)] rounded-xl p-3 text-sm text-[var(--muted)]">
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-[var(--accent)] rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                      <span className="w-2 h-2 bg-[var(--accent)] rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                      <span className="w-2 h-2 bg-[var(--accent)] rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                    </div>
                    Thinking...
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-[var(--card-border)]">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                placeholder="Ask about portfolios, rebalancing..."
                className="flex-1 bg-[var(--background)] border border-[var(--card-border)] rounded-lg px-4 py-2.5 text-sm text-white placeholder-[var(--muted)] focus:outline-none focus:border-[var(--accent)]"
              />
              <button
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                className="px-4 py-2.5 bg-[var(--accent)] text-white rounded-lg text-sm font-medium hover:bg-[var(--accent-light)] disabled:opacity-50 transition-colors"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

"use client";

import { useState, useRef, useEffect } from "react";
import { useChat } from "@/services/api";
import { useAnalysisStore } from "@/store/useAnalysisStore";
import { cn } from "@/lib/utils";
import { Send, MessageSquare, Bot, User } from "lucide-react";

export function ChatInterface() {
  const [question, setQuestion] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatHistory = useAnalysisStore((s) => s.chatHistory);
  const analysisId = useAnalysisStore((s) => s.analysisId);
  const chatMutate = useChat();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  const handleSend = () => {
    if (!question.trim() || !analysisId) return;
    chatMutate.mutate({ analysisId, question: question.trim() });
    setQuestion("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 min-h-0">
        {chatHistory.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-12 h-12 rounded-full bg-atlas-500/10 flex items-center justify-center mb-3">
              <MessageSquare className="w-6 h-6 text-atlas-400" />
            </div>
            <h3 className="text-sm font-medium text-slate-200">Ask about this repository</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-[220px]">
              No questions asked yet
            </p>
          </div>
        ) : (
          chatHistory.map((msg, i) => (
            <div
              key={i}
              className={cn(
                "flex gap-3 max-w-[85%]",
                msg.role === "user" ? "ml-auto flex-row-reverse" : ""
              )}
            >
              <div
                className={cn(
                  "rounded-full w-7 h-7 flex items-center justify-center shrink-0",
                  msg.role === "user" ? "bg-indigo-600" : "bg-atlas-500/20"
                )}
              >
                {msg.role === "user" ? (
                  <User className="w-4 h-4 text-white" />
                ) : (
                  <Bot className="w-4 h-4 text-atlas-400" />
                )}
              </div>
              <div
                className={cn(
                  "rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
                  msg.role === "user"
                    ? "bg-indigo-600 text-white rounded-tr-sm"
                    : "bg-slate-800/60 border border-slate-700 text-slate-200 rounded-tl-sm"
                )}
              >
                {msg.content}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-slate-800 bg-slate-950/50">
        <div className="flex items-end gap-2">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about this repository..."
            rows={1}
            className="flex-1 resize-none rounded-xl border border-slate-700 bg-slate-900/80 text-sm text-slate-100 placeholder-slate-500 outline-none focus:border-atlas-500 px-4 py-3 transition-colors"
            style={{ minHeight: "44px", maxHeight: "120px" }}
            onInput={(e) => {
              const el = e.target as HTMLTextAreaElement;
              el.style.height = "44px";
              el.style.height = Math.min(el.scrollHeight, 120) + "px";
            }}
            disabled={chatMutate.isPending}
          />
          <button
            onClick={handleSend}
            disabled={!question.trim() || chatMutate.isPending}
            className="p-3 rounded-xl bg-atlas-500 hover:bg-atlas-400 disabled:opacity-50 text-white transition-all shadow-lg shadow-atlas-500/30"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

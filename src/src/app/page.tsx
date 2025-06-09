'use client';

import { useState } from "react";

type Message = {
  id: number;
  role: "user" | "bot";
  content: string;
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now(),
      role: "user",
      content: input,
    };
    setMessages((msgs) => [...msgs, userMessage]);
    setInput("");

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input }),
    });
    const data = await res.json();

    const botMessage: Message = {
      id: Date.now() + 1,
      role: "bot",
      content: data.reply || "No response",
    };
    setMessages((msgs) => [...msgs, botMessage]);
  }

  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4 bg-gray-900 text-gray-100">
      <div className="w-full max-w-xl bg-gray-800 rounded shadow p-4 flex flex-col h-[80vh]">
        <div className="flex-1 overflow-y-auto mb-4 space-y-2">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`p-2 rounded ${
                msg.role === "user"
                  ? "bg-blue-700 text-right text-white"
                  : "bg-gray-700 text-left text-gray-100"
              }`}
            >
              <span className="font-semibold">{msg.role === "user" ? "You" : "Bot"}: </span>
              {msg.content}
            </div>
          ))}
        </div>
        <form onSubmit={handleSubmit} className="flex">
          <input
            className="flex-1 p-2 border-none rounded-l bg-gray-700 text-gray-100 placeholder-gray-400 focus:outline-none"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
          />
          <button
            type="submit"
            className="p-2 bg-blue-800 text-white rounded-r"
          >
            Send
          </button>
        </form>
      </div>
    </main>
  );
}

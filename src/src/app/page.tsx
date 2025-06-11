'use client';

import { useState, useEffect } from "react";
import { createClient } from '@/utils/supabase/client';
import { useAuth } from '@/context/auth-context';
import ChatSidebar from '@/app/components/forms/ChatSidebar';

type Message = {
  id: string;
  content: string;
  is_user: boolean;
  created_at?: string;
};

type Session = {
  id: string;
  title: string;
  created_at: string;
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const { isAuthenticated } = useAuth();
  const supabase = createClient();

  // Load sessions when authenticated
  useEffect(() => {
    if (!isAuthenticated) return;

    const loadSessions = async () => {
      const { data, error } = await supabase
        .from('chat_chatsession')
        .select('id, title, created_at')
        .order('created_at', { ascending: false });

      if (!error && data) {
        setSessions(data);
      }
    };

    loadSessions();
  }, [isAuthenticated]);

  // Load messages when session changes
  useEffect(() => {
    if (!activeSessionId) return;

    const loadMessages = async () => {
      const { data, error } = await supabase
        .from('chat_chatmessage')
        .select('*')
        .eq('session_id', activeSessionId)
        .order('created_at');

      if (!error && data) {
        setMessages(data.map(msg => ({
          id: msg.id,
          content: msg.content,
          is_user: msg.is_user
        })));
      }
    };

    loadMessages();
  }, [activeSessionId]);

  const createNewSession = async () => {
    const { data, error } = await supabase
      .from('chat_chatsession')
      .insert([{}])
      .select()
      .single();

    if (!error && data) {
      setSessions(prev => [data, ...prev]);
      setActiveSessionId(data.id);
      setMessages([]);
    }
  };

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || !activeSessionId) return;

    try {
      // Save user message
      const { data: userMsg, error: userError } = await supabase
        .from('chat_chatmessage')
        .insert({
          content: input,
          is_user: true,
          session_id: activeSessionId
        })
        .select()
        .single();

      if (userError) throw userError;

      setMessages(prev => [...prev, {
        id: userMsg.id,
        content: userMsg.content,
        is_user: userMsg.is_user
      }]);

      setInput("");

      // Get bot response
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message: input,
          session_id: activeSessionId 
        }),
      });
      
      if (!res.ok) throw new Error('API request failed');
      
      const data = await res.json();

      // Save bot response
      const { data: botMsg, error: botError } = await supabase
        .from('chat_chatmessage')
        .insert({
          content: data.reply || "No response",
          is_user: false,
          session_id: activeSessionId
        })
        .select()
        .single();

      if (!botError && botMsg) {
        setMessages(prev => [...prev, {
          id: botMsg.id,
          content: botMsg.content,
          is_user: botMsg.is_user
        }]);
      }
    } catch (error) {
      console.error('Message submission error:', error);
    }
  }

  return (
    <main className="flex min-h-screen bg-gray-900 text-gray-100">
      <ChatSidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onCreateNew={createNewSession}
        onSelectSession={setActiveSessionId}
      />

      <div className="flex-1 flex flex-col p-4">
        {activeSessionId ? (
          <>
            <div className="flex-1 overflow-y-auto mb-4 space-y-2">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.is_user ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-[70%] p-3 rounded-lg ${
                    msg.is_user 
                      ? "bg-blue-600 text-white"
                      : "bg-gray-700 text-gray-100"
                  }`}>
                    {msg.content}
                  </div>
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
                className="p-2 bg-blue-800 text-white rounded-r hover:bg-blue-700 transition-colors"
              >
                Send
              </button>
            </form>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            Select a chat or start a new one
          </div>
        )}
      </div>
    </main>
  );
}

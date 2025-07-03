'use client';

import { useState, useEffect } from "react";
import { supabase } from '@/utils/supabase/client';
import { useAuth } from '@/context/auth-context';
import ChatSidebar from '@/app/components/forms/ChatSidebar';

type Message = {
  id: string;
  content: string;
  is_user: boolean;
  session_id: string | null;
  created_at?: string;
};

type Session = {
  id: string;
  title: string;
  user_id: string;
  created_at: string;
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { isAuthenticated } = useAuth();

  // Load sessions with RLS enforcement
  useEffect(() => {
    if (!isAuthenticated) return;

    const loadSessions = async () => {
      setLoading(true);
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (!session) throw new Error("No active session");

        const { data, error } = await supabase
          .from('chat_chatsession')
          .select('id, title, created_at, user_id')
          .eq('user_id', session.user.id)
          .order('created_at', { ascending: false });

        if (error) throw error;
        setSessions(data || []);
      } catch (error) {
        console.error('Session load error:', error);
      } finally {
        setLoading(false);
      }
    };

    loadSessions();
  }, [isAuthenticated]);

  // Load messages when session changes
  useEffect(() => {
    if (!activeSessionId) return;

    const loadMessages = async () => {
      setLoading(true);
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (!session) throw new Error("No active session");

        const { data, error } = await supabase
          .from('chat_chatmessage')
          .select('*')
          .eq('session_id', activeSessionId)
          .eq('user_id', session.user.id)
          .order('created_at');

        if (error) throw error;
        setMessages(data || []);
      } catch (error) {
        console.error('Message load error:', error);
      } finally {
        setLoading(false);
      }
    };

    loadMessages();
  }, [activeSessionId]);

  const createNewSession = async (): Promise<string | null> => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error("User not authenticated");

      const { data, error } = await supabase
        .from('chat_chatsession')
        .insert({  
          title: 'New Chat',
          user_id: session.user.id  // Use session user ID directly
        })
        .select()
        .single();

      if (error) throw error;
      
      setSessions(prev => [data, ...prev]);
      setActiveSessionId(data.id);
      setMessages([]);
      return data.id;
    } catch (error) {
      console.error('Session creation error:', error);
      return null;
    }
  };

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;

    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) throw new Error("Not authenticated");

      // Create a new session if none is active
      let currentSessionId = activeSessionId;
      if (!currentSessionId) {
        const { data, error } = await supabase
          .from("chat_chatsession")
          .insert({
            title: input.slice(0, 50),
            user_id: session.user.id,
          })
          .select()
          .single();

        if (error) throw error;
        currentSessionId = data.id;
        setActiveSessionId(currentSessionId);
        setSessions((prev) => [data, ...prev]);
      }

      // Add user's message to UI immediately
      const userMsg = {
        id: crypto.randomUUID(),
        content: input,
        is_user: true,
        session_id: currentSessionId,
      };
      setMessages((prev) => [...prev, userMsg]);
      setInput("");

      // Send to Django backend
      const res = await fetch("http://localhost:8000/api/chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          message: input,
          session_id: currentSessionId,
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || "Backend error");
      }

      const data = await res.json();
      console.log("Backend response:", data, typeof data);

      // Add bot response to UI
      const botMsg = {
        id: crypto.randomUUID(),
        content: data.reply,
        is_user: false,
        session_id: currentSessionId,
      };
      setMessages((prev) => [...prev, botMsg]);

    } catch (err) {
      console.error("Chat error:", err);
      alert("Something went wrong. Check your server and network logs.");
    }
  }


  // Add loading state UI
  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <main className="flex min-h-screen bg-gradient-to-br from-blue-50 via-white to-gray-100 text-gray-900">
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
                  <div className={`max-w-[70%] p-3 rounded-2xl shadow ${
                    msg.is_user 
                      ? "bg-blue-500 text-white rounded-br-none"
                      : "bg-white text-gray-900 rounded-bl-none border border-gray-200"
                  }`}
                  style={{ wordBreak: "break-word" }}
                >
                    {msg.content}
                  </div>
                </div>
              ))}
            </div>
            <form onSubmit={handleSubmit} className="flex mt-2">
              <input
                className="flex-1 p-3 border border-gray-300 rounded-l-2xl bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-200"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message..."
              />
              <button
                type="submit"
                className="px-6 bg-blue-500 text-white rounded-r-2xl font-semibold hover:bg-blue-600 transition-colors"
              >
                Send
              </button>
            </form>
          </>
        ) : (
          <div className="flex-1 overflow-y-auto mb-4 space-y-3 px-2 py-4 transition-colors duration-200">
            Select a chat or start a new one
          </div>
        )}
      </div>
    </main>
  );
}

'use client';

import { useState, useEffect } from "react";
import { supabase } from '@/utils/supabase/client';
import { useAuth } from '@/context/auth-context';
import ChatSidebar from '@/app/components/forms/ChatSidebar';

type Message = {
  id: string;
  content: string;
  is_user: boolean;
  session_id: string;
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
    if (!input.trim() || !activeSessionId) return;

    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error("User not authenticated");

      // Save user message
      const { data: userMsg, error: userError } = await supabase
        .from('chat_chatmessage')
        .insert({
          content: input,
          is_user: true,
          session_id: activeSessionId,
          user_id: session.user.id
        })
        .select()
        .single();

      if (userError) throw userError;
      setMessages(prev => [...prev, userMsg]);
      setInput("");

      // Get bot response
      const res = await fetch("/api/chat", { 
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${session.access_token}` 
        },
        body: JSON.stringify({ 
          message: input,
          session_id: activeSessionId 
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || "API request failed");
      }

      const botResponse = await res.json();

      // Save bot response
      const { data: botMsg, error: botError } = await supabase
        .from('chat_chatmessage')
        .insert({
          content: botResponse.reply,
          is_user: false,
          session_id: activeSessionId,
          user_id: session.user.id
        })
        .select()
        .single();

      if (botError) throw botError;
      setMessages(prev => [...prev, botMsg]);

    } catch (error) {
      console.error('Submission error:', error);
      if (error instanceof Error && error.message.includes("401")) {
        await supabase.auth.signOut();
      }
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

"use client"; 

import { useState, useEffect } from 'react';
import { supabase } from '@/utils/supabase/client';
interface Session {
  id: string;
  title: string;
  created_at: string;
}

interface ChatSidebarProps {
  sessions: Session[];
  activeSessionId: string | null;
  onCreateNew: () => Promise<string | null>; 
  onSelectSession: (sessionId: string) => void;
}

export default function ChatSidebar({
  sessions,
  activeSessionId,
  onCreateNew,
  onSelectSession
}: ChatSidebarProps) {
  const handleNewChat = async () => {
    const newSessionId = await onCreateNew();
    if (newSessionId) {
      onSelectSession(newSessionId);
    }
  };

  return (
    <aside className="w-72 bg-gradient-to-b from-blue-900 to-gray-800 p-4 flex flex-col shadow-lg">
      <button 
        onClick={handleNewChat}
        className="w-full py-2 mb-6 bg-blue-500 hover:bg-blue-600 rounded-xl text-white font-semibold shadow transition-all"
      >
        + New Chat
      </button>
      <div className="space-y-2 overflow-y-auto flex-1">
        {sessions.map((session) => (
          <div
            key={session.id}
            onClick={() => onSelectSession(session.id)}
            className={`p-3 cursor-pointer rounded-lg transition-all ${
              activeSessionId === session.id
                ? 'bg-blue-100 border-l-4 border-blue-500 text-blue-900 shadow'
                : 'hover:bg-gray-200 text-gray-700'
            }`}
          >
            <div className="font-medium truncate">{session.title}</div>
            <div className="text-xs text-gray-400 mt-1">
              {new Date(session.created_at).toLocaleDateString()}
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}

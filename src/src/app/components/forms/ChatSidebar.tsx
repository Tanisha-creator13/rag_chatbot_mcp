"use client"; 

import { useState, useEffect } from 'react';
import { createClient } from '@/utils/supabase/client';
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
    console.log("handleNewChat called");
    const newSessionId = await onCreateNew();
    if (newSessionId) {
      onSelectSession(newSessionId);
    }
  };



  return (
    <div className="w-64 bg-gray-800 p-4 flex flex-col">
      <button 
        onClick={handleNewChat}
        className="w-full p-2 mb-4 bg-blue-600 hover:bg-blue-700 rounded text-white"
      >
        New Chat
      </button>
      
      <div className="space-y-1 overflow-y-auto flex-1">
        {sessions.map((session) => (
          <div
            key={session.id}
            onClick={() => onSelectSession(session.id)}
            className={`p-3 cursor-pointer rounded-lg ${
              activeSessionId === session.id 
                ? 'bg-gray-700 border-l-4 border-blue-500'
                : 'hover:bg-gray-600'
            } transition-colors`}
          >
            <h4 className="text-white font-medium truncate">{session.title}</h4>
            <small className="text-gray-400 text-xs">
              {new Date(session.created_at).toLocaleDateString()}
            </small>
          </div>
        ))}
      </div>
    </div>
  );
}


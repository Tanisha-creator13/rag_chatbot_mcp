"use client";
import { supabase } from '@/utils/supabase/client';

interface NewChatButtonProps {
  onCreate: (sessionId: string) => void;
}

export default function NewChatButton({ onCreate }: NewChatButtonProps) {
  const handleNewChat = async () => {
    const { data, error } = await supabase
      .from('chat_chatsession')
      .insert([{}])
      .select()
      .single();

    if (error) {
      console.error("Supabase error:", error);
    }
    if (data) {
      onCreate(data.id);
    }
  };

  return (
    <button
      onClick={handleNewChat}
      className="w-full py-2 mb-4 bg-blue-500 hover:bg-blue-600 rounded-xl text-white font-semibold shadow transition-all"
    >
      + New Chat
    </button>
  );
}

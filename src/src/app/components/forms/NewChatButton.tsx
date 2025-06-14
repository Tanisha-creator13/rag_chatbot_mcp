"use client";
import { createClient } from '@/utils/supabase/client'
const supabase = createClient()

interface NewChatButtonProps {
  onCreate: (sessionId: string) => void;
}

export default function NewChatButton({ onCreate }: NewChatButtonProps) {
  const handleNewChat = async () => {
    console.log("New Chat button clicked");
    const { data, error } = await supabase
      .from('chat_chatsession') // Use the correct table name
      .insert([{}])
      .select()
      .single();

    if (error) {
      console.error("Supabase error:", error);
    }
    if (data) {
      console.log("New session created:", data);
      onCreate(data.id);
    }
  };

  return (
    <button
      onClick={handleNewChat}
      className="w-full p-3 mb-4 text-left hover:bg-gray-700 rounded-lg transition-colors"
    >
      + New Chat
    </button>
  );
}

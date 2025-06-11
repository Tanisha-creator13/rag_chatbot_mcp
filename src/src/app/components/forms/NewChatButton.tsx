// import { supabase } from '@/utils/supabase/client';
import { createClient } from '@/utils/supabase/client'
const supabase = createClient()

interface NewChatButtonProps {
  onCreate: (sessionId: string) => void;
}

export default function NewChatButton({ onCreate }: NewChatButtonProps) {
  const handleNewChat = async () => {
    const { data, error } = await supabase
      .from('chatsession')
      .insert([{}])
      .select()
      .single();

    if (!error && data) {
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

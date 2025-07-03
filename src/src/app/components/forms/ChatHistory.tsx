import { supabase } from '@/utils/supabase/client';

interface Session {
  id: string;
  title: string;
  created_at: string;
}

interface ChatHistoryProps {
  sessions: Session[];
  activeSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
}

export default function ChatHistory({
  sessions,
  activeSessionId,
  onSelectSession
}: ChatHistoryProps) {
  return (
    <div className="space-y-2 overflow-y-auto flex-1 px-2 py-4">
      {sessions.map((session) => (
        <div
          key={session.id}
          onClick={() => onSelectSession(session.id)}
          className={`p-3 cursor-pointer rounded-lg transition-all ${
            activeSessionId === session.id
              ? 'bg-blue-50 border-l-4 border-blue-400 text-blue-900 shadow'
              : 'hover:bg-gray-100 text-gray-700'
          }`}
        >
          <div className="font-medium truncate">{session.title}</div>
          <div className="text-xs text-gray-400 mt-1">
            {new Date(session.created_at).toLocaleDateString()}
          </div>
        </div>
      ))}
    </div>
  );
}

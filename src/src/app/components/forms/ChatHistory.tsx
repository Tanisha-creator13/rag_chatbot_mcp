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
          <div className="text-white font-medium truncate">{session.title}</div>
          <div className="text-gray-400 text-xs mt-1">
            {new Date(session.created_at).toLocaleDateString()}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function MessageList({ messages, loading }) {
  return (
    <div className="messages">
      {messages.length === 0 && !loading && (
        <p className="empty">무엇이든 물어보세요.</p>
      )}
      {messages.map((m) => (
        <div key={m.id} className={`message ${m.role}`}>
          <div className="bubble">{m.content}</div>
        </div>
      ))}
      {loading && (
        <div className="message assistant">
          <div className="bubble typing">답변을 쓰는 중…</div>
        </div>
      )}
    </div>
  );
}

import { useEffect, useRef, useState } from 'react';
import './App.css';
import { createConversation, streamQuestion } from './api';
import InputBox from './components/InputBox';
import MessageList from './components/MessageList';

export default function App() {
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);

  useEffect(() => {
    createConversation()
      .then((conv) => setConversationId(conv.id))
      .catch(() => setError('대화를 시작하지 못했습니다. 서버가 켜져 있는지 확인해 주세요.'));
  }, []);

  const handleSend = async (question) => {
    if (!conversationId) return;
    setError(null);
    setLoading(true);

    const controller = new AbortController();
    abortRef.current = controller;

    const answerId = Date.now() + 1;
    setMessages((prev) => [
      ...prev,
      { id: Date.now(), role: 'user', content: question },
      { id: answerId, role: 'assistant', content: '' },
    ]);

    try {
      await streamQuestion(conversationId, question, {
        signal: controller.signal,
        onChunk: (answer) =>
          setMessages((prev) =>
            prev.map((m) => (m.id === answerId ? { ...m, content: answer } : m)),
          ),
      });
    } catch (err) {
      if (err.name === 'AbortError') {
        setError('답변 생성을 중단했습니다.');
      } else {
        setError('답변을 가져오지 못했습니다. 잠시 후 다시 시도해 주세요.');
        console.error(err);
      }
    } finally {
      abortRef.current = null;
      setLoading(false);
    }
  };

  const handleStop = () => abortRef.current?.abort();

  return (
    <div className="app">
      <header>
        <h1>AI 챗봇</h1>
        {conversationId && <span className="conv-id">대화 #{conversationId}</span>}
      </header>

      <MessageList messages={messages} loading={false} />

      {error && <p className="error">{error}</p>}

      <InputBox onSend={handleSend} disabled={loading || !conversationId} />
      {loading && (
        <button className="stop" onClick={handleStop}>
          중단
        </button>
      )}
    </div>
  );
}

import { useEffect, useState } from 'react';
import './App.css';
import { createConversation, sendQuestion } from './api';
import InputBox from './components/InputBox';
import MessageList from './components/MessageList';

export default function App() {
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 화면이 처음 뜰 때 대화방을 하나 만든다.
  useEffect(() => {
    createConversation()
      .then((conv) => setConversationId(conv.id))
      .catch(() => setError('대화를 시작하지 못했습니다. 서버가 켜져 있는지 확인해 주세요.'));
  }, []);

  const handleSend = async (question) => {
    if (!conversationId) return;
    setError(null);
    setLoading(true);

    // 내 메시지는 서버 응답을 기다리지 않고 바로 보여 준다.
    setMessages((prev) => [...prev, { id: Date.now(), role: 'user', content: question }]);

    try {
      const data = await sendQuestion(conversationId, question);
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, role: 'assistant', content: data.answer },
      ]);
    } catch (err) {
      setError('답변을 가져오지 못했습니다. 잠시 후 다시 시도해 주세요.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>AI 챗봇</h1>
        {conversationId && <span className="conv-id">대화 #{conversationId}</span>}
      </header>

      <MessageList messages={messages} loading={loading} />

      {error && <p className="error">{error}</p>}

      <InputBox onSend={handleSend} disabled={loading || !conversationId} />
    </div>
  );
}

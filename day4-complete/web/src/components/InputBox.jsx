import { useState } from 'react';

export default function InputBox({ onSend, disabled }) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    // 빈 입력은 서버까지 보내지 않는다 — 어차피 422 로 거절당한다.
    if (!input.trim()) return;
    onSend(input.trim());
    setInput('');
  };

  return (
    <div className="input-box">
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
        placeholder="질문을 입력하세요"
        disabled={disabled}
      />
      <button onClick={handleSend} disabled={disabled || !input.trim()}>
        전송
      </button>
    </div>
  );
}

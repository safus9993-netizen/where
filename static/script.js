document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const clearBtn = document.getElementById('clear-chat');

    // 自動調整輸入框高度
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = userInput.scrollHeight + 'px';
    });

    // 傳送訊息功能
    const sendMessage = async () => {
        const text = userInput.value.trim();
        if (!text) return;

        // 添加使用者訊息到 UI
        appendMessage('user', text);
        userInput.value = '';
        userInput.style.height = 'auto';

        // 顯示打字中
        const typingId = showTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });

            if (!response.ok) {
                throw new Error(`HTTP 錯誤！狀態碼：${response.status}`);
            }

            const data = await response.json();
            
            // 移除打字中，添加 AI 回應
            removeTypingIndicator(typingId);
            
            if (data.error) {
                appendMessage('ai', '抱歉，發生了錯誤：' + data.error);
            } else {
                appendMessage('ai', data.response);
            }
        } catch (error) {
            removeTypingIndicator(typingId);
            appendMessage('ai', `抱歉，連線失敗。詳細錯誤：${error.message}`);
            console.error('Fetch error:', error);
        }
    };

    const appendMessage = (sender, content) => {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}-message`;
        
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        msgDiv.innerHTML = `
            <div class="message-content">${content}</div>
            <div class="message-time">${time}</div>
        `;
        
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
    };

    const showTypingIndicator = () => {
        const id = 'typing-' + Date.now();
        const typingDiv = document.createElement('div');
        typingDiv.id = id;
        typingDiv.className = 'message ai-message';
        typingDiv.innerHTML = `
            <div class="message-content typing">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        scrollToBottom();
        return id;
    };

    const removeTypingIndicator = (id) => {
        const el = document.getElementById(id);
        if (el) el.remove();
    };

    const scrollToBottom = () => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    // 事件監聽
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    clearBtn.addEventListener('click', () => {
        if (confirm('確定要清除所有對話紀錄嗎？')) {
            chatMessages.innerHTML = '';
            appendMessage('ai', '對話已清除。有什麼我可以幫您的？');
        }
    });
});

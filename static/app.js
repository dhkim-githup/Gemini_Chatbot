const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

function appendMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);

    const bubbleDiv = document.createElement('div');
    bubbleDiv.classList.add('bubble');
    bubbleDiv.innerText = text;

    messageDiv.appendChild(bubbleDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 💡 진짜 백엔드 서버와 통신하도록 비동기(async) 함수로 변경
async function handleSend() {
    const text = userInput.value.trim();
    if (!text) return;

    // 1. 내가 쓴 말 화면에 추가
    appendMessage('user', text);
    userInput.value = '';

    // 2. 챗봇이 생각하는 중임을 표시하기 위해 임시 말풍선 노출 (선택 사항)
    appendMessage('bot', "생각 중...");
    const loadingBubble = chatMessages.lastElementChild;

    try {
        // 3. FastAPI 서버로 포스트(POST) 요청 전송
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: text })
        });

        if (!response.ok) {
            throw new Error('서버 응답 에러');
        }

        const data = await response.json();
        
        // "생각 중..." 문구를 진짜 Gemini 답변으로 교체
        loadingBubble.querySelector('.bubble').innerText = data.reply;

    } catch (error) {
        console.error(error);
        loadingBubble.querySelector('.bubble').innerText = "❌ 답변을 가져오는 중 오류가 발생했습니다. 다시 시도해 주세요.";
    }
}

sendBtn.addEventListener('click', handleSend);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSend();
    }
});
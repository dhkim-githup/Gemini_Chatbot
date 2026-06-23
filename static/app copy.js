const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

// 화면에 메시지 말풍선을 추가하는 함수
function appendMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);

    const bubbleDiv = document.createElement('div');
    bubbleDiv.classList.add('bubble');
    bubbleDiv.innerText = text;

    messageDiv.appendChild(bubbleDiv);
    chatMessages.appendChild(messageDiv);

    // 새 메시지가 추가되면 스크롤을 맨 아래로 이동
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 전송 버튼 핸들러
function handleSend() {
    const text = userInput.value.trim();
    if (!text) return;

    // 1. 내가 쓴 말 화면에 추가
    appendMessage('user', text);
    userInput.value = '';

    // 2. 챗봇의 가짜 답변 대기 (3단계에서 진짜 API 서버와 연동할 예정)
    setTimeout(() => {
        appendMessage('bot', `"${text}"라고 하셨군요! 화면이 정상적으로 잘 작동하고 있습니다. 3단계에서 진짜 저의 두뇌를 연결해 드릴게요.`);
    }, 500);
}

// 이벤트 리스너 등록
sendBtn.addEventListener('click', handleSend);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSend();
    }
});
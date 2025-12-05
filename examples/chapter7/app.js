document.addEventListener('DOMContentLoaded', () => {
    const chatWindow = document.getElementById('chat-window');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    sendBtn.addEventListener('click', () => {
        sendMessage();
    });

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const userText = userInput.value.trim();
        if (userText === '') return;

        appendMessage(userText, 'user-message');
        userInput.value = '';

        // Simulate AI response
        setTimeout(() => {
            const aiResponse = generateAIResponse(userText);
            appendMessage(aiResponse, 'ai-message');
        }, 1000);
    }

    function appendMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', type);
        const p = document.createElement('p');
        p.textContent = text;
        messageDiv.appendChild(p);
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight; // Auto-scroll to bottom
    }

    function generateAIResponse(userText) {
        const lowerText = userText.toLowerCase();

        if (lowerText.includes('hello') || lowerText.includes('hi')) {
            return "Hello there! How can I assist you with AI-native applications?";
        } else if (lowerText.includes('ai-native')) {
            return "AI-native applications are designed with AI at their core, enabling intelligence, adaptability, and personalization from the ground up.";
        } else if (lowerText.includes('conversational ui')) {
            return "Conversational UIs allow users to interact with systems using natural language, like chatbots or voice assistants. They are a key part of AI-powered interfaces.";
        } else if (lowerText.includes('uncertainty')) {
            return "Designing for uncertainty involves communicating the AI's confidence levels and planning for graceful degradation when predictions are not 100% certain.";
        } else if (lowerText.includes('thank you') || lowerText.includes('thanks')) {
            return "You're welcome! Is there anything else you'd like to know?";
        } else if (lowerText.includes('bye') || lowerText.includes('goodbye')) {
            return "Goodbye! Have a great day!";
        } else {
            return "That's an interesting point! In an AI-native context, we would typically analyze your input for intent and entity to provide a more specific response. For now, I can tell you more about AI-native design principles or conversational interfaces.";
        }
    }
});

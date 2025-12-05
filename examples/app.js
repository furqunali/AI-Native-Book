document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('text-input');
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultDiv = document.getElementById('result');

    analyzeBtn.addEventListener('click', () => {
        const text = textInput.value;
        if (text.trim() === '') {
            alert('Please enter some text to analyze.');
            return;
        }

        // Simulate a network request to an AI API
        resultDiv.textContent = 'Analyzing...';
        resultDiv.className = 'neutral';
        
        setTimeout(() => {
            const sentiment = getSentiment(text);
            displayResult(sentiment);
        }, 1000);
    });

    function getSentiment(text) {
        const lowerText = text.toLowerCase();
        const positiveWords = ['love', 'like', 'great', 'awesome', 'happy', 'excellent', 'good'];
        const negativeWords = ['hate', 'dislike', 'terrible', 'awful', 'sad', 'bad', 'poor'];

        let positiveCount = 0;
        let negativeCount = 0;

        positiveWords.forEach(word => {
            if (lowerText.includes(word)) {
                positiveCount++;
            }
        });

        negativeWords.forEach(word => {
            if (lowerText.includes(word)) {
                negativeCount++;
            }
        });

        if (positiveCount > negativeCount) {
            return 'Positive';
        } else if (negativeCount > positiveCount) {
            return 'Negative';
        } else {
            return 'Neutral';
        }
    }

    function displayResult(sentiment) {
        resultDiv.textContent = `Sentiment: ${sentiment}`;
        if (sentiment === 'Positive') {
            resultDiv.className = 'positive';
        } else if (sentiment === 'Negative') {
            resultDiv.className = 'negative';
        } else {
            resultDiv.className = 'neutral';
        }
    }
});

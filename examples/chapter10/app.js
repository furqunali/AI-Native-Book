document.addEventListener('DOMContentLoaded', () => {
    const inputText = document.getElementById('input-text');
    const orchestrateBtn = document.getElementById('orchestrate-btn');
    const sentimentOutput = document.getElementById('sentiment-output');
    const summarizationOutput = document.getElementById('summarization-output');
    const translationOutput = document.getElementById('translation-output');

    orchestrateBtn.addEventListener('click', () => {
        const text = inputText.value.trim();
        if (text === '') {
            alert('Please enter some text to orchestrate AI APIs.');
            return;
        }
        orchestrateAIProcess(text);
    });

    async function orchestrateAIProcess(text) {
        // Reset outputs
        sentimentOutput.textContent = 'Processing...';
        summarizationOutput.textContent = 'Waiting for Sentiment Analysis...';
        translationOutput.textContent = 'Waiting for Summarization...';

        // Step 1: Call Sentiment Analysis API
        const sentimentResult = await callSentimentAPI(text);
        sentimentOutput.textContent = `Predicted Sentiment: ${sentimentResult.sentiment} (Confidence: ${sentimentResult.confidence}%)`;

        // Step 2: Call Summarization API with original text
        summarizationOutput.textContent = 'Processing...';
        const summarizationResult = await callSummarizationAPI(text);
        summarizationOutput.textContent = summarizationResult.summary;

        // Step 3: Call Translation API with the summary
        translationOutput.textContent = 'Processing...';
        const translationResult = await callTranslationAPI(summarizationResult.summary, 'fr');
        translationOutput.textContent = translationResult.translatedText;
    }

    // --- Simulated API Functions ---

    function callSentimentAPI(text) {
        return new Promise(resolve => {
            setTimeout(() => {
                const lowerText = text.toLowerCase();
                let sentiment = 'Neutral';
                let confidence = 70;

                if (lowerText.includes('excellent') || lowerText.includes('great') || lowerText.includes('love') || lowerText.includes('positive')) {
                    sentiment = 'Positive';
                    confidence = Math.min(95, 80 + Math.floor(Math.random() * 15));
                } else if (lowerText.includes('bad') || lowerText.includes('terrible') || lowerText.includes('hate') || lowerText.includes('negative')) {
                    sentiment = 'Negative';
                    confidence = Math.min(95, 80 + Math.floor(Math.random() * 15));
                } else {
                    confidence = Math.min(85, 60 + Math.floor(Math.random() * 25));
                }
                resolve({ sentiment, confidence });
            }, 1500); // Simulate network delay
        });
    }

    function callSummarizationAPI(text) {
        return new Promise(resolve => {
            setTimeout(() => {
                const words = text.split(' ');
                let summary = text;
                if (words.length > 30) {
                    summary = words.slice(0, Math.floor(words.length * 0.4)).join(' ') + '... (Simulated summary)';
                } else {
                    summary = text + ' (Text too short for significant summarization, original text returned.)';
                }
                resolve({ summary });
            }, 2000); // Simulate network delay and processing
        });
    }

    function callTranslationAPI(text, targetLanguage) {
        return new Promise(resolve => {
            setTimeout(() => {
                let translatedText = '';
                if (targetLanguage === 'fr') {
                    if (text.includes('Simulated summary')) {
                        translatedText = "Ceci est un résumé simulé de votre texte. (Traduit en français)";
                    } else if (text.includes('AI-native book')) {
                        translatedText = "Le nouveau livre natif de l'IA est une excellente ressource pour les développeurs.";
                    } else {
                        translatedText = `Traduction simulée en français de: "${text.substring(0, 50)}..."`;
                    }
                } else {
                    translatedText = `Simulated translation of "${text}" into ${targetLanguage}.`;
                }
                resolve({ translatedText });
            }, 1800); // Simulate network delay
        });
    }
});

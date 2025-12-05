document.addEventListener('DOMContentLoaded', () => {
    const aiTaskSelect = document.getElementById('ai-task-select');
    const userInputText = document.getElementById('user-input-text');
    const processBtn = document.getElementById('process-btn');
    const aiOutputText = document.getElementById('ai-output-text');

    processBtn.addEventListener('click', () => {
        const task = aiTaskSelect.value;
        const input = userInputText.value.trim();

        if (input === '') {
            aiOutputText.textContent = 'Please provide some input for the selected task.';
            return;
        }

        aiOutputText.textContent = 'Processing...';

        setTimeout(() => {
            const output = simulateModelOutput(task, input);
            aiOutputText.textContent = output;
        }, 1500); // Simulate processing delay
    });

    function simulateModelOutput(task, input) {
        let output = '';
        const lowerInput = input.toLowerCase();

        switch (task) {
            case 'sentiment_analysis':
                if (lowerInput.includes('great') || lowerInput.includes('excellent') || lowerInput.includes('love')) {
                    output = 'Sentiment: Positive (Confidence: 92%)';
                } else if (lowerInput.includes('bad') || lowerInput.includes('terrible') || lowerInput.includes('hate')) {
                    output = 'Sentiment: Negative (Confidence: 88%)';
                } else {
                    output = 'Sentiment: Neutral (Confidence: 65%)';
                }
                break;
            case 'text_summarization':
                if (input.split(' ').length > 20) {
                    output = `Summary: This is a simulated summary of your input text. It captures the main points concisely, like a powerful language model would do. The original text discusses various topics, and this summary highlights the most salient information.`;
                } else {
                    output = `Summary: Your text is too short to summarize effectively. Please provide more content.`;
                }
                break;
            case 'image_captioning': // Simulated, as we don't handle actual images
                if (lowerInput.includes('cat') || lowerInput.includes('feline')) {
                    output = 'Caption: A domestic short-haired cat relaxing on a sunlit windowsill.';
                } else if (lowerInput.includes('dog') || lowerInput.includes('canine')) {
                    output = 'Caption: A happy golden retriever running through a field of green grass.';
                } else if (lowerInput.includes('mountain') || lowerInput.includes('nature')) {
                    output = 'Caption: Majestic snow-capped mountains under a clear blue sky.';
                } else {
                    output = 'Caption: A vivid scene, perhaps a bustling city street or a tranquil garden.';
                }
                output += ' (Simulated image input, AI model generated description.)';
                break;
            case 'translation':
                if (lowerInput.includes('hello')) {
                    output = 'Translation (French): Bonjour';
                } else if (lowerInput.includes('goodbye')) {
                    output = 'Translation (Spanish): Adiós';
                } else if (lowerInput.includes('thank you')) {
                    output = 'Translation (German): Danke schön';
                } else {
                    output = `Translation: This is a simulated translation of "${input}" into another language.`;
                }
                break;
            default:
                output = 'Unknown AI task selected. Please choose a valid task.';
        }
        return output;
    }
});

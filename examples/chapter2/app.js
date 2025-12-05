document.addEventListener('DOMContentLoaded', () => {
    const promptInput = document.getElementById('prompt-input');
    const generateBtn = document.getElementById('generate-btn');
    const generatedTextDisplay = document.getElementById('generated-text');

    generateBtn.addEventListener('click', () => {
        const prompt = promptInput.value.trim();
        if (prompt === '') {
            generatedTextDisplay.textContent = 'Please enter a prompt to generate text.';
            return;
        }

        generatedTextDisplay.textContent = 'Generating...';
        
        // Simulate a call to an LLM
        setTimeout(() => {
            const generatedResponse = simulateLLMResponse(prompt);
            generatedTextDisplay.textContent = generatedResponse;
        }, 1500); // Simulate a delay for generation
    });

    function simulateLLMResponse(prompt) {
        let response = "";
        const lowerPrompt = prompt.toLowerCase();

        if (lowerPrompt.includes("story about a futuristic city")) {
            response = "In the year 2077, Neo-Kyoto's neon-lit skyscrapers pierced the perpetual twilight. Flying vehicles zipped between chrome towers, and holographic advertisements flickered across every surface. Below, the ancient streets hummed with a different kind of life, a rebellion brewing in the shadows against the omnipresent AI overlord, 'Aura'.";
        } else if (lowerPrompt.includes("recipe for a cake")) {
            response = "To bake a delicious chocolate cake, you'll need flour, sugar, cocoa powder, baking soda, baking powder, salt, eggs, milk, oil, and vanilla extract. Combine dry ingredients, then wet. Mix until just combined. Bake at 350°F (175°C) for 30-35 minutes. Enjoy!";
        } else if (lowerPrompt.includes("poem about nature")) {
            response = "Whispering winds through emerald leaves, \nSunlight dappled, gently weaves. \nRivers murmur, stones they kiss, \nNature's symphony, pure bliss.";
        } else if (lowerPrompt.includes("explain machine learning")) {
            response = "Machine learning is a subset of artificial intelligence that allows systems to learn from data, identify patterns, and make decisions with minimal human intervention. It involves algorithms that are trained on data to build models, which can then be used to make predictions or classifications.";
        } else if (lowerPrompt.includes("hello")) {
            response = "Hello there! How can I assist you today?";
        }
        else {
            response = `I'm an AI text generator. You asked me to "${prompt}". Here's a generic response: The future holds endless possibilities, and with AI, we are constantly expanding the boundaries of what can be achieved.`;
        }
        return response;
    }
});

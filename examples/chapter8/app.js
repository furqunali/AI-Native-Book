document.addEventListener('DOMContentLoaded', () => {
    const commandInput = document.getElementById('command-input');
    const sendCommandBtn = document.getElementById('send-command-btn');
    const agentOutput = document.getElementById('agent-output');

    sendCommandBtn.addEventListener('click', () => {
        executeCommand();
    });

    commandInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            executeCommand();
        }
    });

    function addMessage(text, type) {
        const messageDiv = document.createElement('p');
        messageDiv.classList.add(type === 'agent' ? 'agent-message' : 'user-command');
        messageDiv.innerHTML = `<strong>${type === 'agent' ? 'Agent' : 'User'}:</strong> ${text}`;
        agentOutput.appendChild(messageDiv);
        agentOutput.scrollTop = agentOutput.scrollHeight; // Auto-scroll
    }

    async function executeCommand() {
        const command = commandInput.value.trim();
        if (command === '') return;

        addMessage(command, 'user');
        commandInput.value = '';

        addMessage("Thinking...", 'agent');
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate thinking time

        const response = await simulateAgent(command);
        agentOutput.lastChild.remove(); // Remove "Thinking..." message
        addMessage(response, 'agent');
    }

    async function simulateAgent(command) {
        const lowerCommand = command.toLowerCase();

        if (lowerCommand.includes('search for') || lowerCommand.includes('what is')) {
            addMessage("Agent: Using 'SearchTool'...", 'agent-message');
            await new Promise(resolve => setTimeout(resolve, 800));
            return simulateSearchTool(lowerCommand);
        } else if (lowerCommand.includes('set reminder') || lowerCommand.includes('remind me')) {
            addMessage("Agent: Using 'ReminderTool'...", 'agent-message');
            await new Promise(resolve => setTimeout(resolve, 800));
            return simulateReminderTool(lowerCommand);
        } else if (lowerCommand.includes('generate')) {
            addMessage("Agent: Using 'TextGenerationTool'...", 'agent-message');
            await new Promise(resolve => setTimeout(resolve, 800));
            return simulateTextGenerationTool(lowerCommand);
        } else if (lowerCommand.includes('hello') || lowerCommand.includes('hi')) {
            return "Hello! How can I assist you with a task today?";
        } else if (lowerCommand.includes('tell me about ai agents')) {
            return "AI agents are systems that perceive their environment, make decisions, and take actions to achieve goals. They often orchestrate multiple AI models and tools.";
        }
        else {
            return "I'm not sure which tool to use for that. Can you phrase your request differently?";
        }
    }

    // Simulated Tools
    function simulateSearchTool(query) {
        if (query.includes("weather")) {
            return "SearchTool: Today's weather in your simulated location is sunny with a high of 25°C.";
        } else if (query.includes("AI-native")) {
            return "SearchTool: AI-native applications are built with AI as their core, enabling intelligence, adaptability, and personalization.";
        }
        return `SearchTool: Found simulated results for "${query}".`;
    }

    function simulateReminderTool(command) {
        const match = command.match(/remind me to (.*)( on | at )?(.*)?/i);
        if (match && match[1]) {
            const what = match[1].trim();
            const when = match[3] ? match[3].trim() : "sometime soon";
            return `ReminderTool: Set a reminder to "${what}" for ${when}.`;
        }
        return "ReminderTool: Please specify what you want to be reminded about. E.g., 'remind me to call John tomorrow'.";
    }

    function simulateTextGenerationTool(command) {
        const match = command.match(/generate (a short story|a poem|a recipe) about (.*)/i);
        if (match && match[1] && match[2]) {
            const type = match[1].toLowerCase();
            const subject = match[2].trim();
            return `TextGenerationTool: Generating ${type} about "${subject}". This would typically involve a large language model to produce creative text.`;
        }
        return "TextGenerationTool: Please specify what you'd like me to generate. E.g., 'generate a short story about a brave knight'.";
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const interestCheckboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]');
    const updateRecommendationsBtn = document.getElementById('update-recommendations-btn');
    const recommendationsList = document.getElementById('recommendations-list');

    // Simulated content database with associated keywords/topics
    const allArticles = [
        { title: "The Latest in Large Language Models", topics: ["AI", "Tech"], content: "A deep dive into recent advancements in LLMs." },
        { title: "Blockchain's Impact on Modern Business", topics: ["Tech", "Business"], content: "Exploring how distributed ledger technology is reshaping industries." },
        { title: "Neuroscience Breakthroughs in Memory Formation", topics: ["Science"], content: "New research shedding light on how our brains store memories." },
        { title: "Generative AI in Artistic Creation", topics: ["AI", "Creativity"], content: "How AI is assisting artists and designers in new ways." },
        { title: "Stock Market Trends and AI Prediction", topics: ["Business", "AI"], content: "An analysis of current market dynamics and AI-driven forecasting." },
        { title: "Innovations in Quantum Computing", topics: ["Tech", "Science"], content: "The race to build powerful quantum machines and their potential impact." },
        { title: "User Experience Design with AI Assistants", topics: ["AI", "Creativity"], content: "Designing intuitive interfaces for AI-powered virtual helpers." },
        { title: "Sustainable Business Practices for the Future", topics: ["Business"], content: "Companies adopting eco-friendly strategies for long-term growth." },
        { title: "Exploring the Milky Way: New Discoveries", topics: ["Science"], content: "Astronomers uncover more secrets of our home galaxy." },
        { title: "Creative Writing Prompts for AI", topics: ["AI", "Creativity"], content: "Ideas for using AI to overcome writer's block and explore new narratives." }
    ];

    updateRecommendationsBtn.addEventListener('click', () => {
        const selectedInterests = Array.from(interestCheckboxes)
                                    .filter(cb => cb.checked)
                                    .map(cb => cb.value);

        displayRecommendations(selectedInterests);
    });

    function displayRecommendations(interests) {
        recommendationsList.innerHTML = ''; // Clear previous recommendations

        if (interests.length === 0) {
            recommendationsList.innerHTML = '<li>Please select at least one interest to get recommendations.</li>';
            return;
        }

        const filteredArticles = allArticles.filter(article => 
            interests.some(interest => article.topics.includes(interest))
        );

        if (filteredArticles.length === 0) {
            recommendationsList.innerHTML = '<li>No articles match your selected interests. Try selecting more!</li>';
        } else {
            // Simulate a delay for fetching/generating recommendations
            recommendationsList.innerHTML = '<li>Fetching personalized recommendations...</li>';
            setTimeout(() => {
                recommendationsList.innerHTML = ''; // Clear "fetching" message
                filteredArticles.forEach(article => {
                    const listItem = document.createElement('li');
                    listItem.innerHTML = `<strong>${article.title}</strong><p>${article.content.substring(0, 100)}...</p>`;
                    recommendationsList.appendChild(listItem);
                });
            }, 1000);
        }
    }
    
    // Initial display of recommendations (e.g., based on default or no selection)
    displayRecommendations([]);
});

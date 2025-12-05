document.addEventListener('DOMContentLoaded', () => {
    const searchQueryInput = document.getElementById('search-query-input');
    const searchBtn = document.getElementById('search-btn');
    const searchResultsList = document.getElementById('search-results-list');

    // Simulated documents with keywords indicating their "semantic" content
    const documents = [
        {
            id: 1,
            title: 'The Rise of Large Language Models',
            content: 'Large Language Models (LLMs) are transforming how we interact with AI. They excel at natural language processing tasks like generation and understanding. This document discusses their architecture and applications.',
            keywords: ['LLM', 'language model', 'NLP', 'AI', 'text generation', 'understanding']
        },
        {
            id: 2,
            title: 'Vector Databases: Powering Semantic Search',
            content: 'Vector databases are specialized systems designed to store and query high-dimensional vectors, or embeddings. They are crucial for semantic search, recommendation systems, and anomaly detection by finding similar items based on vector proximity.',
            keywords: ['vector database', 'embeddings', 'semantic search', 'similarity', 'AI', 'data']
        },
        {
            id: 3,
            title: 'Data Quality in Machine Learning Pipelines',
            content: 'High-quality data is paramount for effective machine learning. Data pipelines ensure data is clean, consistent, and relevant. This article emphasizes the importance of data validation and preprocessing steps.',
            keywords: ['data quality', 'ML pipeline', 'data processing', 'machine learning', 'clean data']
        },
        {
            id: 4,
            title: 'The Future of AI-Native Applications',
            content: 'AI-native applications integrate AI at their core. They are adaptive, intelligent, and personalized. This piece explores future trends like multimodal AI and embodied AI, shaping technology and society.',
            keywords: ['AI-native', 'future of AI', 'adaptive systems', 'intelligent applications', 'multimodal AI']
        },
        {
            id: 5,
            title: 'Human-in-the-Loop AI Design Principles',
            content: 'Human-in-the-loop (HITL) is a design principle where humans collaborate with AI to improve performance. It ensures oversight and allows AI to learn from human feedback, especially in tasks requiring nuanced judgment.',
            keywords: ['HITL', 'human-in-the-loop', 'AI design', 'feedback', 'collaboration']
        }
    ];

    searchBtn.addEventListener('click', () => {
        const query = searchQueryInput.value.trim();
        if (query === '') {
            searchResultsList.innerHTML = '<li>Please enter a search query.</li>';
            return;
        }

        searchResultsList.innerHTML = '<li>Searching...</li>';

        // Simulate a delay for semantic search
        setTimeout(() => {
            const results = performSemanticSearch(query);
            displaySearchResults(results);
        }, 1500);
    });

    function performSemanticSearch(query) {
        const lowerQuery = query.toLowerCase();
        const relevantDocuments = [];

        // Simple keyword-based semantic matching for simulation purposes
        documents.forEach(doc => {
            let score = 0;
            const queryWords = lowerQuery.split(/\s+/).filter(word => word.length > 2); // ignore short words

            doc.keywords.forEach(keyword => {
                if (queryWords.includes(keyword) || lowerQuery.includes(keyword)) {
                    score += 1;
                }
            });
            
            // Also check content for broader matches
            if (lowerQuery.split(/\s+/).some(qWord => doc.content.toLowerCase().includes(qWord))) {
                score += 0.5; // Slightly lower score for general content match
            }

            if (score > 0) {
                relevantDocuments.push({ doc, score });
            }
        });

        // Sort by score (higher score means more relevant)
        relevantDocuments.sort((a, b) => b.score - a.score);

        return relevantDocuments.map(item => item.doc);
    }

    function displaySearchResults(results) {
        searchResultsList.innerHTML = ''; // Clear previous results
        if (results.length === 0) {
            searchResultsList.innerHTML = '<li>No semantically similar documents found.</li>';
        } else {
            results.forEach(doc => {
                const listItem = document.createElement('li');
                listItem.innerHTML = `<strong>${doc.title}</strong><p>${doc.content}</p>`;
                searchResultsList.appendChild(listItem);
            });
        }
    }
});

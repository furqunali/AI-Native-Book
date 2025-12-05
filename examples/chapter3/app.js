document.addEventListener('DOMContentLoaded', () => {
    const statementInput = document.getElementById('statement-input');
    const predictBtn = document.getElementById('predict-btn');
    const predictionText = document.getElementById('prediction-text');
    const confidencePercentage = document.getElementById('confidence-percentage');
    const confidenceFill = document.getElementById('confidence-fill');

    predictBtn.addEventListener('click', () => {
        const statement = statementInput.value.trim();
        if (statement === '') {
            predictionText.textContent = '---';
            confidencePercentage.textContent = '0%';
            confidenceFill.style.width = '0%';
            alert('Please enter a statement to predict.');
            return;
        }

        predictionText.textContent = 'Predicting...';
        confidencePercentage.textContent = '...';
        confidenceFill.style.width = '0%';

        // Simulate an AI prediction with a delay
        setTimeout(() => {
            const { prediction, confidence } = simulatePredictionWithConfidence(statement);
            displayPrediction(prediction, confidence);
        }, 1500); // Simulate a delay for prediction
    });

    function simulatePredictionWithConfidence(statement) {
        const lowerStatement = statement.toLowerCase();
        let prediction = 'Neutral';
        let confidence = 50; // Default confidence

        if (lowerStatement.includes('great') || lowerStatement.includes('fantastic') || lowerStatement.includes('love')) {
            prediction = 'Positive';
            confidence = Math.min(95, 70 + Math.floor(Math.random() * 25)); // High confidence
        } else if (lowerStatement.includes('bad') || lowerStatement.includes('terrible') || lowerStatement.includes('hate')) {
            prediction = 'Negative';
            confidence = Math.min(95, 70 + Math.floor(Math.random() * 25)); // High confidence
        } else if (lowerStatement.includes('okay') || lowerStatement.includes('average')) {
            prediction = 'Neutral';
            confidence = Math.min(75, 40 + Math.floor(Math.random() * 35)); // Medium confidence
        } else if (lowerStatement.length < 10) { // Shorter statements might be less confident
            confidence = Math.min(60, 20 + Math.floor(Math.random() * 40));
        } else {
            confidence = Math.min(80, 50 + Math.floor(Math.random() * 30));
        }

        return { prediction, confidence };
    }

    function displayPrediction(prediction, confidence) {
        predictionText.textContent = prediction;
        confidencePercentage.textContent = `${confidence}%`;
        confidenceFill.style.width = `${confidence}%`;

        // You could also change colors based on confidence level for more visual feedback
        if (confidence < 40) {
            confidenceFill.style.backgroundColor = '#dc3545'; // Red for low confidence
        } else if (confidence < 70) {
            confidenceFill.style.backgroundColor = '#ffc107'; // Yellow for medium confidence
        } else {
            confidenceFill.style.backgroundColor = '#28a745'; // Green for high confidence
        }
    }
});

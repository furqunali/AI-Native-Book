document.addEventListener('DOMContentLoaded', () => {
    const accuracyValue = document.getElementById('accuracy-value');
    const accuracyStatus = document.getElementById('accuracy-status');
    const driftValue = document.getElementById('drift-value');
    const driftStatus = document.getElementById('drift-status');

    let currentAccuracy = 95.0;
    let currentDrift = 0.15;

    function updateDashboard() {
        // Simulate fluctuations in metrics
        currentAccuracy += (Math.random() - 0.5) * 0.5; // +/- 0.25
        currentDrift += (Math.random() - 0.5) * 0.02; // +/- 0.01

        // Keep metrics within reasonable bounds
        currentAccuracy = Math.max(80.0, Math.min(99.0, currentAccuracy));
        currentDrift = Math.max(0.05, Math.min(0.5, currentDrift));

        accuracyValue.textContent = `${currentAccuracy.toFixed(1)}%`;
        driftValue.textContent = currentDrift.toFixed(2);

        // Update accuracy status
        if (currentAccuracy > 90) {
            accuracyStatus.innerHTML = 'Status: <span class="good">Optimal</span>';
            accuracyValue.style.color = '#28a745';
        } else if (currentAccuracy > 85) {
            accuracyStatus.innerHTML = 'Status: <span class="warning">Warning (Slight Degradation)</span>';
            accuracyValue.style.color = '#ffc107';
        } else {
            accuracyStatus.innerHTML = 'Status: <span class="critical">Critical (Significant Degradation)</span>';
            accuracyValue.style.color = '#dc3545';
        }

        // Update drift status
        if (currentDrift < 0.2) {
            driftStatus.innerHTML = 'Status: <span class="good">Low</span>';
            driftValue.style.color = '#28a745';
        } else if (currentDrift < 0.35) {
            driftStatus.innerHTML = 'Status: <span class="warning">Warning (Moderate Drift)</span>';
            driftValue.style.color = '#ffc107';
        } else {
            driftStatus.innerHTML = 'Status: <span class="critical">Critical (High Drift)</span>';
            driftValue.style.color = '#dc3545';
        }
    }

    // Update metrics every 3 seconds
    setInterval(updateDashboard, 3000);

    // Initial update
    updateDashboard();
});

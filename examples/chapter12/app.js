document.addEventListener('DOMContentLoaded', () => {
    const futureConceptInput = document.getElementById('future-concept-input');
    const generateScenarioBtn = document.getElementById('generate-scenario-btn');
    const generatedScenarioText = document.getElementById('generated-scenario-text');

    generateScenarioBtn.addEventListener('click', () => {
        const concept = futureConceptInput.value.trim();
        if (concept === '') {
            generatedScenarioText.textContent = 'Please enter a concept to generate a future AI scenario.';
            return;
        }
        generatedScenarioText.textContent = 'Generating future scenario...';

        setTimeout(() => {
            const scenario = generateFutureScenario(concept);
            generatedScenarioText.textContent = scenario;
        }, 2000); // Simulate generation time
    });

    function generateFutureScenario(concept) {
        const lowerConcept = concept.toLowerCase();
        let scenario = `In a future reshaped by AI, the domain of "${concept}" undergoes a profound transformation.`;

        if (lowerConcept.includes('healthcare') || lowerConcept.includes('medicine')) {
            scenario += ` Personalized AI diagnostics systems, leveraging quantum computing, predict diseases years in advance with near-perfect accuracy. Robotic surgeons, guided by real-time AI analytics, perform complex operations with unprecedented precision. Wearable AI health monitors continuously optimize individual well-being, while AI-powered drug discovery accelerates cures for previously intractable conditions. The focus shifts from treatment to predictive, preventive, and hyper-personalized care, extending human lifespan and quality of life significantly.`;
        } else if (lowerConcept.includes('autonomous driving') || lowerConcept.includes('transportation')) {
            scenario += ` Fully autonomous vehicles, coordinated by city-wide AI traffic management systems, eliminate congestion and accidents. Personal AI copilots anticipate travel needs, optimize routes, and even manage logistics for last-mile delivery drones. Public transport becomes a seamless, on-demand network of self-driving pods, drastically reducing environmental impact and reclaiming urban space previously dedicated to parking.`;
        } else if (lowerConcept.includes('creative arts') || lowerConcept.includes('art')) {
            scenario += ` AI becomes an omnipresent collaborator in the creative arts. Generative AI models co-create symphonies, paint novel masterpieces, and write compelling narratives alongside human artists. Personal AI muses offer instant feedback and inspiration, pushing creative boundaries. Art becomes a dynamic, interactive experience, where AI adapts creations in real-time to individual viewer emotions, blurring the lines between artist, audience, and algorithm.`;
        } else if (lowerConcept.includes('education') || lowerConcept.includes('learning')) {
            scenario += ` Personalized AI tutors, adapting to each student's learning style, pace, and interests, revolutionize education. Holographic AI mentors guide experiential learning in virtual and augmented realities. The curriculum becomes fluid, constantly updated by AI to reflect the latest global knowledge, preparing individuals not just for jobs, but for continuous adaptation in a rapidly changing world.`;
        } else {
            scenario += ` Driven by advanced AI, every aspect of this field is optimized, automated, and hyper-personalized. Intelligent agents handle complex tasks, while predictive analytics inform all decisions. The human role shifts to oversight, creativity, and strategic direction, as AI empowers unprecedented efficiency and innovation. This future is characterized by seamless integration, continuous adaptation, and a focus on maximizing human potential within an intelligent ecosystem.`;
        }
        return scenario;
    }
});

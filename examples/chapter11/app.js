document.addEventListener('DOMContentLoaded', () => {
    const aiDomainSelect = document.getElementById('ai-domain-select');
    const exploreBtn = document.getElementById('explore-btn');
    const projectsContainer = document.getElementById('projects-container');

    const openSourceProjects = {
        nlp: [
            { name: "Hugging Face Transformers", description: "State-of-the-art NLP for PyTorch, TensorFlow, and JAX.", link: "https://huggingface.co/transformers/" },
            { name: "spaCy", description: "Industrial-strength natural language processing (NLP) in Python.", link: "https://spacy.io/" },
            { name: "NLTK", description: "Natural Language Toolkit, a leading platform for building Python programs to work with human language data.", link: "https://www.nltk.org/" }
        ],
        cv: [
            { name: "OpenCV", description: "Open Source Computer Vision Library for real-time computer vision.", link: "https://opencv.org/" },
            { name: "YOLO (You Only Look Once)", description: "Real-time object detection system.", link: "https://pjreddie.com/darknet/yolo/" },
            { name: "Detectron2", description: "Facebook AI Research's next-generation platform for object detection and segmentation.", link: "https://github.com/facebookresearch/detectron2" }
        ],
        mlops: [
            { name: "MLflow", description: "Open source platform for the machine learning lifecycle.", link: "https://mlflow.org/" },
            { name: "Kubeflow", description: "The machine learning toolkit for Kubernetes.", link: "https://www.kubeflow.org/" },
            { name: "DVC (Data Version Control)", description: "Open-source version control system for machine learning projects.", link: "https://dvc.org/" }
        ],
        frameworks: [
            { name: "TensorFlow", description: "An open-source machine learning framework by Google.", link: "https://www.tensorflow.org/" },
            { name: "PyTorch", description: "An open-source machine learning library developed by Facebook AI Research.", link: "https://pytorch.org/" },
            { name: "JAX", description: "Composable transformations of Python+NumPy programs: differentiate, vectorize, jit, and more.", link: "https://github.com/google/jax" }
        ]
    };

    exploreBtn.addEventListener('click', () => {
        const selectedDomain = aiDomainSelect.value;
        displayProjects(selectedDomain);
    });

    function displayProjects(domain) {
        projectsContainer.innerHTML = ''; // Clear previous projects

        const projects = openSourceProjects[domain];

        if (projects && projects.length > 0) {
            projects.forEach(project => {
                const projectCard = document.createElement('div');
                projectCard.classList.add('project-card');
                projectCard.innerHTML = `
                    <h3>${project.name}</h3>
                    <p>${project.description}</p>
                    <a href="${project.link}" target="_blank">Learn More</a>
                `;
                projectsContainer.appendChild(projectCard);
            });
        } else {
            projectsContainer.innerHTML = '<p>No projects found for this domain.</p>';
        }
    }

    // Initial display
    displayProjects(aiDomainSelect.value);
});

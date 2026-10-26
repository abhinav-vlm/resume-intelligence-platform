SKILLS = {
    "programming_languages": {
        "Python",
        "C",
        "C++",
        "Java",
        "JavaScript",
        "TypeScript",
        "Go",
        "Rust",
        "Ruby",
    },

    "web_frontend": {
        "HTML",
        "CSS",
        "React",
    },

    "backend_systems": {
        "FastAPI",
        "Django",
        "Flask",
        "Node.js",
        "Kafka",
        "Spark",
        "GraphQL",
        "REST",
        "Spring Boot",
        ".NET",
    },

    "databases": {
        "SQL",
        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "Redis",
        "Cassandra",
        "Elasticsearch",
        "DynamoDB",
    },

    "ml_ai": {
        "TensorFlow",
        "PyTorch",
        "Scikit-learn",
        "Pandas",
        "NumPy",
        "Keras",
        "MLflow",
        "Hugging Face",
        "NLP",
        "Computer Vision",
    },

    "devops_cloud": {
        "AWS",
        "Azure",
        "GCP",
        "Docker",
        "Kubernetes",
        "Terraform",
        "Jenkins",
        "CI/CD",
        "Bash",
        "Ansible",
    },

    "version_control": {
        "Git",
    },

    # R-044: compound multi-word technical concepts that must survive
    # conjunction splitting (e.g. 'Data Structures and Algorithms').
    "compound_concepts": {
        "Data Structures and Algorithms",
        "Object Oriented Programming",
        "Computer Vision",
        "Natural Language Processing",
        "Machine Learning",
        "Deep Learning",
        "Reinforcement Learning",
        "System Design",
        "Distributed Systems",
        "Operating Systems",
        "Database Management Systems",
    },
}


KNOWN_SKILLS = {
    skill
    for category in SKILLS.values()
    for skill in category
}
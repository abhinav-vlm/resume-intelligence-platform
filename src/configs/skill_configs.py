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
}


KNOWN_SKILLS = {
    skill
    for category in SKILLS.values()
    for skill in category
}
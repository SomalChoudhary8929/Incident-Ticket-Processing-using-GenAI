# ai-svc-INTERN-IncidentTicketsProcessing
# 🚑 AI Incident Ticket Processing Service

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Contributions](https://img.shields.io/badge/contributions-welcome-orange)](#-contributing)
[![Repo](https://img.shields.io/badge/repo-RPI--GROUP--AI--Lab%2Fai--svc--INTERN--IncidentTicketsProcessing-purple)](https://github.com/RPI-GROUP-AI-Lab/ai-svc-INTERN-IncidentTicketsProcessing)

> 🤖 Automating **incident ticket management** using **AI-powered NLP & ML** to classify, prioritize, and route support tickets with speed & precision.

---

##  Overview

The **AI Incident Ticket Processing Service** streamlines helpdesk operations by applying **machine learning** and **natural language processing** to incoming support/incident tickets.  

✅ Faster response times  
✅ Accurate categorization  
✅ Smart prioritization & routing  
✅ Scalable & extensible backend  

---

##  Features

-  **Automatic Ticket Categorization**  
  Classifies incoming tickets using AI-driven models.  

-  **Priority & Urgency Detection**  
  Detects severity and assigns priorities based on ticket context.  

-  **Routing & Assignment**  
  Suggests or auto-assigns tickets to relevant teams/agents.  

-  **Extensible Architecture**  
  Integrates easily with existing support platforms or custom frontends.  

---

##  Technology Stack

- **Languages**: Python 
- **AI/ML**: `scikit-learn`, `spaCy`, `transformers`, `LangChain`, `OpenAI API`  
- **Frameworks/Tools**: `FastAPI` / `Flask`, `Celery`, `Docker`, `PostgreSQL`  

---

##  Setup

###  Prerequisites
- Python **3.8+**  
- [pip](https://pip.pypa.io/en/stable/) or [conda](https://docs.conda.io/)  
- (Optional) [Docker](https://www.docker.com/)  

###  Installation

```bash
# Clone the repository
git clone https://github.com/RPI-GROUP-AI-Lab/ai-svc-INTERN-IncidentTicketsProcessing.git
cd ai-svc-INTERN-IncidentTicketsProcessing

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Set environment variables in .env or export manually:

- OPENAI_API_KEY=your_openai_key_here
  
- DATABASE_URL=your_database_url_here

### Running the Service
Navigate to /'langgraph developement' folder and run the backend server
```bash
python3 app.py
```
### Contributing

We ❤️ contributions!

- Fork the repo
- Create your branch (git checkout -b feature-name)
- Commit changes (git commit -m 'Add feature')
- Push (git push origin feature-name)
- Open a PR

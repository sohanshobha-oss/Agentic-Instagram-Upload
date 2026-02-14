Agentic Instagram Upload BOT

An AI-powered Instagram automation system that generates content and posts automatically.


## Features

- AI Content Generation
- Instagram Auto Upload
- AWS S3 Integration
- Tavily & Serper Search
- Replicate AI Support
- Modular Architecture
- Docker Support

---

## Project Structure

```
GIT-INSTAPOST/
│
├── src/
│   ├── AWS_S3Upload.py
│   ├── instagram_api.py
│   ├── Replicate.py
│   ├── TavilySearch.py
│   ├── GSerper.py
│   ├── Decider.py
│
├── agent_graph.py
├── app.py
├── Dockerfile
├── pyproject.toml
├── requirements
├── .env
└── README.md
```

---

## Tech Stack

- Python
- Streamlit UI
- AWS S3
- Instagram API
- Replicate AI
- Tavily API
- Serper API
- Docker

---

## Setup

### Clone Repository

```
git clone https://github.com/YOUR_USERNAME/git-instapost.git
cd git-instapost
```

### Install Dependencies

```
pip install -r requirements
```

### Add Environment Variables

Create `.env`:

```
IG_USERNAME=your_username
IG_PASSWORD=your_password
AWS_ACCESS_KEY=your_key
AWS_SECRET_KEY=your_secret
REPLICATE_API_TOKEN=your_token
TAVILY_API_KEY=your_key
SERPER_API_KEY=your_key
```

### Run Application

```
streamlit run app.py
```

---

## 🐳 Docker

```
docker build -t instapost .
docker run --env-file .env instapost
```

---

## 👨‍💻 Author

Sohan K  
Automation & AI Developer

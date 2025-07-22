# GitHub Issue Analyzer

An AI-powered web app that helps you understand, classify, and prioritize GitHub issues using Google's Gemini LLM.



---

## Overview 🚀

The **GitHub Issue Analyzer** enables developers, maintainers, and open-source contributors to:

- Understand issue summaries at a glance  
- Classify issues as bugs, features, docs, or questions  
- Get AI-suggested priority scores  
- Recommend practical GitHub labels  
- See potential user impact  

Powered by [Gemini LLM](https://ai.google.dev/) and integrated with the GitHub API.

---

## Tech Stack

| Frontend  | Backend   | AI Model  | API |
|-----------|-----------|-----------|-----|
| React + TypeScript | FastAPI + Pydantic | Gemini 1.5 Flash | GitHub REST v3 |

---

## Features

- Gemini LLM integration (Google Generative AI)
- GitHub issue & comment fetcher
- AI-driven classification (bug, doc, feature, etc.)
- Priority scoring system (1–5)
- Label & impact suggestions
- GitHub-style frontend UI
- Error handling for missing/invalid issues
- Fully CORS-enabled API

---

## Installation

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # or source venv/bin/activate (Linux/macOS)
pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_google_gemini_key_here
# Optional
GITHUB_TOKEN=your_personal_access_token
```

Start server:

```bash
uvicorn main:app --reload
```

API runs on: `http://localhost:8000`

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: `http://localhost:5173`

---

## API Usage

**POST** `/analyze`

**Request Body**:

```json
{
  "repo_url": "https://github.com/facebook/react",
  "issue_number": 12345
}
```

**Response**:

```json
{
  "summary": "...",
  "type": "bug",
  "priority_score": "4 - High impact on UX",
  "suggested_labels": ["bug", "ux"],
  "potential_impact": "Affects onboarding"
}
```

---

## Sample Inputs for Testing 🧪

| Repository | Issue # | Example |
|------------|---------|---------|
| [react](https://github.com/facebook/react) | 21787 | Bug in state handling |
| [vscode](https://github.com/microsoft/vscode) | 191814 | Log formatting fix |
| [scikit-learn](https://github.com/scikit-learn/scikit-learn) | 27187 | Docs dropdown improvement |
| [tensorflow](https://github.com/tensorflow/tensorflow) | 64444 | FFI API enhancement |

---

## Project Structure

```
GitHub-Issue-Analyzer/
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── .env
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── public/
└── README.md
```

---

## .gitignore (backend)

```
__pycache__/
.env
venv/
*.pyc
*.log
```

---

## License

MIT License © 2025 [Niel Abhishek J David](https://github.com/Nieldave)

---

## Credits

- [Google Gemini API](https://ai.google.dev/)
- [GitHub REST API](https://docs.github.com/en/rest)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)

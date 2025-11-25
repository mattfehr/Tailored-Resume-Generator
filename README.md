# ResuMatch AI

**AI-powered resume tailoring platform** that helps job seekers automatically rewrite their resumes to match a target job posting using Natural Language Processing (NLP) and Large Language Models (LLMs).  

This is the **MVP prototype** for the CECS 451 term project. It implements:
- Resume & job description upload  
- Keyword extraction (TF-IDF + NER)  
- AI-powered resume rewriting (Gemini API)  
- ATS match scoring (cosine similarity)  
- A React frontend for uploading and reviewing tailored resumes  

---

## Tech Stack

**Frontend:** React (Vite or Next.js)  
**Backend:** **FastAPI** (Python 3.10+)  
**AI:** Google Gemini API (LLM for rewriting)  
**NLP:** spaCy, scikit-learn (TF-IDF, cosine similarity)  
**Data Extraction:** pdfminer.six, docx2txt  

---

## Repository Structure

```
backend/
│
├── app/
│   ├── main.py                    # FastAPI entry point
│   ├── __init__.py                # Marks app as a package
│   │
│   ├── routes/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── health.py              # Health-check endpoint
│   │   └── resume_routes.py       # Resume upload, rewrite, and scoring routes
│   │
│   ├── services/                  # Core backend logic
│   │   ├── __init__.py
│   │   ├── parsing_service.py     # PDF/DOCX → text extraction
│   │   ├── keyword_service.py     # TF-IDF + NER keyword extraction
│   │   ├── latex_service.py       # LaTeX resume wrapper and formatting
│   │   ├── rewrite_service.py     # Gemini API rewriting logic
│   │   └── score_service.py       # ATS score computation (cosine similarity)
│   │
│   ├── utils/                     # Helper functions and configuration
│   │   ├── __init__.py
│   │   └── config.py              # Environment variables and constants
│   │
│   └── requirements.txt           # Python dependencies
│
├── tests/                         # Unit tests for backend services and routes
│
├── .env                           # Environment configuration (API keys, etc.)
│
└── README.md                      # Backend documentation

frontend/
│
├── app/                            # Next.js App Router structure
│   ├── layout.tsx                  # Root layout (applied to all pages)
│   ├── globals.css                 # Global Tailwind and theme styles
│   │
│   ├── page.tsx                    # Home page (resume upload + rewrite UI)
│   │
│   ├── login/                      # Login route
│   │   └── page.tsx
│   │
│   └── saved/                      # Saved resumes / rewrites
│       └── page.tsx
│
├── components/                     # Reusable UI components
│   └── UploadForm.tsx              # Resume + job description upload form
│
├── lib/                            # API and utility modules
│   └── api.ts                      # Axios-based API client for backend routes
│
├── public/                         # Static assets (favicon, images)
│   └── favicon.ico
│
├── .gitignore                      # Git ignored files
├── eslint.config.mjs               # ESLint configuration
├── next.config.ts                  # Next.js configuration
├── next-env.d.ts                   # Next.js TypeScript definitions
├── package.json                    # Frontend dependencies and scripts
├── package-lock.json               # Dependency lockfile
├── postcss.config.mjs              # PostCSS + Tailwind setup
├── tsconfig.json                   # TypeScript configuration
└── README.md                       # Frontend documentation

data/
├── sample_resumes/   # Sample PDFs or text resumes
├── sample_jobs/      # Example job descriptions
└── mock_outputs/     # Example rewritten resumes or ATS reports

docs/
├── architecture_diagram.md
├── api_reference.md
└── setup_guide.md

.gitignore
LICENSE
README.md
```

---

## Setup Instructions

### **Backend Setup**

```bash
cd backend

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # On Windows (PowerShell): venv\Scripts\Activate.ps1

# Install dependencies into the venv
pip install -r app/requirements.txt # After installing, run: python -m spacy download en_core_web_sm
```

Create a `.env` file in `backend/`:
```
GEMINI_API_KEY=your_api_key_here
ENV=development
```

Run the FastAPI backend:
```bash
uvicorn app.main:app --reload
```

Your backend will run at:
```
http://127.0.0.1:8000
```

Swagger API docs:
```
http://127.0.0.1:8000/docs
```

---

### **Frontend Setup**

```bash
cd frontend
npm install
npm run dev
```

Frontend will typically run on:
```
http://localhost:5173
```

CORS is already enabled for this origin in the backend configuration.

---

## Running Tests

From the backend root:
```bash
pytest
```

You can add more tests in `backend/tests/` to validate each service independently (parsing, rewriting, scoring).

---

## Environment Variables

| Variable | Description |
|-----------|-------------|
| `GEMINI_API_KEY` | Your Google Gemini API key |
| `ENV` | Application environment (development / production) |

---

## MVP Core Flow

1. **User uploads** a resume (PDF/DOCX) and a job description.  
2. **Backend extracts** text and keywords using TF-IDF + NER.  
3. **Gemini API** rewrites the resume to emphasize matching skills.  
4. **ATS score** is computed using cosine similarity.  
5. **Frontend displays** tailored resume and score, with download/export options.  

---

## Future Expansion

- User accounts (store verified experiences, projects, and skills)  
- Vector database integration for contextual resume generation  
- Multi-section resume formatting (Education, Projects, Skills)  
- Bias & clarity checker  
- Export templates (LaTeX, HTML, or custom PDF styles)

---

## Contributing

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Commit changes with clear messages.
3. Push and open a pull request.

---

## Authors

- **Team ResuMatch AI** – CECS 451, Fall 2025  
- Original concept & architecture by: *Matthew Fehr, Angelo Cervana, & Marissa Marcarelli*

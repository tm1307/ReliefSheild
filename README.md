# ReliefShield 🛡️

**Trust Verification Platform for Emergency Donation Appeals**

ReliefShield is an end-to-end verification platform designed to combat fraudulent donation appeals during natural disasters and emergencies. By analyzing text, links, and screenshots, it assigns a deterministic **Trust Score** and generates an explainable **Evidence Graph** to help donors make safe, informed decisions.

Built for the **Omni_DisasterMgmt_18** problem statement.

## 🚀 Features

*   **Multi-Format Ingestion:** Process direct text, URLs (with auto-scraping), and screenshots (via OCR).
*   **5-Pillar Verification Pipeline:**
    *   **Extraction:** Uses NLP (spaCy) and OCR (Tesseract) to extract entities (NGO names, locations, payment IDs).
    *   **Identity:** Verifies organizations against known registries (e.g., NGO Darpan).
    *   **Payment:** Detects personal UPI IDs masquerading as official NGO accounts.
    *   **Similarity:** Identifies recycled scam appeals and reused images using Perceptual Hashing.
    *   **Claims:** Validates factual claims (e.g., FCRA registration, government approvals).
*   **Explainable Evidence Graph:** A visual node-tree that maps entities and highlights contradictions, ensuring the AI's decision is 100% transparent.
*   **Shareable Reports:** 1-click clipboard export to share trust scores and warnings on social media platforms like WhatsApp.

## 💻 Tech Stack

*   **Frontend:** React 18, Vite, TailwindCSS, Lucide Icons
*   **Backend:** Python 3.10+, FastAPI (Async)
*   **Database:** SQLite (aiosqlite) with SQLAlchemy ORM
*   **AI & Processing:**
    *   `spaCy` (Named Entity Recognition)
    *   `pytesseract` (Optical Character Recognition)
    *   `imagehash` (Perceptual Hashing)
    *   `BeautifulSoup4` (Web scraping)

## 🛠️ Local Setup Instructions

### 1. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Download the spaCy NLP model
python -m spacy download en_core_web_sm

# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```
*The backend will be available at `http://localhost:8000`*

### 2. Frontend Setup

Open a new terminal window:

```bash
cd frontend

# Install dependencies
npm install

# Start the Vite development server
npm run dev
```
*The frontend will be available at `http://localhost:5173`*

## 📝 Attributions
*   **Core Architecture:** The verification logic, scoring engine, evidence graph, and user interfaces are original code built for this hackathon.
*   **Open Source:** We utilized `spaCy` for foundational NLP and `Tesseract` for OCR capabilities.

## 📄 License
MIT License

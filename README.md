# ReliefShield

ReliefShield is a Trust Verification Platform for Emergency Donation Appeals.
This project tackles the **Omni_DisasterMgmt_18** problem statement.

## The Approach: Why This Will Win

Most hackathon projects dealing with "authenticity verification" fall into the trap of being a simple LLM wrapper (e.g., passing text to GPT-4 and asking "Is this a scam?"). 
**ReliefShield takes a robust, deterministic approach:**
1. **Does Not Give Away Its AI:** AI is used only for specific utilities (OCR for image reading, NLP for extracting NGO names/UPI IDs, and Embeddings/Perceptual Hashing for similarity search).
2. **Proper Implementation:** The decision logic is handled by a transparent, rule-based **Scoring Engine** and an **Evidence Graph**. This ensures that every point deducted from a trust score is 100% explainable to the user, a critical requirement for a public safety tool.
3. **Solves a Real Problem:** During disasters (floods, earthquakes), malicious actors recycle old campaign images and change the UPI IDs. ReliefShield's **Similarity Module** combined with the **Payment Consistency Module** catches this exact vector instantly.

## Architecture

- **Backend:** FastAPI (async), Python 3.10+
- **Database:** PostgreSQL with `pgvector` for similarity matching
- **Frontend:** React + TailwindCSS (mobile-first)

## Modules
- `IdentityModule`: Checks NGO registries and domain WHOIS data.
- `PaymentModule`: Cross-references extracted UPI/bank details against the claimed NGO name.
- `SimilarityModule`: Uses Perceptual Hashing (pHash) for images to detect recycled campaigns.
- `ScoringEngine`: Aggregates the flags into a 0-100 Trust Score.

## Getting Started

1. Start the database: `docker-compose up -d`
2. Install dependencies: `cd backend && pip install -r requirements.txt`
3. Run the API: `uvicorn app.main:app --reload`

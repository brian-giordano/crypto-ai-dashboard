# Vision Crypto AI Dashboard

A modern full-stack cryptocurrency dashboard with AI-powered insights. Built as a portfolio project to demonstrate clean architecture, real-time data handling, and thoughtful UX decisions.

**[View Live Demo →](https://crypto-ai-dashboard-lovat.vercel.app/)**

## ✨ Features

- Real-time cryptocurrency market data with interactive charts
- AI assistant ("Vision") that answers natural language questions
- Personalized dashboard – save and track your favorite coins
- Fully responsive design with dark/light mode
- Instant-loading **Demo Mode** for the best portfolio viewing experience

## 🧪 Demo Mode

This live demo uses **instant mock data** so it loads lightning-fast with zero delays.  
The full backend (FastAPI + Celery) is available in the `/backend` folder and can be run locally or deployed for live data.

## Tech Stack

**Frontend**

- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS + shadcn/ui
- Zustand + TanStack Query
- Recharts

**Backend** (optional)

- FastAPI (Python)
- Celery + Redis

## Getting Started

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend (optional)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

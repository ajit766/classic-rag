# Deployment Guide: "The Modern Sage"

This guide outlines how to deploy the application for free using **Render** (Backend) and **Vercel** (Frontend).

## Prerequisites
*   GitHub Account (to push your code).
*   Accounts on [Render.com](https://render.com) and [Vercel.com](https://vercel.com).
*   API Keys ready (`OPENAI_API_KEY`, `PINECONE-API-KEY`, `COHERE_API_KEY`).

---

## Part 1: Prepare the Codebase

### 1. Backend Preparation
Ensure your `backend/requirements.txt` is up to date.
The start command will be:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```
(Render automatically sets `$PORT`).

### 2. Frontend Connection
The frontend needs to know where the backend lives.
Currently, `frontend/components/ChatInterface.tsx` likely points to `http://localhost:8000`.
**Action Required**: We need to make the API URL configurable.

**Step 2.1**: Update `frontend/components/ChatInterface.tsx` (or where the fetch call happens).
Instead of hardcoding the URL, use an environment variable or a relative path if using a proxy.
*   *Recommended for Vercel*: Use an environment variable `NEXT_PUBLIC_API_URL`.

---

## Part 2: Deploy Backend (Render)

1.  **Push your code** to a GitHub repository (if not already there).
2.  Log in to **RenderDashboard**.
3.  Click **New +** -> **Web Service**.
4.  Connect your GitHub repository.
5.  **Settings**:
    *   **Name**: `modern-sage-backend`
    *   **Root Directory**: `backend` (Important!)
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
    *   **Instance Type**: `Free`
6.  **Environment Variables** (Advanced):
    Add the following keys:
    *   `OPENAI_API_KEY`: `sk-...`
    *   `PINECONE-API-KEY`: `pc-...`
    *   `COHERE_API_KEY`: `...`
    *   `PINECONE_ENV`: `us-east-1` (or whatever your env is)
    *   `LANGFUSE_SECRET_KEY`: `sk-lf-...`
    *   `LANGFUSE_PUBLIC_KEY`: `pk-lf-...`
    *   `LANGFUSE_HOST`: `https://cloud.langfuse.com`
7.  Click **Create Web Service**.

*Note: Free tier spins down after 15 minutes of inactivity. The first request might take 50 seconds to wake it up.*

---

## Part 3: Deploy Frontend (Vercel)

1.  Log in to **Vercel Dashboard**.
2.  Click **Add New...** -> **Project**.
3.  Import the same GitHub repository.
4.  **Settings**:
    *   **Framework Preset**: Next.js
    *   **Root Directory**: `frontend` (Important: Click 'Edit' next to Root Directory and select `frontend`).
5.  **Environment Variables**:
    *   `NEXT_PUBLIC_API_URL`: `https://your-render-backend-name.onrender.com/api/chat`
        *(You get this URL after the Render deploy is live)*.
6.  Click **Deploy**.

---

## Part 4: Final Config (CORS)

Once Vercel is deployed, you will get a URL like `https://modern-sage.vercel.app`.

1.  Go back to **Render** -> **Environment Variables**.
2.  (Optional) If you enforced CORS strictness in `main.py`, update it. currently it allows `["*"]` so it should work out of the box.

## Summary of URLs
*   **Live App**: `https://modern-sage.vercel.app`
*   **Backend API**: `https://modern-sage-backend.onrender.com`

---

## Part 5: CI/CD (Automatic Updates)
Yes, Continuous Deployment is built-in!

1.  **How it works**:
    *   Both Vercel and Render are connected to your GitHub repository.
    *   Whenever you `git push origin main`, they receive a "Webhook" from GitHub.
    *   **Vercel**: Immediately rebuilds and redeploys the frontend (takes ~1 min).
    *   **Render**: Detects the change, pulls the new code, pip installs requirements, and restarts the server (takes ~2-3 mins).

2.  **Workflow**:
    *   Make changes locally.
    *   Test with `npm run dev` and `uvicorn`.
    *   Commit and Push:
        ```bash
        git add .
        git commit -m "New feature"
        git push origin main
        ```
    *   **Done!** Your live site will update automatically in a few minutes.

# Deploying the AgriPredict Backend

This document contains step-by-step instructions to deploy the FastAPI backend to free hosts (Render / Railway) and notes for Vercel environment configuration.

Prerequisites

- Push this repository to GitHub (or ensure it's in a Git remote accessible by Render/Railway).

Files added

- `requirements.txt` - Python dependencies.
- `Procfile` - run command for platform hooks.
- `Dockerfile` - optional container deployment.

Render (recommended quick deploy)

1. Create a free account at https://render.com
2. Connect your GitHub account and find this repository.
3. Click New → Web Service.
4. Select the repo and branch. Set the Root to `AGRI-Tecno/PythonProject7 (1)/PythonProject7` if Render asks for a subdirectory.
5. Build Command: leave empty (Render will use `pip install -r requirements.txt` if detected). If required, use:
   - `pip install -r requirements.txt`
6. Start Command:
   - `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Add environment variables in the Render dashboard:
   - `PYTHONUNBUFFERED=true` (optional)
   - Any API keys your app needs
8. Deploy. Render will provide a public `https://<service>.onrender.com` URL. Use that as your `VITE_API_BASE` in Vercel.

Railway (alternative)

1. Create a free account at https://railway.app
2. Create a new project → Deploy from GitHub.
3. Select the repository and set the project root path to `AGRI-Tecno/PythonProject7 (1)/PythonProject7`.
4. Railway will auto-detect Python and use the `requirements.txt` to install dependencies.
5. Set the Start Command to:
   - `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Railway will provide a public URL `https://<project>.railway.app` — set `VITE_API_BASE` to that value.

Notes for Vercel

- Vercel cannot access `http://127.0.0.1:8000`. Use the public backend URL from Render/Railway.
- In the Vercel Project → Settings → Environment Variables, set:
  - Key: `VITE_API_BASE`
  - Value: `https://<your-backend-url>`
  - Environment: Production (and Preview/Development as needed)
- Redeploy the Vercel project after adding env variables.

CORS

- `main.py` already includes `CORSMiddleware` with `allow_origins` set to include localhost and wildcard `"*"`. In production, replace `"*"` with your frontend domain for security.

Testing locally after deploy

- Once you have the public backend URL `https://my-backend.example.com`, verify:
  - `curl https://my-backend.example.com/health`
  - `curl -X POST 'https://my-backend.example.com/predict-soil' -F "file=@test.jpg;type=image/jpeg"`

If you want, I can prepare a GitHub Actions workflow or a `render.yaml` manifest — tell me which host you prefer and I will add it.

# Deployment

## Backend on Render

1. Create a new Render Web Service.
2. Set the root directory to the repository root.
3. Use Docker deployment with the root `Dockerfile`.
4. Add environment variables from `configs/.env.example`.
5. Mount persistent storage for `/app/data` if you want indexes to survive deploys.

## Frontend on Vercel

1. Import the GitHub repository into Vercel.
2. Set the project root to `frontend`.
3. Add `NEXT_PUBLIC_API_BASE_URL` pointing to the deployed FastAPI URL.
4. Deploy with the default Next.js build command.

## Local Docker

```bash
docker compose up --build
```

The backend will run at `http://localhost:8000` and the frontend at `http://localhost:3000`.

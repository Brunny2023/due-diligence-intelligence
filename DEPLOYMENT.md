# Deployment

The showcase is a small Python HTTP service and can run on any host that supports Python 3.10+. Start it with `python3 -m app.api.server`; bind port 8000 and expose `/demo`. This repository does not claim a production deployment or persistent hosted Pinecone index.

For live mode, inject environment variables from a secret manager. Do not place keys in HTML, JavaScript, Git history, or `.env.example`. Keep Pinecone and LLM calls server-side. The checked-in synthetic case is safe for demonstration; do not upload confidential diligence materials.

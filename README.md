3 Containers template repo

1. Next.js frontend
2. Server flask-python backend
3. chromadb vector db

frontend can communicate with backend see page.js and next.config.mjs
backend accesses chroma through network bridge see docker-compose.yml and parser.py


To run
1. export OPEN_AI_KEY= (your key)
2. docker-compose up --build


This may be discontinued as this approach isn't the best for my product but feel free to fork. 
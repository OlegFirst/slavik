FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    fastapi uvicorn psycopg2-binary redis

COPY . .

RUN echo 'from fastapi import FastAPI\napp = FastAPI()\n@app.get("/health")\ndef health(): return {"status": "ok"}\nif __name__ == "__main__":\n  import uvicorn\n  uvicorn.run(app, host="0.0.0.0", port=8000)' > main.py

CMD ["python", "main.py"]

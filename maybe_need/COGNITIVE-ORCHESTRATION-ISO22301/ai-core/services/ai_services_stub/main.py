from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "PDCA AI Assistant Service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)
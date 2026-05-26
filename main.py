from fastapi import FastAPI

app = FastAPI(title="Enterprise RAG System")

@app.get("/")
def root():
    return {"message": "Enterprise RAG System Running"}

from fastapi import FastAPI

app = FastAPI(
    title = "PDF Summarizer FastAPI",
    description = "A production-ready API for uploading and summarizing PDFs",
    version = "0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "PDF Summarizer API is running"}

@app.get("/health")
def health_check():
    return {"status": "Ok"}

@app.get("/about")
def about():
    return {"Project Name":"PDF Summarizer API","Description": "A producton-ready API for uploading and summarizing PDFs","version":"0.1.0"}


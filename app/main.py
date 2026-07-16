from fastapi import FastAPI,HTTPException

app = FastAPI(
    title = "PDF Summarizer FastAPI",
    description = "A production-ready API for uploading and summarizing PDFs",
    version = "0.1.0"
)

fake_pdfs_db = {1:{"filename":"resume","pages":1},2:{"filename":"Research_paper","pages":40}}


@app.get("/")
def read_root():
    return {"message": "PDF Summarizer API is running"}


@app.get("/health")
def health_check():
    return {"status": "Ok"}

@app.get("/pdfs/count")
def get_count():
    return len(fake_pdfs_db)


@app.get("/pdfs/{pdf_id}")
def get_pdf(pdf_id : int):
    if pdf_id not in fake_pdfs_db:
        raise HTTPException(status_code = 404,detail = "PDF not found")
    
    return fake_pdfs_db[pdf_id]


@app.get("/pdfs/{pdf_id}/summary")
def get_summary(pdf_id:int):
    if pdf_id not in fake_pdfs_db:
        raise HTTPException(status_code = 404,detail = "PDF not found")
    filename = fake_pdfs_db[pdf_id]["filename"]
    return {"pdf_id": pdf_id, "summary": f"This is a placeholder summary for {filename}"}


@app.delete("/pdfs/{pdf_id}")
def delete_pdf(pdf_id:int):
    if pdf_id not in fake_pdfs_db:
        raise HTTPException(status_code = 404,detail = "PDF not found")
    del fake_pdfs_db[pdf_id]
    return {"message":"PDF Deleted Successfully"}


@app.get("/about")
def about():
    return {"Project Name":"PDF Summarizer API","Description": "A producton-ready API for uploading and summarizing PDFs","version":"0.1.0"}



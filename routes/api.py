import mimetypes
import os

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from models.models import Job
from models.database import SessionLocal
from pathlib import Path
from typing import Optional
import uuid
import shutil
import threading
import logging
from services.processing import process_pdf


router = APIRouter()

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("processed_pdfs")

@router.post("/upload/")
def upload_pdf(file: UploadFile = File(...)):
    # Check if file type is PDF
    mime_type, _ = mimetypes.guess_type(file.filename)
    if mime_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")

    with SessionLocal() as db:
        job_id = str(uuid.uuid4())
        Job.create(db, job_id)

    input_path = os.path.join(UPLOAD_DIR ,f"{job_id}.pdf")
    with SessionLocal() as db:
        Job.update_input_path(db, job_id=job_id, input_path=str(input_path))

    output_path = os.path.join(OUTPUT_DIR ,f"{job_id}_processed.pdf")

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    threading.Thread(target=process_pdf, args=(input_path, output_path, job_id)).start()

    return {"job_id": job_id}


@router.get("/status/{job_id}")
def check_status(job_id: str):
    with SessionLocal() as db:
        job = Job.get_job(db, job_id)
        if not job:
            return {"error": "Job not found"}
        return {"status": job["status"]}


@router.get("/download/{job_id}")
def download_pdf(job_id: str):
    with SessionLocal() as db:
        job = Job.get_job(db, job_id)
        if not job or job["status"] != "completed":
            return {"error": "Job not completed or not found"}
        return FileResponse(job["output_path"], media_type='application/pdf', filename=f"{job_id}_processed.pdf")


@router.get("/jobs")
def list_jobs(from_date: Optional[str] = Query(None, alias="from"), to_date: Optional[str] = Query(None, alias="to")):
    with SessionLocal() as db:
        jobs = Job.get_filtered(db, from_date, to_date)
        return jobs


@router.post("/retry/{job_id}")
def retry_job(job_id: str):
    with SessionLocal() as db:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.status != "failed":
            raise HTTPException(status_code=400, detail="Only failed jobs can be retried")

        job.status = "retrying"
        input_path = job.input_path
        output_path = os.path.join(OUTPUT_DIR , f"{job_id}_processed.pdf")
        db.commit()

    threading.Thread(target=process_pdf, args=(input_path, output_path, job_id)).start()

    return {"message": f"Retrying job {job_id}"}

@router.get("/preview/{job_id}")
def preview_pdf(job_id: str):
    with SessionLocal() as db:
        job = Job.get_job(db, job_id)
        if not job or job["status"] != "completed":
            raise HTTPException(status_code=404, detail="Job not completed or not found")

        return FileResponse(
            job["output_path"],
            media_type='application/pdf',
            filename= f"{job_id}_processed.pdf",
            headers={"Content-Disposition": "inline; filename=printable.pdf"}
        )
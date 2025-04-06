import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from main import app
from routes.api import UPLOAD_DIR, OUTPUT_DIR
from models.database import SessionLocal
from models.models import Job

client = TestClient(app)

# Fixture to clean up files after test
@pytest.fixture(autouse=True)
def cleanup_files():
    yield
    for folder in [UPLOAD_DIR, OUTPUT_DIR]:
        for f in folder.glob("*.pdf"):
            f.unlink()


def test_upload_pdf_creates_job_and_starts_processing():
    # Create a dummy PDF file in memory
    fake_pdf = io.BytesIO(b"%PDF-1.4\n%Fake PDF file\n1 0 obj\n<<>>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<<>>\nstartxref\n0\n%%EOF")

    response = client.post(
        "/upload/",
        files={"file": ("test.pdf", fake_pdf, "application/pdf")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data

    job_id = data["job_id"]

    # Check that the job was created in the DB
    with SessionLocal() as db:
        job = Job.get_job(db, job_id)
        assert job is not None
        assert job["status"] in ["processing", "completed", "failed"]

    # Check that input file was saved
    input_path = UPLOAD_DIR / f"{job_id}.pdf"
    assert input_path.exists()




# Test that only PDF files are allowed
def test_upload_only_pdf():
    # Create a fake non-PDF file (txt)
    fake_txt = io.BytesIO(b"This is a fake text file.")

    response = client.post(
        "/upload/",
        files={"file": ("test.txt", fake_txt, "text/plain")}
    )

    # Assert that the upload fails for non-PDF file type
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid file type. Only PDF files are allowed."}

    # Create a fake PDF file
    fake_pdf = io.BytesIO(
        b"%PDF-1.4\n%Fake PDF file\n1 0 obj\n<<>>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<<>>\nstartxref\n0\n%%EOF")

    response = client.post(
        "/upload/",
        files={"file": ("test.pdf", fake_pdf, "application/pdf")}
    )

    # Assert that the upload succeeds for PDF file
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data  # Ensure the job_id is returned


import pytest
from fastapi.testclient import TestClient
import os
import time
import fitz  # PyMuPDF
from io import BytesIO
from services.processing import process_pdf

# Helper function to check if a QR code exists on each page of the PDF
def check_qr_code_in_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    qr_found = True
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        # print(f"Page {page_num} text: {text}")  # Debug print for text content

        # Debugging the images on the page (check if the QR code is inserted as an image)
        images = page.get_images(full=True)
        # print(f"Page {page_num} images: {images}")  # Debug print for image info

        if not images:  # If no images found, assume QR code is not present
            qr_found = False
            break
    return qr_found


# Test case to simulate processing and QR code check
@pytest.mark.parametrize("file_name", ["test1.pdf"])  # Example file name
def test_process_pdf_and_check_qr_code(file_name):
    # Simulate reading the test PDF file (you can add any file you need for testing)
    parentFolder = os.path.join(Path(__file__).parent,"test_pdfs")
    outputFolder=  os.path.join(Path(__file__).parent,"processed_pdfs")
    with open(os.path.join(parentFolder,"test1.pdf"), "rb") as f:
        pdf_file = BytesIO(f.read())  # Read the file into memory

        # Simulate job ID creation and processing (skip the upload route)
        job_id = "dummy-job-id"  # You can use any job ID or generate one
        input_path = os.path.join(parentFolder,"test1.pdf")   # Simulated path
        output_path = os.path.join(outputFolder,f"{job_id}_processed.pdf")  # Simulated output path

        # Save the PDF file to the simulated input path
        with open(input_path, "wb") as buffer:
            buffer.write(pdf_file.getvalue())

        # Directly call the process_pdf function (bypassing upload)
        process_pdf(input_path, output_path, job_id)

    # Check if the processed PDF contains a QR code
    assert check_qr_code_in_pdf(output_path), "QR code not found on all pages in the processed PDF"

    # Clean up - Remove the processed file after test
    os.remove(output_path)

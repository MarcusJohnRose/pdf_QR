import fitz  # PyMuPDF
import qrcode
import logging
from io import BytesIO
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from models.database import SessionLocal
from models.models import Job

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def process_page(doc, page_num, job_id):
    try:
        page = doc.load_page(page_num)
        text = page.get_text("text")

        for line in text.split("\n"):
            if "#" in line:
                qr_img = qrcode.make(line.split("#")[1].strip())
                buffer = BytesIO()
                qr_img.save(buffer, format="PNG")
                buffer.seek(0)

                qr_width = 80
                x_center = page.rect.width / 2
                rect = fitz.Rect(x_center - qr_width / 2, 20, x_center + qr_width / 2, 100)

                page.insert_image(rect, stream=buffer.getvalue())
                break
    except Exception as e:
        logging.error(f"Error processing page {page_num}: {e}")


def process_pdf(file_path: Path, output_path: Path, job_id: str):
    try:
        logging.info(f"Processing PDF: {file_path}")
        doc = fitz.open(str(file_path))

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_page, doc, i, job_id) for i in range(len(doc))]
            for f in futures:
                f.result()

        doc.save(str(output_path))
        doc.close()

        with SessionLocal() as db:
            Job.update_status(db, job_id, status="completed", output_path=str(output_path))

        logging.info(f"Finished processing: {output_path}")
    except Exception as e:
        logging.error(f"Error processing PDF: {e}")
        with SessionLocal() as db:
            Job.update_status(db, job_id, status="failed")

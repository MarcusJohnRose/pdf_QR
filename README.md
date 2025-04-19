# 📄 PDF QR Processor

A sleek FastAPI-based web app for uploading, processing, and printing PDFs with optional QR code manipulation. Features include drag-and-drop upload, auto-download, auto-print, a jobs history log, and configurable backend settings — all wrapped in a modern UI.

---

## 🚀 Features

- ⚡ Fast PDF upload and processing
- 🖨️ Auto-download and optional print preview
- 🧲 Drag-and-drop upload UX
- 🧠 Configurable backend settings via UI
- 🕒 Job history with timestamps in your local timezone
- 🎨 Clean, TailwindCSS-powered interface

---

## 📦 Requirements

- Python 3.9+
- [Poetry](https://python-poetry.org/) or `pip`
- Node.js (optional, if modifying frontend assets)
  
---

## 🔧 Installation

### 1.Clone the repo and spin up your environment:

```bash
git clone https://github.com/your-username/pdf-qr-processor.git
cd pdf-qr-processor
```
### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```
### 3. Install Python Dependencies
```bash 
pip install -r requirements.txt
```
---

## ▶️ Running the App

### 1. Start the FastAPI Server
```bash
uvicorn main:app --reload
```
This will start the server at: http://127.0.0.1:8000
```bash
uvicorn main:app --reload --host 0.0.0.0
```
This will start the server at: http://127.0.0.1:8000 and will be accessable to any device on the same network

## 🧪 Development Notes
The backend is powered by FastAPI and SQLAlchemy.

Settings are stored in a separate SQLite database (`settings.db`).

Uploaded files are stored temporarily and processed into a `/processed_pdfs/` directory.

Settings can be modified from the `/settings.html` page in your browser.

## ⚙️ Customizing Defaults
To change the default behavior for QR parsing or PDF handling:

Visit the Settings page via the link on the home screen.

Modify predefined values such as:

`qr_code_marker` : Default `#` search string for detecting the Order number

These values are stored in the `settings` table and applied automatically during processing.


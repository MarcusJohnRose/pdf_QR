function autodownloader(downloadUrl) {
  const link = document.createElement("a");
  link.href = downloadUrl;
  link.download = "processed.pdf";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function triggerPrint() {
  const jobId = sessionStorage.getItem("lastJobId");
  if (!jobId) return;

  const iframe = document.createElement("iframe");
  iframe.style.display = "none";
  iframe.src = `/preview/${jobId}`;

  document.body.appendChild(iframe);

  iframe.onload = () => {
    setTimeout(() => {
      try {
        iframe.contentWindow.focus();
        iframe.contentWindow.print();
      } catch (e) {
        console.error("Manual print failed:", e);
      }
    }, 1000);
  };
}

async function uploadPDF(file) {
  const statusDiv = document.getElementById("status");
  const downloadLink = document.getElementById("downloadLink");
  const printLink = document.getElementById("printLink");
  const autoPrint = document.getElementById("autoPrint");
  const autoDownload = document.getElementById("autoDownload").checked;

  const formData = new FormData();
  formData.append("file", file);
  setStatus("Uploading...");

  downloadLink.classList.add("hidden");
  printLink.classList.add("hidden");


  try {
    const res = await fetch("/upload/", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const error = await res.json();
      clearStatusAnimation();
      throw new Error(error.detail || "Upload failed");
    }
    const data = await res.json();
    const jobId = data.job_id;
    sessionStorage.setItem("lastJobId", jobId);
    setStatus("Processing...");

    const interval = setInterval(async () => {
    const statusRes = await fetch(`/status/${jobId}`);
    const statusData = await statusRes.json();

      if (statusData.status === "completed") {
        clearInterval(interval);
        statusDiv.textContent = "✅ Processing complete!";
        const downloadUrl = `/download/${jobId}`;
        downloadLink.href = downloadUrl;

        downloadLink.classList.remove("hidden");
        downloadLink.textContent = "Download PDF";

        // Show the print link
        const printLink = document.getElementById("printLink");
        printLink.classList.remove("hidden");
        printLink.onclick = () => triggerPrint(jobId);
        if (autoDownload) {
          autodownloader(downloadUrl);
        }
        if (autoPrint.checked) {
          triggerPrint(jobId);
        }
        clearStatusAnimation()
      } else if (statusData.status === "failed") {
        clearInterval(interval);
        statusDiv.textContent = "❌ Processing failed.";
      } else {
        setStatus("⏳ Still processing...");
      }
    }, 1500);
  } catch (err) {
  console.error(err);
  const errorDiv = document.getElementById("errorNotification");
  const errorMessage = document.getElementById("errorMessage");

  errorMessage.textContent = `❌ ${err.message}`;
  errorDiv.classList.remove("hidden");

  // Auto-hide after 5 seconds
  setTimeout(() => {
    errorDiv.classList.add("hidden");
  }, 5000);
  }
}

  // Drag & Drop
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("bg-gray-100");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("bg-gray-100");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("bg-gray-100");
    const file = e.dataTransfer.files[0];
    if (file && file.type === "application/pdf") {
      uploadPDF(file);
    } else {
      alert("Please drop a valid PDF file.");
    }
  });

  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (file) {
      uploadPDF(file);
    }
  });

function setStatus(text) {
  const statusDiv = document.getElementById("status");
  const statusZone = document.getElementById("StatusZone");
  const dropZone = document.getElementById("dropZone");
  dropZone.classList.add("hidden")
  statusDiv.innerHTML = ""; // Clear previous content
  statusZone.classList.remove("hidden");
  [...text].forEach((char, i) => {
    const span = document.createElement("span");
    span.textContent = char;
    span.classList.add("status-animate");
    span.style.animationDelay = `${i * 0.05}s`; // Stagger animation
    statusDiv.appendChild(span);
  });
}

function clearStatusAnimation() {
  const statusDiv = document.getElementById("status");
  statusDiv.classList.remove("status-animate");
  const statusZone = document.getElementById("StatusZone");
  statusZone.classList.add("hidden");
  const dropZone = document.getElementById("dropZone");
  dropZone.classList.remove("hidden")
}

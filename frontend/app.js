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

    statusDiv.textContent = "Uploading...";
    downloadLink.classList.add("hidden");
    printLink.classList.add("hidden");


    try {
      const res = await fetch("/upload/", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      const jobId = data.job_id;
      sessionStorage.setItem("lastJobId", jobId);
      statusDiv.textContent = `Processing started. Job ID: ${jobId}`;

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

        } else if (statusData.status === "failed") {
          clearInterval(interval);
          statusDiv.textContent = "❌ Processing failed.";
        } else {
          statusDiv.textContent = `⏳ Still processing...`;
        }
      }, 1500);
    } catch (err) {
      console.error(err);
      statusDiv.textContent = "Error uploading file.";
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

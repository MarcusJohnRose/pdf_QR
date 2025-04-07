
  function autodownloader(downloadUrl){
          const link = document.createElement("a");
          link.href = downloadUrl;
          link.download = "processed.pdf";
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        }



document.getElementById("uploadBtn").addEventListener("click", async () => {
  const fileInput = document.getElementById("fileInput");
  const statusDiv = document.getElementById("status");
  const downloadLink = document.getElementById("downloadLink");
  const autoDownload = document.getElementById("autoDownload").checked;
  const autoPrint = document.getElementById("autoPrint");

  if (!fileInput.files.length) {
    statusDiv.textContent = "Please select a PDF file first.";
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  statusDiv.textContent = "Uploading...";
  downloadLink.classList.add("hidden");

  try {
    const res = await fetch("/upload/", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    const jobId = data.job_id;
    sessionStorage.setItem("lastJobId", jobId);
    statusDiv.textContent = `Processing started. Job ID: ${jobId}`;

    // Polling loop
    const interval = setInterval(async () => {
      const statusRes = await fetch(`/status/${jobId}`);
      const statusData = await statusRes.json();
      const savedId = sessionStorage.getItem("lastJobId");  // Get jobId from sessionStorage (to ensure we're polling for the correct one)


      if (statusData.status === "completed") {
        clearInterval(interval);
        statusDiv.textContent = "✅ Processing complete!";
        downloadLink.href = `/download/${jobId}`;
        downloadLink.classList.remove("hidden");
        downloadLink.textContent = "Download PDF";
        if (autoDownload) {
          autodownloader(downloadLink)
        }
        if (autoPrint.checked) {
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
            console.error("Auto print failed:", e);
          }
          }, 1000); // Give it a sec to fully render
          };
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
});

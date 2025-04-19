
function formatLocalTime(timestamp) {
  const localDate = new Date(timestamp);
  return localDate.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function timeAgo(timestamp) {
  const now = new Date();
  const then = new Date(timestamp);
  const diffMs = now - then;
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins} minutes ago`;
  const diffHrs = Math.floor(diffMins / 60);
  if (diffHrs < 24) return `${diffHrs} hours ago`;
  const diffDays = Math.floor(diffHrs / 24);
  return `${diffDays} days ago`;
}


document.addEventListener("DOMContentLoaded", async () => {
  const jobList = document.getElementById("jobList");
  const searchInput = document.getElementById("searchInput");

  async function loadJobs() {
    const res = await fetch("/jobs");
    const jobs = await res.json();

    jobList.innerHTML = ""; // Clear old items

    jobs.forEach(job => {
      const relative = timeAgo(job.timestamp);
      const fullDate = formatLocalTime(job.timestamp);
      const li = document.createElement("li");
      li.className = "bg-white shadow rounded p-4 flex justify-between items-center";

      const date = new Date(job.timestamp).toLocaleString();

      let actionHTML = "";

      if (job.status === "completed") {
        actionHTML = `<a href="/download/${job.id}" class="text-blue-600 hover:underline">Download</a>`;
      } else if (job.status === "processing") {
        actionHTML = `<span class="text-yellow-500">In Progress</span>`;
      } else if (job.status === "failed") {
        actionHTML = `<button onclick="retryJob('${job.id}')" class="text-red-500 hover:underline">Retry</button>`;
      }

      li.innerHTML = `
        <div>
          <div class="font-medium">Job ID: ${job.id}</div>
<!--          // <div class="text-sm text-gray-500">${date}</div>-->
          <div<span title="${fullDate}" class="text-gray-500">
        ${relative}
        </div></div>
        ${actionHTML}
      `;

      jobList.appendChild(li);
    });
  }

  // Retry function (you'll need an API for this)
  window.retryJob = async function (jobId) {
    const confirmed = confirm(`Retry job ${jobId}?`);
    if (!confirmed) return;

    const res = await fetch(`/retry/${jobId}`, { method: "POST" });
    if (res.ok) {
      alert("Job retry started.");
      loadJobs(); // Reload the list
    } else {
      alert("Failed to retry job.");
    }
  };

  // Search functionality
  searchInput.addEventListener("input", () => {
    const term = searchInput.value.toLowerCase();
    const items = document.querySelectorAll("#jobList li");

    items.forEach(item => {
      const id = item.textContent.toLowerCase();
      item.style.display = id.includes(term) ? "flex" : "none";
    });
  });

  await loadJobs();
});

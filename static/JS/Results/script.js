let currentPrefix = ""

function loadS3(prefix = "") {
  fetch(`/browse-s3?prefix=${encodeURIComponent(prefix)}`)
    .then((res) => res.json())
    .then((data) => {
      currentPrefix = data.prefix
      const contentDiv = document.getElementById("content")
      const breadcrumbDiv = document.getElementById("breadcrumb")
      contentDiv.innerHTML = ""
      breadcrumbDiv.innerHTML = ""

      // Breadcrumb Navigation
      const parts = prefix.split("/").filter(Boolean)
      let pathSoFar = ""
      breadcrumbDiv.innerHTML = `<span onclick="loadS3('')"> <i class="fas fa-home" style="color: #3498db; margin-right: 8px;"></i> Home</span>`

      parts.forEach((part, index) => {
        pathSoFar += part + "/"
        breadcrumbDiv.innerHTML += `<span class="divider">/</span><span onclick="loadS3('${pathSoFar}')">${part}</span>`
      })
      // Folders
      data.folders.forEach((folder) => {
        const folderName = folder.replace(prefix, "").replace(/\/$/, "")
        const folderEl = document.createElement("div")
        folderEl.className = "folder"
        folderEl.innerHTML = `<i class="fas fa-folder" style="color: #f1c40f; margin-right: 8px;"></i> ${folderName}`
        folderEl.onclick = () => loadS3(folder)
        contentDiv.appendChild(folderEl)
      })

      // Files
      data.files.forEach((file) => {
        const fileEl = document.createElement("div")
        fileEl.className = "file"
        fileEl.innerHTML = `<i class="fas fa-file-alt" style="color: #2c3e50; margin-right: 8px;"></i> <a href="${file.url}" target="_blank" download>${file.filename}</a>`
        contentDiv.appendChild(fileEl)
      })

      if (data.folders.length === 0 && data.files.length === 0) {
        contentDiv.innerHTML = "<p>No files or folders here.</p>"
      }
    })
    .catch((err) => {
      console.error(err)
      document.getElementById("content").innerHTML = "Error loading S3 data."
    })
}

// Load root folder on page load
window.onload = () => loadS3()

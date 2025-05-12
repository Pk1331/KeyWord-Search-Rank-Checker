// Mobile Menu Toggle
const menuToggle = document.getElementById("menuToggle")
const mobileMenu = document.getElementById("mobileMenu")

menuToggle.addEventListener("click", () => {
  mobileMenu.classList.toggle("hidden")
})

document.getElementById("logoutBtnMobile").addEventListener("click", () => {
  document.getElementById("logoutBtn").click()
})

document
  .getElementById("viewResultsBtnMobile")
  .addEventListener("click", () => {
    document.getElementById("viewResultsBtn").click()
  })

// Logout Event
document.getElementById("logoutBtn")?.addEventListener("click", () => {
  window.location.href = "/logout"
})

// View Results Event
document.getElementById("viewResultsBtn")?.addEventListener("click", () => {
  window.open("/results", (target = "_parent"))
})

// File Upload Event
document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("uploadForm")
  const loader = document.getElementById("loader")
  const confirmModal = document.getElementById("confirmModal")

  // Upload Event
  uploadForm.addEventListener("submit", (e) => {
    e.preventDefault()
    confirmModal.classList.remove("hidden")
  })

  // No Button Event
  document.getElementById("confirmNo").addEventListener("click", () => {
    confirmModal.classList.add("hidden")
  })

  // Yes Button Event
  document.getElementById("confirmYes").addEventListener("click", async () => {
    confirmModal.classList.add("hidden")
    loader.classList.remove("hidden")

    const formData = new FormData(uploadForm)

    try {
      const response = await fetch("/process", {
        method: "POST",
        body: formData,
      })

      loader.classList.add("hidden")
      const blob = await response.blob()

      if (!response.ok) {
        const data = await response.json()
        showToast(data.error || "Something went wrong", "error")
        return
      }

      window.open("/results", "_parent")
    } catch (error) {
      loader.classList.add("hidden")
      showToast("An error occurred while processing the file.", "error", error)
    }
  })
})

// Toast Notification
const showToast = (message, type = "success") => {
  Toastify({
    text: message,
    duration: 3000,
    gravity: "top",
    position: "right",
    backgroundColor: type === "success" ? "green" : "red",
  }).showToast()
}

async function fetchRemainingSearches() {
  try {
    const res = await fetch("/remaining-searches")
    const data = await res.json()

    const count = data.total_searches_left ?? "N/A"
    const countElement = document.getElementById("remainingCount")

    countElement.textContent = count

    // Re-trigger the popup animation
    countElement.classList.remove("animate-popup")
    void countElement.offsetWidth
    countElement.classList.add("animate-popup")

    document.getElementById("searchCount").classList.remove("hidden")
  } catch (error) {
    console.error("Failed to fetch remaining searches:", error)
  }
}

fetchRemainingSearches()

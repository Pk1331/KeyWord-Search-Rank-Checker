document
  .getElementById("loginForm")
  .addEventListener("submit", function (event) {
    event.preventDefault()
    let email = document.getElementById("email").value
    let password = document.getElementById("password").value

    fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.redirect) {
          showToast("Login Successful!", "green")

          setTimeout(() => {
            window.location.href = data.redirect
          }, 2000)
        } else {
          showToast(data.error || "Login Failed!", "red")
        }
      })
      .catch((error) => {
        console.error("Login error:", error)
        showToast("Something went wrong!", "red")
      })
  })

function togglePassword() {
  let passwordInput = document.getElementById("password")
  let eyeIcon = document.getElementById("eyeIcon")

  passwordInput.type = passwordInput.type === "password" ? "text" : "password"
  eyeIcon.classList.toggle("fa-eye")
  eyeIcon.classList.toggle("fa-eye-slash")
}

function showToast(message, color) {
  Toastify({
    text: message,
    duration: 3000,
    close: true,
    gravity: "top",
    position: window.innerWidth < 640 ? "center" : "right",
    backgroundColor: color,
    style: {
      fontSize: "14px",
      maxWidth: "90%",
      wordBreak: "break-word",
    },
  }).showToast()
}

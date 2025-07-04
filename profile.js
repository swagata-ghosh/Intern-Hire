document.getElementById("internForm").addEventListener("submit", function(event) {
  event.preventDefault();

  const form = event.target;
  const resumeFile = form.resume.files[0];

  if (!resumeFile || resumeFile.type !== "application/pdf") {
    alert("Please upload a valid PDF file for the resume.");
    return;
  }

  // Here you could send data to a server using fetch() or AJAX
  form.reset();
  document.getElementById("successMessage").classList.remove("hidden");

  // Optional: auto-hide success message after 5 seconds
  setTimeout(() => {
    document.getElementById("successMessage").classList.add("hidden");
  }, 5000);
});

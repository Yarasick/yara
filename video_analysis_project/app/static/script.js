document.getElementById("upload-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const fileInput = document.getElementById("video-file");
  if (!fileInput.files.length) {
    alert("Будь ласка, виберіть файл!");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = "Зачекайте, файл обробляється...";

  try {
    const response = await fetch("http://localhost:8000/analyze/", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    document.getElementById("transcription").innerHTML = `
      <h3>Транскрипція:</h3>
      <p>${data.transcription}</p>
    `;

    document.getElementById("detections").innerHTML = `
      <h3>Детекція об'єктів:</h3>
      <pre>${JSON.stringify(data.detections, null, 2)}</pre>
    `;
  } catch (error) {
    console.error("Помилка:", error);
    resultsDiv.innerHTML = "Сталася помилка при обробці файлу.";
  }
});

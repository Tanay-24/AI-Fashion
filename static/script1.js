document.getElementById("styleForm").addEventListener("submit", async function (e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);

  const res = await fetch("/predict", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    alert("Failed to generate styled image.");
    return;
  }

  const blob = await res.blob();
  const imgUrl = URL.createObjectURL(blob);
  document.getElementById("outputImage").src = imgUrl;
});

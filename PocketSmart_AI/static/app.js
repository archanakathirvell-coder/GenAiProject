async function submitPlanner(formId, endpoint) {
  const form = document.getElementById(formId);
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const result = document.getElementById("result");
    result.innerHTML = "<p>Generating recommendations...</p>";

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        body: new FormData(form)
      });
      const data = await response.json();

      if (!response.ok) throw new Error(data.detail || "Request failed");

      result.innerHTML =
        "<h3>Recommendations</h3><pre>" +
        JSON.stringify(data.result, null, 2) +
        "</pre>";
    } catch (error) {
      result.innerHTML = "<p>Error: " + error.message + "</p>";
    }
  });
}

submitPlanner("homeForm", "/generate-home");
submitPlanner("partyForm", "/generate-party");
submitPlanner("jewelryForm", "/generate-jewelry");

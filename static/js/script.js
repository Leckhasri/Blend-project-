// -------- Helpers --------
function collectInputs() {
  // Build a flat object of 5 * 10 fields
  const payload = {};
  for (let c = 1; c <= 5; c++) {
    for (let p = 1; p <= 10; p++) {
      const id = `Component${c}_Property${p}`;
      const el = document.getElementById(id);
      payload[id] = el && el.value !== "" ? Number(el.value) : null;
    }
  }
  return payload;
}

function fillForm(values) {
  // values expected as { "Component1_Property1": 0.12, ... }
  for (const key in values) {
    const el = document.getElementById(key);
    if (el) el.value = values[key];
  }
}

function showResults(preds) {
  // preds: array of length 10
  const card = document.getElementById("results-card");
  card.classList.remove("d-none");

  preds.forEach((v, i) => {
    const cell = document.getElementById(`bp${i + 1}`);
    if (cell) cell.textContent = typeof v === "number" ? v.toFixed(3) : v;
  });

  // Draw bar chart
  drawChart(preds);
}

let chartInstance = null;
function drawChart(preds) {
  const ctx = document.getElementById("predictionChart");
  if (!ctx) return;

  const labels = Array.from({ length: 10 }, (_, i) => `BP${i + 1}`);
  const data = preds.map(v => Number(v));

  if (chartInstance) chartInstance.destroy();

  chartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Predicted Blend Properties",
          data
          // No colors specified (kept default as requested)
        }
      ]
    },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: false }
      }
    }
  });
}

// -------- Event wiring --------
document.addEventListener("DOMContentLoaded", () => {
  const fillBtn = document.getElementById("fill-btn");
  const predictBtn = document.getElementById("predict-btn");

  // Fill Input from /api/random-inputs
  if (fillBtn) {
    fillBtn.addEventListener("click", async () => {
      try {
        const resp = await fetch("/api/random-inputs");
        if (!resp.ok) throw new Error("Failed to fetch sample inputs");
        const data = await resp.json();
        // Expecting { inputs: { "Component1_Property1": number, ... } }
        fillForm(data.inputs || data); // supports both shapes
      } catch (err) {
        alert("Could not auto-fill inputs. Please try again.");
        console.error(err);
      }
    });
  }

  // Predict via /api/predict
  if (predictBtn) {
    predictBtn.addEventListener("click", async () => {
      const inputs = collectInputs();

      // Optional: basic validation (ensure no nulls)
      const missing = Object.entries(inputs).filter(([_, v]) => v === null);
      if (missing.length > 0) {
        if (!confirm(`You have ${missing.length} empty fields.\nContinue anyway?`)) {
          return;
        }
      }

      try {
        const resp = await fetch("/api/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ inputs })
        });
        if (!resp.ok) throw new Error("Prediction failed");
        const data = await resp.json();
        // Expecting { predictions: [p1..p10] }
        showResults(data.predictions || []);
      } catch (err) {
        alert("Prediction failed. Please try again.");
        console.error(err);
      }
    });
  }
});

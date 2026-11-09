(() => {
  const form = document.querySelector(".calculator form");
  if (!form) return;

  const nameInput = form.querySelector("#name");
  const heightInput = form.querySelector("#height");
  const weightInput = form.querySelector("#weight");
  const panel = document.querySelector("#result-panel");
  const illustration = document.querySelector("#illustration");
  const sideCaption = document.querySelector("#side-caption");
  const bmiNumber = document.querySelector("#result-number");
  const categoryLabel = document.querySelector("#result-label");
  const advice = document.querySelector("#result-advice");
  const gauge = document.querySelector("#bmi-gauge");
  const needle = document.querySelector("#gauge-needle");
  const guidance = JSON.parse(form.dataset.guidance);

  function updateResult() {
    const height = Number(heightInput.value);
    const weight = Number(weightInput.value);
    const heightMeters = height / 100;
    const heightSquared = heightMeters * heightMeters;
    const bmi = weight / heightSquared;

    if (
      !Number.isFinite(height) ||
      height <= 0 ||
      !Number.isFinite(weight) ||
      weight <= 0 ||
      !Number.isFinite(heightSquared) ||
      heightSquared === 0 ||
      !Number.isFinite(bmi) ||
      bmi <= 0
    ) {
      panel.hidden = true;
      if (illustration) illustration.hidden = false;
      if (sideCaption) sideCaption.hidden = false;
      return;
    }

    const scaledBmi = bmi * 10;
    const lowerBmi = Math.floor(scaledBmi);
    const fraction = scaledBmi - lowerBmi;
    const roundedBmi =
      fraction === 0.5
        ? (lowerBmi % 2 === 0 ? lowerBmi : lowerBmi + 1) / 10
        : Math.round(scaledBmi) / 10;
    let category = "obese";
    if (roundedBmi < 18.5) category = "low";
    else if (roundedBmi < 24) category = "healthy";
    else if (roundedBmi < 27) category = "high";

    const result = guidance[category];
    const gaugeBmi = Math.min(Math.max(roundedBmi, 10), 40);
    const angle = ((gaugeBmi - 10) / 30) * 180 - 90;

    bmiNumber.textContent = roundedBmi.toFixed(1);
    categoryLabel.textContent = result.label;
    const name = nameInput.value.trim();
    advice.textContent = name ? `${name}，${result.advice}` : result.advice;
    panel.classList.remove("low", "healthy", "high", "obese");
    panel.classList.add(result.tone);
    needle.style.setProperty("--needle-angle", `${angle.toFixed(1)}deg`);
    gauge.setAttribute("aria-label", `BMI ${roundedBmi.toFixed(1)}，${result.label}`);
    panel.hidden = false;
    if (illustration) illustration.hidden = true;
    if (sideCaption) sideCaption.hidden = true;
  }

  form.addEventListener("input", updateResult);
})();

"use strict";
const button = document.getElementById("check-health");
const statusLabel = document.getElementById("status");
async function checkHealth() {
  button.disabled = true;
  statusLabel.textContent = "Checking…";
  statusLabel.className = "live";
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);
  const start = performance.now();
  try {
    const response = await fetch("/health", {cache: "no-store", signal: controller.signal});
    if (!response.ok) throw new Error("HTTP failure");
    const data = await response.json();
    if (data.status !== "ok" || typeof data.version !== "string") throw new Error("Invalid health data");
    document.getElementById("health-result").textContent = JSON.stringify({status: data.status, service: data.service, version: data.version}, null, 2);
    document.getElementById("release").textContent = data.version;
    document.getElementById("latency").textContent = Math.round(performance.now() - start) + " ms";
    statusLabel.textContent = "Healthy";
    statusLabel.className = "live ok";
  } catch (_) {
    statusLabel.textContent = "Unavailable";
    statusLabel.className = "live error";
    document.getElementById("latency").textContent = "—";
    document.getElementById("health-result").textContent = "Health check failed. Confirm that the server is still running, then try again.";
  } finally {
    clearTimeout(timeout);
    button.disabled = false;
  }
}
button.addEventListener("click", checkHealth);
checkHealth();

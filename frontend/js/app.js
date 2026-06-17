/**
 * Frontend logic for the inventory dashboard.
 * Plain fetch calls - no axios, no build step.
 */

// --- DOM refs ---
const apiUrlInput = document.getElementById("apiUrl");
const saveApiBtn = document.getElementById("saveApiBtn");
const connectionStatus = document.getElementById("connectionStatus");
const commandInput = document.getElementById("commandInput");
const runCommandBtn = document.getElementById("runCommandBtn");
const commandResult = document.getElementById("commandResult");
const addForm = document.getElementById("addForm");
const refreshBtn = document.getElementById("refreshBtn");
const filterBtn = document.getElementById("filterBtn");
const clearFilterBtn = document.getElementById("clearFilterBtn");
const filterLocation = document.getElementById("filterLocation");
const inventoryBody = document.getElementById("inventoryBody");
const statItems = document.getElementById("statItems");
const statQuantity = document.getElementById("statQuantity");
const statWarehouses = document.getElementById("statWarehouses");
const toastEl = document.getElementById("toast");

// Load saved API URL on page open
apiUrlInput.value = getApiBaseUrl();

// --- Helpers ---

function showToast(message, type = "success") {
  toastEl.textContent = message;
  toastEl.className = `toast ${type}`;
  setTimeout(() => toastEl.classList.add("hidden"), 3000);
}

function formatDate(isoString) {
  if (!isoString) return "-";
  const d = new Date(isoString);
  return d.toLocaleString();
}

async function apiFetch(path, options = {}) {
  const base = getApiBaseUrl();
  const response = await fetch(`${base}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const msg = data.detail || data.message || `Request failed (${response.status})`;
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }

  return data;
}

function setConnectionStatus(online) {
  connectionStatus.textContent = online ? "Connected" : "Not connected";
  connectionStatus.className = `status-dot ${online ? "online" : "offline"}`;
}

// --- API actions ---

async function checkHealth() {
  try {
    await apiFetch("/api/health");
    setConnectionStatus(true);
    return true;
  } catch {
    setConnectionStatus(false);
    return false;
  }
}

async function loadInventory(location = "") {
  const query = location ? `?location=${encodeURIComponent(location)}` : "";
  const data = await apiFetch(`/api/inventory${query}`);

  statItems.textContent = data.total_items;
  statQuantity.textContent = data.total_quantity;
  statWarehouses.textContent = data.warehouses;

  if (!data.items.length) {
    inventoryBody.innerHTML = '<tr><td colspan="5" class="empty">No items yet. Add some stock above.</td></tr>';
    return;
  }

  inventoryBody.innerHTML = data.items
    .map(
      (item) => `
      <tr>
        <td>${escapeHtml(item.item_name)}</td>
        <td>${item.quantity}</td>
        <td>${escapeHtml(item.location)}</td>
        <td>${formatDate(item.updated_at)}</td>
        <td><button class="btn danger" data-id="${item.id}">Delete</button></td>
      </tr>`
    )
    .join("");

  // Wire up delete buttons
  inventoryBody.querySelectorAll(".btn.danger").forEach((btn) => {
    btn.addEventListener("click", () => deleteItem(btn.dataset.id));
  });
}

async function runCommand() {
  const command = commandInput.value.trim();
  if (!command) {
    showToast("Type a command first.", "error");
    return;
  }

  try {
    const result = await apiFetch("/api/command", {
      method: "POST",
      body: JSON.stringify({ command }),
    });

    commandResult.textContent = JSON.stringify(result, null, 2);
    commandResult.classList.remove("hidden");

    if (result.status === "success") {
      showToast(result.message || "Command executed.");
      await loadInventory(filterLocation.value.trim());
    } else {
      showToast(result.message || "Command failed.", "error");
    }
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function addItemManual(e) {
  e.preventDefault();

  const payload = {
    item_name: document.getElementById("itemName").value.trim(),
    quantity: parseInt(document.getElementById("quantity").value, 10),
    location: document.getElementById("location").value.trim(),
  };

  try {
    await apiFetch("/api/items", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    showToast(`Added ${payload.quantity} x ${payload.item_name}.`);
    addForm.reset();
    await loadInventory();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function deleteItem(id) {
  if (!confirm("Remove this item from inventory?")) return;

  try {
    await apiFetch(`/api/items/${id}`, { method: "DELETE" });
    showToast("Item removed.");
    await loadInventory(filterLocation.value.trim());
  } catch (err) {
    showToast(err.message, "error");
  }
}

// Basic XSS guard when rendering user-supplied item names
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// --- Event listeners ---

saveApiBtn.addEventListener("click", async () => {
  setApiBaseUrl(apiUrlInput.value.trim());
  const ok = await checkHealth();
  if (ok) {
    showToast("Connected to API.");
    loadInventory();
  } else {
    showToast("Could not reach API. Check the URL.", "error");
  }
});

runCommandBtn.addEventListener("click", runCommand);
commandInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") runCommand();
});

addForm.addEventListener("submit", addItemManual);
refreshBtn.addEventListener("click", () => loadInventory(filterLocation.value.trim()));

filterBtn.addEventListener("click", () => loadInventory(filterLocation.value.trim()));
clearFilterBtn.addEventListener("click", () => {
  filterLocation.value = "";
  loadInventory();
});

// Boot
(async () => {
  const ok = await checkHealth();
  if (ok) await loadInventory();
})();

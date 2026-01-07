// =================================================================
// FRONTEND CONFIGURATION
// =================================================================

// 1. DEPLOY BACKEND TO VERCEL FIRST.
// 2. COPY THE URL (e.g., https://my-project.vercel.app).
// 3. PASTE IT BELOW.

const API_BASE_URL = "https://full-stack-project-iota-lime.vercel.app";

// =================================================================

const itemsList = document.getElementById('itemsList');
const addItemForm = document.getElementById('addItemForm');
const statusMessage = document.getElementById('statusMessage');

function showStatus(message, isError = false) {
    statusMessage.style.display = 'block';
    statusMessage.style.backgroundColor = isError ? '#ffecec' : '#e6fffa';
    statusMessage.style.color = isError ? '#d8000c' : '#0070f3';
    statusMessage.textContent = message;
}

async function loadItems() {
    try {
        if (API_BASE_URL.includes("YOUR_VERCEL_BACKEND_URL_HERE")) {
            throw new Error("API_BASE_URL not configured. See js/app.js");
        }

        const res = await fetch(`${API_BASE_URL}/api/items/`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const items = await res.json();

        itemsList.innerHTML = items.map(item => `
            <li>
                <strong>${item.name}</strong>
                <span style="color:#666">${item.description || ''}</span>
            </li>
        `).join('');

        if (items.length === 0) {
            itemsList.innerHTML = `<li style="color:#888; text-align:center;">No items found. Add one!</li>`;
        }

        statusMessage.style.display = 'none';

    } catch (err) {
        showStatus(`Connection Error: ${err.message}`, true);
    }
}

async function handleAdd(e) {
    e.preventDefault();
    const name = document.getElementById('itemName').value;
    const desc = document.getElementById('itemDesc').value;

    try {
        const res = await fetch(`${API_BASE_URL}/api/items/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name, description: desc })
        });

        if (!res.ok) throw new Error("Failed to create item");

        document.getElementById('itemName').value = '';
        document.getElementById('itemDesc').value = '';
        loadItems(); // Refresh

    } catch (err) {
        showStatus(err.message, true);
    }
}

document.addEventListener('DOMContentLoaded', loadItems);
addItemForm.addEventListener('submit', handleAdd);

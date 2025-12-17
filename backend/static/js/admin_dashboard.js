document.addEventListener('DOMContentLoaded', async () => {
    const user = JSON.parse(localStorage.getItem('user'));

    // Security Check
    if (!user || user.role !== 'admin') {
        alert('Access Denied');
        window.location.href = '../index.html';
        return;
    }

    document.getElementById('adminName').textContent = user.name;
    document.getElementById('logoutBtn').addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.removeItem('user');
        window.location.href = '../index.html';
    });

    await loadStats();
    await loadUsers();
    await loadBookings();
});

async function loadStats() {
    try {
        const stats = await API.get('/admin/dashboard');
        document.getElementById('totalUsers').textContent = stats.users;
        document.getElementById('totalProviders').textContent = stats.providers;
        document.getElementById('totalBookings').textContent = stats.bookings;
    } catch (err) {
        console.error('Failed to load stats', err);
    }
}

async function loadUsers() {
    try {
        const users = await API.get('/admin/users');
        const list = document.getElementById('usersList');
        list.innerHTML = '';

        users.forEach(u => {
            const row = document.createElement('tr');

            // Verification button for providers
            let actionBtn = '-';
            if (u.role === 'provider') {
                actionBtn = `<button class="btn-small" onclick="verifyProvider(${u.provider_profile?.id || 'null'})" style="background:#2563eb; color:white; padding:4px 8px; border:none; border-radius:4px; cursor:pointer;">Verify</button>`;
            }

            row.innerHTML = `
                <td>${u.id}</td>
                <td>${u.name}</td>
                <td>${u.email}</td>
                <td>${u.role}</td>
                <td>${new Date(u.created_at).toLocaleDateString()}</td>
                <td>${actionBtn}</td>
            `;
            list.appendChild(row);
        });
    } catch (err) {
        console.error('Failed to load users', err);
    }
}

async function loadBookings() {
    try {
        const bookings = await API.get('/admin/bookings');
        const list = document.getElementById('bookingsList');
        list.innerHTML = '';

        bookings.forEach(b => {
            const row = document.createElement('tr');

            row.innerHTML = `
                <td>${b.id}</td>
                <td>${b.service_name}</td>
                <td>${b.booking_date}</td>
                <td><span class="badge ${b.status}">${b.status}</span></td>
                <td>${b.total_amount}</td>
            `;
            list.appendChild(row);
        });
    } catch (err) {
        console.error('Failed to load bookings', err);
    }
}

async function verifyProvider(providerId) {
    if (!providerId) return alert('Not a provider');
    if (!confirm('Verify this provider?')) return;
    try {
        await API.request(`/providers/${providerId}/verify`, 'PATCH');
        loadUsers(); // Refresh
        alert('Provider Verified!');
    } catch (err) {
        alert(err.message);
    }
}



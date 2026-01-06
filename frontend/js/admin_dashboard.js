document.addEventListener('DOMContentLoaded', async () => {
    const user = JSON.parse(localStorage.getItem('user'));

    if (!user || user.role !== 'admin') {
        alert('Access Denied');
        window.location.href = 'index.html';
        return;
    }

    document.getElementById('adminName').textContent = user.name;
    document.getElementById('logoutBtn').addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.removeItem('user');
        window.location.href = 'index.html';
    });

    await loadStats();
    await loadUsers();
    await loadBookings();
    await loadComplaints();
});

async function loadStats() {
    try {
        const stats = await API.get('/admin/dashboard');
        document.getElementById('totalUsers').textContent = stats.users;
        document.getElementById('totalProviders').textContent = stats.providers;
        document.getElementById('totalBookings').textContent = stats.bookings;
        document.getElementById('totalSales').textContent = `₹${stats.total_sales.toLocaleString()}`;
        document.getElementById('platformRevenue').textContent = `₹${stats.platform_revenue.toLocaleString()}`;
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

            let actionBtns = '';
            if (u.role === 'provider' && u.provider_profile?.background_verified === 'pending') {
                actionBtns += `<button class="btn-small" onclick="viewProfile(${u.provider_profile?.id}, true)" style="background:#475569; color:white; margin-right:5px;">Inspect</button>`;
                actionBtns += `<button class="btn-small" onclick="verifyProvider(${u.provider_profile?.id || 'null'})" style="background:#2563eb; color:white; margin-right:5px;">Verify</button>`;
            }

            // Only allow deleting non-admin users to prevent self-deletion or locking out the admin account easily
            if (u.role !== 'admin') {
                actionBtns += `<button class="btn-small" onclick="deleteUser(${u.id})" style="background:#ef4444; color:white;">Delete</button>`;
            }

            let info = u.role;
            if (u.role === 'provider' && u.provider_profile) {
                info = `<div><strong>${u.provider_profile.service_type}</strong></div>
                        <div style="font-size:0.8rem; color:#94a3b8;">${u.provider_profile.address || 'No address'}</div>`;
            }

            row.innerHTML = `
                <td>${u.id}</td>
                <td>${u.name}</td>
                <td>${u.email}</td>
                <td>${info}</td>
                <td>${new Date(u.created_at).toLocaleDateString()}</td>
                <td><div style="display:flex;">${actionBtns || '-'}</div></td>
            `;
            list.appendChild(row);
        });
    } catch (err) {
        console.error('Failed to load users', err);
    }
}

async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user and all associated profile data? This action cannot be undone.')) return;
    try {
        await API.request(`/admin/users/${userId}`, 'DELETE');
        alert('User removed successfully.');
        loadUsers();
        await loadStats(); // Update counts
    } catch (err) {
        alert(err.message);
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
        loadUsers();
        alert('Provider Verified!');
    } catch (err) {
        alert(err.message);
    }
}


async function loadComplaints() {
    try {
        const complaints = await API.get('/complaints');
        const list = document.getElementById('complaintsList');
        if (!list) return;
        list.innerHTML = '';

        complaints.forEach(c => {
            const row = document.createElement('tr');
            let actionBtn = '-';
            if (c.status === 'pending') {
                actionBtn = `<button class="btn-small" onclick="resolveComplaint(${c.id})" style="background:#166534; color:white; padding:4px 8px; border:none; border-radius:4px; cursor:pointer;">Resolve</button>`;
            }

            row.innerHTML = `
                <td>${c.id}</td>
                <td>Booking #${c.booking_id}</td>
                <td><strong>${c.subject}</strong><br><small>${c.description}</small></td>
                <td><span class="badge ${c.status}">${c.status}</span></td>
                <td>${actionBtn}</td>
            `;
            list.appendChild(row);
        });
    } catch (err) {
        console.error('Failed to load complaints', err);
    }
}

async function resolveComplaint(id) {
    const resolution = prompt('Enter resolution for this complaint:');
    if (!resolution) return;

    try {
        await API.request(`/complaints/${id}/resolve`, 'PATCH', { resolution });
        loadComplaints();
        alert('Complaint resolved!');
    } catch (err) {
        alert(err.message);
    }
}

function viewProfile(id, isAdminReview = false) {
    let url = `profile.html?id=${id}`;
    if (isAdminReview) url += '&admin_review=true';
    window.open(url, '_blank');
}

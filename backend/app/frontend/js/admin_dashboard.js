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
    await loadInquiries();
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

        if (users.length === 0) {
            list.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:20px; color:#64748b;">No users found</td></tr>';
            return;
        }

        users.forEach(u => {
            const row = document.createElement('tr');

            let actionBtns = '';
            if (u.role === 'provider' && u.provider_profile?.background_verified === 'pending') {
                actionBtns += `<button class="btn-small" onclick="viewProfile(${u.provider_profile?.id}, true)" style="background:#475569; color:white; margin-right:5px;">Inspect</button>`;
                actionBtns += `<button class="btn-small" onclick="verifyProvider(${u.provider_profile?.id || 'null'})" style="background:#2563eb; color:white; margin-right:5px;">Verify</button>`;
            }

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
    if (!confirm('Are you sure you want to delete this user?')) return;
    try {
        await API.request(`/admin/users/${userId}`, 'DELETE');
        alert('User removed successfully.');
        loadUsers();
        await loadStats();
    } catch (err) {
        alert(err.message);
    }
}

async function loadBookings() {
    try {
        const bookings = await API.get('/admin/bookings');
        const list = document.getElementById('bookingsList');
        list.innerHTML = '';

        if (bookings.length === 0) {
            list.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:20px; color:#64748b;">No bookings found</td></tr>';
            return;
        }

        bookings.forEach(b => {
            const row = document.createElement('tr');

            row.innerHTML = `
                <td>${b.id}</td>
                <td>${b.service_name}</td>
                <td>${b.booking_date}</td>
                <td><span class="badge ${b.status}">${b.status}</span></td>
                <td>₹${b.total_amount}</td>
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

        if (complaints.length === 0) {
            list.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:20px; color:#64748b;">No complaints found</td></tr>';
            return;
        }

        complaints.forEach(c => {
            const row = document.createElement('tr');
            let actions = '';

            if (c.status === 'pending') {
                actions = `
                    <button class="btn-small" onclick="investigateComplaint(${c.id})" style="background:#f59e0b; color:white; margin-right:2px;">Check</button>
                    <button class="btn-small" onclick="refundComplaint(${c.id})" style="background:#2563eb; color:white; margin-right:2px;">Refund</button>
                    <button class="btn-small" onclick="warnProvider(${c.id})" style="background:#ef4444; color:white; margin-right:2px;">Warn</button>
                `;
            } else if (c.status === 'investigating') {
                actions = `
                    <button class="btn-small" onclick="refundComplaint(${c.id})" style="background:#2563eb; color:white; margin-right:2px;">Refund</button>
                    <button class="btn-small" onclick="warnProvider(${c.id})" style="background:#ef4444; color:white; margin-right:2px;">Warn</button>
                    <button class="btn-small" onclick="resolveComplaint(${c.id})" style="background:#166534; color:white;">Resolve</button>
                `;
            } else {
                actions = `<span style="font-size:0.8rem; color:#64748b;">${c.resolution || 'No notes'}</span>`;
            }

            row.innerHTML = `
                <td>${c.id}</td>
                <td>Booking #${c.booking_id}</td>
                <td><strong>${c.subject}</strong><br><small>${c.description}</small></td>
                <td><span class="badge ${c.status}">${c.status}</span></td>
                <td><div style="display:flex; flex-wrap:wrap;">${actions}</div></td>
            `;
            list.appendChild(row);
        });
    } catch (err) {
        console.error('Failed to load complaints', err);
    }
}

async function investigateComplaint(id) {
    try {
        await API.request(`/complaints/${id}/investigate`, 'PATCH');
        loadComplaints();
        alert('Complaint marked as Under Investigation.');
    } catch (err) {
        alert(err.message);
    }
}

async function refundComplaint(id) {
    if (!confirm('Process refund for this booking?')) return;
    try {
        await API.request(`/complaints/${id}/refund`, 'PATCH');
        loadComplaints();
        alert('Refund processed successfully.');
    } catch (err) {
        alert(err.message);
    }
}

async function warnProvider(id) {
    if (!confirm('Issue a formal warning to the provider?')) return;
    try {
        await API.request(`/complaints/${id}/warn`, 'PATCH');
        loadComplaints();
        alert('Formal warning issued to provider.');
    } catch (err) {
        alert(err.message);
    }
}

async function resolveComplaint(id) {
    const resolution = prompt('Enter final resolution notes:');
    if (!resolution) return;
    try {
        await API.request(`/complaints/${id}/resolve`, 'PATCH', { resolution });
        loadComplaints();
        alert('Complaint resolved!');
    } catch (err) {
        alert(err.message);
    }
}

async function loadInquiries() {
    try {
        const inquiries = await API.get('/inquiries');
        const list = document.getElementById('inquiriesList');
        if (!list) return;
        list.innerHTML = '';

        if (inquiries.length === 0) {
            list.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:20px; color:#64748b;">No inquiries found</td></tr>';
            return;
        }

        inquiries.forEach(i => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${new Date(i.created_at).toLocaleDateString()}</td>
                <td>${i.name} (${i.email})</td>
                <td><strong>${i.subject}</strong></td>
                <td>${i.message}</td>
                <td><span class="badge ${i.status}">${i.status}</span></td>
            `;
            list.appendChild(row);
        });
    } catch (err) {
        console.error('Failed to load inquiries', err);
    }
}

async function viewProfile(providerId, isAdminView = false) {
    if (!providerId) return;
    window.location.href = `profile.html?id=${providerId}&admin=${isAdminView}`;
}

window.investigateComplaint = investigateComplaint;
window.refundComplaint = refundComplaint;
window.warnProvider = warnProvider;
window.resolveComplaint = resolveComplaint;
window.verifyProvider = verifyProvider;
window.deleteUser = deleteUser;
window.viewProfile = viewProfile; // Fix for Inspect button

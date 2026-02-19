let currentBookings = [];
let currentUserRole = '';

document.addEventListener('DOMContentLoaded', async () => {
    const userString = localStorage.getItem('user');
    if (!userString) {
        window.location.href = '/login.html';
        return;
    }
    const user = JSON.parse(userString);

    // Redirect provider to their specific dashboard
    if (user.role === 'provider') {
        window.location.href = '/provider_dashboard.html';
        return;
    }


    updateProfileUI(user);


    console.log('Loading dashboard for user:', user.id);
    if (user.role === 'customer') {
        currentUserRole = 'customer';
        // Hide management buttons for customers
        const addProviderBtn = document.getElementById('add-provider-btn');
        if (addProviderBtn) addProviderBtn.style.display = 'none';

        await loadCustomerDashboard(user.id);
        await loadCustomerReviews(user.id);
    } else {
        currentUserRole = 'provider';
        await loadProviderDashboard(user.id);
    }


    setupSettingsForm(user);


    setupTabs(user);
    setupFilterListener();
});

function setupFilterListener() {
    const filterSelect = document.querySelector('.filter-select');
    if (filterSelect) {
        filterSelect.addEventListener('change', (e) => {
            const status = e.target.value;
            renderBookingsTable(status);
        });
    }
}

function renderBookingsTable(statusFilter = 'All Status') {
    const body = document.getElementById('all-bookings-body') || document.querySelector('#bookings-page .full-table tbody');
    if (!body) return;

    let filtered = currentBookings;
    if (statusFilter !== 'All Status') {
        filtered = currentBookings.filter(b => b.status.toLowerCase() === statusFilter.toLowerCase());
    }

    body.innerHTML = '';
    if (filtered.length === 0) {
        const msg = statusFilter === 'All Status' ? "You haven't made any bookings yet." : `No ${statusFilter} bookings found.`;
        body.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 40px; color: #666;">${msg}</td></tr>`;
        return;
    }

    filtered.forEach(b => {
        const pName = b.provider?.user?.name || `Professional #${b.provider_id}`;
        const customerName = b.customer?.name || "Customer";

        let actionBtn = '';
        if (currentUserRole === 'customer') {
            if (b.status === 'completed') {
                actionBtn += `<button class="btn-small" onclick="openReviewModal(${b.id}, ${b.provider_id})" style="margin-right:5px;">Review</button>`;
            }
            if (b.status !== 'cancelled') {
                actionBtn += `<button class="btn-small" onclick="openComplaintModal(${b.id})" style="background:#f97316; color:white; margin-right:5px;">Complaint</button>`;
            }
            if (b.status === 'reschedule_requested') {
                actionBtn += `
                    <div style="display:flex; flex-direction:column; gap:4px; margin-bottom:5px;">
                        <span style="font-size:0.75rem; color:#d97706; font-weight:600;">Proposed: ${b.suggested_date} @ ${b.suggested_time}</span>
                        <div style="display:flex; gap:4px;">
                            <button class="btn-small" onclick="handleReschedule(${b.id}, true)" style="background:#16a34a; color:white;">Accept</button>
                            <button class="btn-small" onclick="handleReschedule(${b.id}, false)" style="background:#dc2626; color:white;">Decline</button>
                        </div>
                    </div>
                `;
            }
            if (b.status === 'pending' || b.status === 'confirmed') {
                actionBtn += `<button class="btn-small" onclick='openEditBookingModal(${JSON.stringify(b)})' style="background:#0ea5e9; color:white; margin-right:5px;">Edit</button>`;
                actionBtn += `<button class="btn-small btn-danger" onclick="cancelBooking(${b.id})" style="background:#dc2626; color:white;">Cancel</button>`;
            }
        } else {
            // Provider Role
            if (b.status === 'pending') {
                actionBtn += `
                    <button class="btn-small" onclick="updateBookingStatus(${b.id}, 'confirmed')" style="background:#16a34a; color:white; margin-right:5px;">Accept</button>
                    <button class="btn-small" onclick="openRescheduleModal(${b.id})" style="background:#f59e0b; color:white; margin-right:5px;">Reschedule</button>
                    <button class="btn-small btn-danger" onclick="updateBookingStatus(${b.id}, 'cancelled')" style="background:#dc2626; color:white;">Reject</button>
                 `;
            } else if (b.status === 'confirmed') {
                actionBtn += `
                    <button class="btn-small" onclick="updateBookingStatus(${b.id}, 'completed')" style="background:#2563eb; color:white; margin-right:5px;">Mark Complete</button>
                    <button class="btn-small" onclick="openRescheduleModal(${b.id})" style="background:#f59e0b; color:white;">Reschedule</button>
                `;
            }
        }

        if (!actionBtn) actionBtn = '-';

        body.innerHTML += `
            <tr>
                <td>#B${b.id.toString().padStart(3, '0')}</td>
                <td>${b.service_name}</td>
                <td>${currentUserRole === 'provider' ? 'You' : pName}</td>
                <td>${customerName}</td>
                <td>${b.booking_date} ${b.booking_time}</td>
                <td>₹${b.total_amount}</td>
                <td><span class="badge ${b.status.toLowerCase()}">${b.status.replace(/_/g, ' ')}</span></td>
                <td>${actionBtn}</td>
            </tr>
        `;
    });
}

// Global Reschedule Handler for Customers
window.handleReschedule = async (bookingId, accept) => {
    const action = accept ? 'accept' : 'decline';
    if (!confirm(`Are you sure you want to ${action} this reschedule request?`)) return;

    try {
        await API.request(`/bookings/${bookingId}/reschedule/response?accept=${accept}`, 'PATCH');
        alert(`Reschedule request ${accept ? 'accepted' : 'declined'}.`);
        window.location.reload();
    } catch (err) {
        alert('Failed to process response: ' + err.message);
    }
};

function updateProfileUI(user) {
    const nameEl = document.getElementById('header-user-name');
    const imgEl = document.getElementById('header-user-img');

    if (nameEl) nameEl.textContent = user.name;
    if (imgEl) imgEl.src = `https://ui-avatars.com/api/?name=${user.name}&background=random`;
}

function setupTabs(user) {
    const links = document.querySelectorAll('.sidebar-nav .nav-link');
    const pages = document.querySelectorAll('.page');

    links.forEach(link => {
        link.addEventListener('click', (e) => {
            const targetId = link.getAttribute('data-page');

            // Allow default navigation for "Back to Home"
            if (link.getAttribute('href') !== '#' && !targetId) return;

            e.preventDefault();

            // Handle special tabs
            if (targetId) {
                pages.forEach(p => p.classList.remove('active'));
                links.forEach(l => l.classList.remove('active'));

                const targetPage = document.getElementById(targetId + '-page');
                if (targetPage) {
                    targetPage.classList.add('active');
                    link.classList.add('active');

                    // Load specific data if needed
                    if (targetId === 'complaints') {
                        loadCustomerComplaints(user.id);
                    }
                }
            }
        });
    });
}

async function loadCustomerDashboard(userId) {
    try {
        const results = await Promise.allSettled([
            API.get(`/bookings/customer/${userId}`),
            API.get('/providers/')
        ]);

        const bookings = results[0].status === 'fulfilled' ? results[0].value : [];
        currentBookings = bookings;
        const providers = results[1].status === 'fulfilled' ? results[1].value : [];

        // 1. Stats Overview
        const pending = bookings.filter(b => b.status === 'pending').length;
        const confirmed = bookings.filter(b => b.status === 'confirmed').length;
        const completedBookings = bookings.filter(b => b.status === 'completed');
        const monthlySpend = completedBookings.reduce((sum, b) => sum + b.total_amount, 0);

        document.getElementById('stat-pending-bookings').textContent = pending;
        document.getElementById('stat-confirmed-bookings').textContent = confirmed;
        document.getElementById('stat-active-providers').textContent = providers.length;
        document.getElementById('stat-monthly-spend').textContent = `₹${monthlySpend.toLocaleString()}`;

        // 2. Recent Bookings (Overview Tab)
        const recentBody = document.getElementById('recent-bookings-body');
        if (recentBody) {
            recentBody.innerHTML = '';
            if (bookings.length === 0) {
                recentBody.innerHTML = '<tr><td colspan="4" style="text-align:center; padding: 20px; color: #666;">No bookings found yet. Time to book your first service!</td></tr>';
            } else {
                const recent = [...bookings].reverse().slice(0, 5); // Last 5
                recent.forEach(b => {
                    const pName = b.provider?.user?.name || `Professional #${b.provider_id}`;
                    // Make row clickable to go to bookings tab
                    recentBody.innerHTML += `
                        <tr onclick="document.querySelector('[data-page=bookings]').click()" style="cursor:pointer;" title="Click to view details">
                            <td>${b.service_name}</td>
                            <td>${pName}</td>
                            <td>${new Date(b.booking_date).toLocaleDateString()}</td>
                            <td><span class="badge ${b.status}">${b.status}</span></td>
                        </tr>
                    `;
                });
            }
        }

        // 3. Top Providers List (Overview Tab)
        const topProvidersContainer = document.getElementById('top-providers-list');
        if (topProvidersContainer) {
            topProvidersContainer.innerHTML = '';
            if (providers.length === 0) {
                topProvidersContainer.innerHTML = '<p style="text-align:center; padding: 20px; color: #666;">No verified providers found in your area.</p>';
            } else {
                const top = [...providers].sort((a, b) => b.rating - a.rating).slice(0, 3);
                top.forEach(p => {
                    topProvidersContainer.innerHTML += `
                        <div class="provider-item" onclick="window.location.href='/profile.html?id=${p.id}'" style="cursor:pointer;">
                            <img src="https://ui-avatars.com/api/?name=${p.user.name}&background=random" alt="Provider">
                            <div class="provider-info">
                                <p class="provider-name">${p.user.name}</p>
                                <p class="provider-service">${p.service_type}</p>
                            </div>
                            <div class="provider-rating">
                                <span class="rating">${p.rating}</span>
                                <span class="star">★</span>
                            </div>
                        </div>
                    `;
                });
            }
        }

        // 4. All Bookings Page
        renderBookingsTable();

        // 5. Payments Page
        const transactionsBody = document.getElementById('transactions-body') || document.querySelector('#payments-page .full-table tbody');
        if (transactionsBody) {
            transactionsBody.innerHTML = '';
            const paid = bookings.filter(b => b.status === 'completed' || b.status === 'confirmed');
            paid.forEach(b => {
                transactionsBody.innerHTML += `
                    <tr>
                        <td>#TXN${b.id.toString().padStart(3, '0')}</td>
                        <td>${b.service_name} Payment</td>
                        <td>₹${b.total_amount}</td>
                        <td>${new Date(b.created_at || Date.now()).toLocaleDateString()}</td>
                        <td><span class="badge completed">Paid</span></td>
                    </tr>
                `;
            });

        }

        // 6. Payments Page Stats
        const paymentTotalEl = document.getElementById('payment-total');
        const paymentMonthEl = document.getElementById('payment-month');
        const paymentPendingEl = document.getElementById('payment-pending');

        if (paymentTotalEl || paymentMonthEl || paymentPendingEl) {
            const confirmedAndCompleted = bookings.filter(b => b.status === 'confirmed' || b.status === 'completed');
            const totalPayments = confirmedAndCompleted.reduce((sum, b) => sum + (b.total_amount || 0), 0);

            const now = new Date();
            const thisMonth = confirmedAndCompleted.filter(b => {
                const date = new Date(b.created_at || Date.now());
                return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
            }).reduce((sum, b) => sum + (b.total_amount || 0), 0);

            const pendingAmount = bookings.filter(b => b.status === 'pending')
                .reduce((sum, b) => sum + (b.total_amount || 0), 0);

            if (paymentTotalEl) paymentTotalEl.textContent = `₹${totalPayments.toLocaleString()}`;
            if (paymentMonthEl) paymentMonthEl.textContent = `₹${thisMonth.toLocaleString()}`;
            if (paymentPendingEl) paymentPendingEl.textContent = `₹${pendingAmount.toLocaleString()}`;
        }

    } catch (err) {
        console.error('Failed to load customer dashboard:', err);
    }
}

async function loadProviderDashboard(userId) {
    console.log('Loading Provider Dashboard...');
    try {
        // 1. Get Provider Profile
        const provider = await API.get(`/providers/profile/${userId}`);
        const providerId = provider.id;

        // 2. Get Provider Bookings
        const bookings = await API.get(`/bookings/provider/${providerId}`);
        currentBookings = bookings;

        // 3. Calculate Stats
        const pending = bookings.filter(b => b.status === 'pending').length;
        const confirmed = bookings.filter(b => b.status === 'confirmed').length;
        const completed = bookings.filter(b => b.status === 'completed');
        const earnings = completed.reduce((sum, b) => sum + (b.provider_amount || 0), 0);

        // Update Labels for Provider Context
        document.querySelector('.stat-card:nth-child(3) .stat-label').textContent = 'Total Jobs Done';
        document.getElementById('stat-active-providers').textContent = completed.length; // Reuse ID but change meaning

        document.querySelector('.stat-card:nth-child(4) .stat-label').textContent = 'Total Earnings';

        document.getElementById('stat-pending-bookings').textContent = pending;
        document.getElementById('stat-confirmed-bookings').textContent = confirmed;
        document.getElementById('stat-monthly-spend').textContent = `₹${earnings.toLocaleString()}`; // Reusing ID for earnings

        // 4. Render Recent Bookings
        const recentBody = document.getElementById('recent-bookings-body');
        if (recentBody) {
            recentBody.innerHTML = '';
            if (bookings.length === 0) {
                recentBody.innerHTML = '<tr><td colspan="4" style="text-align:center; padding: 20px; color: #666;">No bookings yet. Stay tuned!</td></tr>';
            } else {
                const recent = [...bookings].reverse().slice(0, 5);
                recent.forEach(b => {
                    const cName = b.customer?.name || "Customer";
                    recentBody.innerHTML += `
                        <tr onclick="document.querySelector('[data-page=bookings]').click()" style="cursor:pointer;">
                            <td>${b.service_name}</td>
                            <td>${cName}</td>
                            <td>${new Date(b.booking_date).toLocaleDateString()}</td>
                            <td><span class="badge ${b.status}">${b.status}</span></td>
                        </tr>
                    `;
                });
            }
        }

        // 5. Hide "Top Providers" and show something else or hide it?
        // For now, let's hide "Top Providers" section for providers as it's not relevant
        const topProvidersCard = document.querySelector('.dashboard-grid .card:nth-child(2)');
        if (topProvidersCard) {
            topProvidersCard.style.display = 'none';
            // potentially expand the recent bookings to full width
            document.querySelector('.dashboard-grid').style.gridTemplateColumns = '1fr';
        }

        // 6. All Bookings Table
        renderBookingsTable();

    } catch (err) {
        console.error("Error loading provider dashboard:", err);
        // Show error to user
        const recentBody = document.getElementById('recent-bookings-body');
        if (recentBody) recentBody.innerHTML = `<tr><td colspan="4">Error loading data: ${err.message}</td></tr>`;

        // This usually happens if provider profile is missing for a "provider" user
        if (err.message.includes('404')) {
            alert("Provider profile not found. Please contact admin.");
        }
    }
}

async function updateBookingStatus(bookingId, status) {
    if (!confirm(`Are you sure you want to mark this booking as ${status}?`)) return;
    try {
        await API.request(`/bookings/${bookingId}/status?new_status=${status}`, 'PATCH'); // Query param or body depending on backend
        alert('Status updated!');
        location.reload();
    } catch (err) {
        alert("Failed to update status: " + err.message);
    }
}


async function loadCustomerReviews(userId) {
    try {
        const reviews = await API.get(`/reviews/customer/${userId}`);
        const container = document.querySelector('.reviews-container');
        if (!container) return;

        container.innerHTML = '';

        if (reviews.length === 0) {
            container.innerHTML = '<p>You haven\'t written any reviews yet.</p>';
            return;
        }

        reviews.forEach(review => {
            const card = document.createElement('div');
            card.className = 'review-card';
            card.innerHTML = `
                <div class="review-header">
                    <div class="reviewer-info">
                        <div>
                            <p class="reviewer-name">Review for Provider #${review.provider_id}</p>
                            <p class="review-service">Booking #${review.booking_id}</p>
                        </div>
                    </div>
                    <div class="review-rating">${review.rating}★</div>
                </div>
                <p class="review-text">${review.comment || 'No comment'}</p>
                <p class="review-date">Posted on ${new Date(review.created_at).toLocaleDateString()}</p>
            `;
            container.appendChild(card);
        });

    } catch (err) {
        console.error('Failed to load reviews:', err);
    }
}

function setupSettingsForm(user) {
    const form = document.querySelector('.settings-form');
    if (!form) return;

    // Prefill
    const inputs = form.querySelectorAll('input');
    if (inputs.length >= 3) {
        inputs[0].value = user.name;
        inputs[1].value = user.email;
        inputs[2].value = user.phone || '';
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            name: inputs[0].value,
            email: inputs[1].value,
            phone: inputs[2].value
        };

        try {
            const updatedUser = await API.put(`/users/${user.id}`, data);

            const newUserState = { ...user, ...updatedUser };
            localStorage.setItem('user', JSON.stringify(newUserState));

            alert('Profile updated successfully!');
            location.reload();
        } catch (err) {
            alert('Update failed: ' + err.message);
        }
    });

    const deleteBtn = document.querySelector('.btn-danger');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', async () => {
            if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
                try {
                    await API.request(`/users/${user.id}`, 'DELETE');
                    alert('Account deleted successfully.');
                    localStorage.clear();
                    window.location.href = 'index.html';
                } catch (err) {
                    alert('Failed to delete account: ' + err.message);
                }
            }
        });
    }
}


function openReviewModal(bookingId, providerId) {

    if (!document.getElementById('reviewModal')) {
        const modalHTML = `
            <div id="reviewModal" class="modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100vh; background:rgba(0,0,0,0.5); z-index:1000; align-items:center; justify-content:center;">
                <div class="modal-content" style="background:white; padding:2rem; border-radius:8px; max-width:500px; width:90%;">
                    <h2>Write a Review</h2>
                    <form id="reviewForm">
                        <input type="hidden" id="reviewBookingId">
                        <div class="form-group" style="margin-bottom:1rem;">
                            <label>Rating (1-5)</label>
                            <select id="reviewRating" style="width:100%; padding:8px;" required>
                                <option value="5">5 - Excellent</option>
                                <option value="4">4 - Good</option>
                                <option value="3">3 - Average</option>
                                <option value="2">2 - Poor</option>
                                <option value="1">1 - Terrible</option>
                            </select>
                        </div>
                         <div class="form-group" style="margin-bottom:1rem;">
                            <label>Comment</label>
                            <textarea id="reviewComment" style="width:100%; padding:8px;" rows="4" required></textarea>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-top:20px;">
                            <button type="button" onclick="document.getElementById('reviewModal').style.display='none'" style="padding:10px 20px; border:none; background:#ccc; cursor:pointer;">Cancel</button>
                            <button type="submit" style="padding:10px 20px; border:none; background:#2563eb; color:white; cursor:pointer;">Submit Review</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);


        document.getElementById('reviewForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                booking_id: parseInt(document.getElementById('reviewBookingId').value),
                rating: parseInt(document.getElementById('reviewRating').value),
                comment: document.getElementById('reviewComment').value
            };

            try {

                const user = JSON.parse(localStorage.getItem('user'));
                await API.post(`/reviews/?customer_id=${user.id}`, data);
                alert('Review submitted!');
                document.getElementById('reviewModal').style.display = 'none';
                location.reload();
            } catch (err) {
                alert(err.message);
            }
        });
    }

    document.getElementById('reviewBookingId').value = bookingId;
    document.getElementById('reviewModal').style.display = 'flex';
}

function openComplaintModal(bookingId) {
    if (!document.getElementById('complaintModal')) {
        const modalHTML = `
            <div id="complaintModal" class="modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100vh; background:rgba(0,0,0,0.5); z-index:1000; align-items:center; justify-content:center;">
                <div class="modal-content" style="background:white; padding:2rem; border-radius:8px; max-width:500px; width:90%;">
                    <h2>Raise a Complaint</h2>
                    <form id="complaintForm">
                        <input type="hidden" id="complaintBookingId">
                        <div class="form-group" style="margin-bottom:1rem;">
                            <label>Subject</label>
                            <input type="text" id="complaintSubject" style="width:100%; padding:8px;" required placeholder="Brief summary of the issue">
                        </div>
                         <div class="form-group" style="margin-bottom:1rem;">
                            <label>Description</label>
                            <textarea id="complaintDescription" style="width:100%; padding:8px;" rows="4" required placeholder="Detailed description of the problem"></textarea>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-top:20px;">
                            <button type="button" onclick="document.getElementById('complaintModal').style.display='none'" style="padding:10px 20px; border:none; background:#ccc; cursor:pointer;">Cancel</button>
                            <button type="submit" style="padding:10px 20px; border:none; background:#dc2626; color:white; cursor:pointer;">Submit Complaint</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        document.getElementById('complaintForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const user = JSON.parse(localStorage.getItem('user'));
            const data = {
                booking_id: parseInt(document.getElementById('complaintBookingId').value),
                subject: document.getElementById('complaintSubject').value,
                description: document.getElementById('complaintDescription').value
            };

            try {
                await API.post(`/complaints/?customer_id=${user.id}`, data);
                alert('Complaint submitted successfully. Our team will review it.');
                document.getElementById('complaintModal').style.display = 'none';
                location.reload();
            } catch (err) {
                alert(err.message);
            }
        });
    }

    document.getElementById('complaintBookingId').value = bookingId;
    document.getElementById('complaintModal').style.display = 'flex';
}

async function cancelBooking(bookingId) {
    if (!confirm('Are you sure you want to cancel this booking?')) return;
    try {
        await API.request(`/bookings/${bookingId}`, 'DELETE');
        alert('Booking cancelled.');
        location.reload();
    } catch (err) {
        alert(err.message);
    }
}

function openEditBookingModal(booking) {
    if (!document.getElementById('editBookingModal')) {
        const modalHTML = `
            <div id="editBookingModal" class="modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100vh; background:rgba(0,0,0,0.5); z-index:1000; align-items:center; justify-content:center;">
                <div class="modal-content" style="background:white; padding:2rem; border-radius:8px; max-width:500px; width:90%; color: #333;">
                    <h2 style="margin-bottom: 1.5rem;">Edit Booking Details</h2>
                    <form id="editBookingForm">
                        <input type="hidden" id="editBookingId">
                        
                        <div class="form-group" style="margin-bottom:1rem;">
                            <label style="display:block; margin-bottom:5px; font-weight:bold;">Date</label>
                            <input type="date" id="editBookingDate" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:4px;" required>
                        </div>

                        <div class="form-group" style="margin-bottom:1rem;">
                            <label style="display:block; margin-bottom:5px; font-weight:bold;">Time</label>
                            <input type="time" id="editBookingTime" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:4px;" required>
                        </div>

                        <div class="form-group" style="margin-bottom:1rem;">
                            <label style="display:block; margin-bottom:5px; font-weight:bold;">Duration (Hours)</label>
                            <input type="number" id="editBookingDuration" min="1" max="24" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:4px;" required>
                        </div>

                        <div class="form-group" style="margin-bottom:1rem;">
                            <label style="display:block; margin-bottom:5px; font-weight:bold;">Service Name</label>
                            <input type="text" id="editBookingServiceName" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:4px;" required>
                        </div>

                         <div class="form-group" style="margin-bottom:1rem;">
                            <label style="display:block; margin-bottom:5px; font-weight:bold;">Address</label>
                            <textarea id="editBookingAddress" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:4px;" rows="2" required></textarea>
                        </div>

                        <div class="form-group" style="margin-bottom:1rem;">
                            <label style="display:block; margin-bottom:5px; font-weight:bold;">Notes (Optional)</label>
                            <textarea id="editBookingNotes" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:4px;" rows="2"></textarea>
                        </div>

                        <div style="display:flex; justify-content:space-between; margin-top:20px;">
                            <button type="button" onclick="document.getElementById('editBookingModal').style.display='none'" style="padding:10px 20px; border:none; background:#ccc; border-radius:4px; cursor:pointer; font-weight:bold;">Cancel</button>
                            <button type="submit" style="padding:10px 20px; border:none; background:#0ea5e9; color:white; border-radius:4px; cursor:pointer; font-weight:bold;">Save Changes</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        document.getElementById('editBookingForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const bookingId = document.getElementById('editBookingId').value;
            const data = {
                booking_date: document.getElementById('editBookingDate').value,
                booking_time: document.getElementById('editBookingTime').value,
                duration_hours: parseInt(document.getElementById('editBookingDuration').value),
                service_name: document.getElementById('editBookingServiceName').value,
                address: document.getElementById('editBookingAddress').value,
                notes: document.getElementById('editBookingNotes').value
            };

            try {
                await API.request(`/bookings/${bookingId}`, 'PATCH', data);
                alert('Booking updated successfully!');
                document.getElementById('editBookingModal').style.display = 'none';
                location.reload();
            } catch (err) {
                alert('Failed to update booking: ' + err.message);
            }
        });
    }

    // Pre-fill form
    document.getElementById('editBookingId').value = booking.id;
    document.getElementById('editBookingDate').value = booking.booking_date;
    document.getElementById('editBookingTime').value = booking.booking_time;
    document.getElementById('editBookingDuration').value = booking.duration_hours;
    document.getElementById('editBookingServiceName').value = booking.service_name;
    document.getElementById('editBookingAddress').value = booking.address;
    document.getElementById('editBookingNotes').value = booking.notes || '';

    document.getElementById('editBookingModal').style.display = 'flex';
}

async function loadCustomerComplaints(userId) {
    const body = document.getElementById('user-complaints-body');
    if (!body) return;

    try {
        const complaints = await API.get(`/complaints/customer/${userId}`);
        body.innerHTML = '';

        if (complaints.length === 0) {
            body.innerHTML = '<tr><td colspan="6" style="text-align:center; padding: 40px; color: #666;">No complaints found. We hope you are having a great experience!</td></tr>';
            return;
        }

        complaints.forEach(c => {
            const statusClass = c.status.toLowerCase();
            const resolution = c.resolution || '-';
            body.innerHTML += `
                <tr>
                    <td>#C${c.id.toString().padStart(3, '0')}</td>
                    <td>#B${c.booking_id.toString().padStart(3, '0')}</td>
                    <td>${c.subject}</td>
                    <td><span class="badge ${statusClass}">${c.status}</span></td>
                    <td>${resolution}</td>
                    <td>${new Date(c.created_at).toLocaleDateString()}</td>
                </tr>
            `;
        });
    } catch (err) {
        console.error('Failed to load complaints:', err);
        body.innerHTML = '<tr><td colspan="6" style="text-align:center; color: red;">Error loading complaints. Please try again.</td></tr>';
    }
}


// This dashboard script handles authentication, role-based UI rendering, API-driven data loading, and real-time user interactions for both customers and providers using a single reusable JavaScript file.
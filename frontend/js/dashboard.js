document.addEventListener('DOMContentLoaded', async () => {
    const user = JSON.parse(localStorage.getItem('user'));

    if (!user) {
        window.location.href = '/login.html';
        return;
    }


    updateProfileUI(user);


    console.log('Loading dashboard for user:', user.id);
    if (user.role === 'customer') {
        await loadCustomerDashboard(user.id);
        await loadCustomerReviews(user.id);
    } else {
        await loadProviderDashboard(user.id);
    }


    setupSettingsForm(user);


    setupTabs();
});

function updateProfileUI(user) {

    const profileNames = document.querySelectorAll('.user-profile span');
    profileNames.forEach(el => el.textContent = user.name);
}

function setupTabs() {
    const links = document.querySelectorAll('.sidebar-nav .nav-link');
    const pages = document.querySelectorAll('.page');

    links.forEach(link => {
        link.addEventListener('click', (e) => {
            const targetId = link.getAttribute('data-page');
            if (targetId === 'bookings' || targetId === 'providers') {

                e.preventDefault();


                pages.forEach(p => p.classList.remove('active'));
                links.forEach(l => l.classList.remove('active'));


                const targetPage = document.getElementById(targetId + '-page');
                if (targetPage) {
                    targetPage.classList.add('active');
                    link.classList.add('active');
                }
            } else if (targetId) {
                e.preventDefault();
                pages.forEach(p => p.classList.remove('active'));
                links.forEach(l => l.classList.remove('active'));
                const targetPage = document.getElementById(targetId + '-page');
                if (targetPage) {
                    targetPage.classList.add('active');
                    link.classList.add('active');
                }
            }
        });
    });
}

async function loadCustomerDashboard(userId) {
    try {
        // Fetch data independently or use allSettled to prevent one failure from blocking the other
        const results = await Promise.allSettled([
            API.get(`/bookings/customer/${userId}`),
            API.get('/providers/')
        ]);

        const bookings = results[0].status === 'fulfilled' ? results[0].value : [];
        const providers = results[1].status === 'fulfilled' ? results[1].value : [];

        if (results[0].status === 'rejected') console.error('Bookings failed:', results[0].reason);
        if (results[1].status === 'rejected') console.error('Providers failed:', results[1].reason);

        const providerMap = {};
        providers.forEach(p => providerMap[p.id] = p);

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
                const recent = bookings.slice(-5).reverse(); // Last 5
                recent.forEach(b => {
                    const pName = providerMap[b.provider_id]?.user.name || `Provider #${b.provider_id}`;
                    recentBody.innerHTML += `
                        <tr>
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
                        <div class="provider-item" onclick="viewProfile(${p.id})" style="cursor:pointer;">
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
        const allBookingsBody = document.getElementById('all-bookings-body') || document.querySelector('#bookings-page .full-table tbody');
        if (allBookingsBody) {
            allBookingsBody.innerHTML = '';
            if (bookings.length === 0) {
                allBookingsBody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding: 40px; color: #666;">You haven\'t made any bookings yet. Browse our services to get started!</td></tr>';
            } else {
                bookings.reverse().forEach(b => {
                    const pName = providerMap[b.provider_id]?.user.name || `Provider #${b.provider_id}`;
                    let actionBtn = '';
                    if (b.status === 'completed') {
                        actionBtn += `<button class="btn-small" onclick="openReviewModal(${b.id}, ${b.provider_id})" style="margin-right:5px;">Review</button>`;
                    }

                    if (b.status !== 'cancelled') {
                        actionBtn += `<button class="btn-small" onclick="openComplaintModal(${b.id})" style="background:#f97316; color:white; margin-right:5px;">Complaint</button>`;
                    }

                    if (b.status === 'pending' || b.status === 'confirmed') {
                        actionBtn += `<button class="btn-small btn-danger" onclick="cancelBooking(${b.id})" style="background:#dc2626; color:white;">Cancel</button>`;
                    }

                    if (!actionBtn) actionBtn = '-';

                    allBookingsBody.innerHTML += `
                    <tr>
                        <td>#B${b.id.toString().padStart(3, '0')}</td>
                        <td>${b.service_name}</td>
                        <td>${pName}</td>
                        <td>${JSON.parse(localStorage.getItem('user')).name}</td>
                        <td>${b.booking_date} ${b.booking_time}</td>
                        <td>₹${b.total_amount}</td>
                        <td><span class="badge ${b.status}">${b.status}</span></td>
                        <td>${actionBtn}</td>
                    </tr>
                `;
                });
            }

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
                        <td>${new Date(b.created_at).toLocaleDateString()}</td>
                        <td><span class="badge completed">Paid</span></td>
                    </tr>
                `;
                });

                document.getElementById('payment-total').textContent = `₹${monthlySpend.toLocaleString()}`;
                document.getElementById('payment-month').textContent = `₹${monthlySpend.toLocaleString()}`; // Simplified
                document.getElementById('payment-pending').textContent = `₹${bookings.filter(b => b.status === 'pending').reduce((sum, b) => sum + b.total_amount, 0).toLocaleString()}`;
            }

        } catch (err) {
            console.error('Failed to load customer dashboard:', err);
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
        inputs[0].value = user.name;
        inputs[1].value = user.email;
        inputs[2].value = user.phone || '';

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
            deleteBtn.addEventListener('click', () => {
                alert('Delete functionality is not implemented yet for safety.');
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
                    booking_id: document.getElementById('reviewBookingId').value,
                    rating: document.getElementById('reviewRating').value,
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

    async function loadProviderDashboard(userId) {

        console.log('Provider dashboard loaded via dashboard.js specific logic');
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
                    booking_id: document.getElementById('complaintBookingId').value,
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

    function viewProfile(id) {
        window.location.href = `/profile.html?id=${id}`;
    }
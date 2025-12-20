document.addEventListener('DOMContentLoaded', async () => {
    const user = JSON.parse(localStorage.getItem('user'));

    if (!user) {
        window.location.href = '../htmlpages/login.html';
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
        const bookings = await API.get(`/bookings/customer/${userId}`);


        const pending = bookings.filter(b => b.status === 'pending').length;
        const confirmed = bookings.filter(b => b.status === 'confirmed').length;

        const tableBody = document.querySelector('.bookings-table tbody');
        if (tableBody) {
            tableBody.innerHTML = '';

            if (bookings.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5">No bookings found.</td></tr>';
            }

            bookings.forEach(booking => {
                const row = document.createElement('tr');


                let actionBtn = '-';
                if (booking.status === 'completed') {
                    actionBtn = `<button class="btn-small" onclick="openReviewModal(${booking.id}, ${booking.provider_id})">Review</button>`;
                } else if (booking.status === 'confirmed' || booking.status === 'pending') {
                    actionBtn = `<button class="btn-small" style="background:#dc2626;" onclick="openComplaintModal(${booking.id})">Complaint</button>`;
                }

                row.innerHTML = `
                    <td>${booking.service_name}</td>
                    <td>Provider #${booking.provider_id}</td> 
                    <td>${booking.booking_date}</td>
                    <td><span class="badge ${booking.status}">${booking.status}</span></td>
                    <td>${actionBtn}</td>
                `;
                tableBody.appendChild(row);
            });
        }

        const statValues = document.querySelectorAll('.stat-value');
        if (statValues.length >= 2) {
            statValues[0].textContent = pending;
            statValues[1].textContent = confirmed;
        }

    } catch (err) {
        console.error('Failed to load bookings:', err);
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
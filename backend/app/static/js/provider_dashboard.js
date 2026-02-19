document.addEventListener('DOMContentLoaded', async () => {
    const user = JSON.parse(localStorage.getItem('user'));

    if (!user || user.role !== 'provider') {
        window.location.href = '/index.html';
        return;
    }


    let providerId = null;
    let currentBookings = [];

    try {
        // 1. Get Provider Profile
        const providers = await API.get('/providers/');
        const myProfile = providers.find(p => p.user_id === user.id);

        if (myProfile) {
            providerId = myProfile.id;
            document.getElementById('total-jobs').textContent = myProfile.total_bookings;

            // Set User Name in Header
            const nameDisplay = document.getElementById('provider-name-display');
            if (nameDisplay) nameDisplay.textContent = user.name;
        } else {
            console.error('Provider profile not found for user', user.id);
            alert('Error: Provider profile not found.');
            return;
        }

        // Initialize display values
        const earningsEl = document.getElementById('total-earnings');
        if (earningsEl) earningsEl.textContent = '₹0';

        // 2. Setup Tabs
        setupTabs();

        // 3. Load Bookings
        await loadProviderBookings(providerId);

        // 4. Setup Reschedule Form
        const rescheduleForm = document.getElementById('rescheduleForm');
        if (rescheduleForm) {
            rescheduleForm.addEventListener('submit', submitReschedule);
        }

        // 5. Setup Filter Listener
        setupFilterListener();

    } catch (err) {
        console.error('Error loading provider dashboard:', err);
    }

    function setupTabs() {
        const navLinks = document.querySelectorAll('.nav-link[data-page]');
        const pages = document.querySelectorAll('.page');

        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetPage = link.getAttribute('data-page');

                navLinks.forEach(nl => nl.classList.remove('active'));
                link.classList.add('active');

                pages.forEach(page => {
                    page.classList.remove('active');
                    if (page.id === `${targetPage}-page`) {
                        page.classList.add('active');
                    }
                });

                if (targetPage === 'reviews') {
                    loadProviderReviews(providerId);
                }
            });
        });
    }

    async function loadProviderReviews(id) {
        try {
            const container = document.querySelector('#reviews-page .reviews-container');
            if (!container) return;

            const reviews = await API.get(`/reviews/provider/${id}`);
            container.innerHTML = '';

            if (reviews.length === 0) {
                container.innerHTML = '<p style="text-align:center; padding: 20px; color: #666;">No reviews yet. Keep up the good work!</p>';
                return;
            }

            reviews.forEach(review => {
                const cName = review.customer?.name || "Customer";
                const card = document.createElement('div');
                card.className = 'review-card';
                card.innerHTML = `
                    <div class="review-header">
                        <div class="reviewer-info">
                            <img src="https://ui-avatars.com/api/?name=${cName}&background=random" alt="Reviewer" style="width:50px; height:50px; border-radius:50%; margin-right:12px;">
                            <div>
                                <p class="reviewer-name">Review by ${cName}</p>
                                <p class="review-service">Booking #${review.booking_id}</p>
                            </div>
                        </div>
                        <div class="review-rating">${review.rating}★</div>
                    </div>
                    <p class="review-text">${review.comment || 'No comment provided'}</p>
                    <p class="review-date">Posted on ${new Date(review.created_at).toLocaleDateString()}</p>
                `;
                container.appendChild(card);
            });
        } catch (err) {
            console.error('Failed to load provider reviews:', err);
        }
    }

    async function loadProviderBookings(id) {
        try {
            const bookings = await API.get(`/bookings/provider/${id}`);
            currentBookings = bookings;

            renderUpcomingJobs();
            renderAllJobs();
            calculateEarnings();
        } catch (err) {
            console.error('Failed to load bookings', err);
        }
    }

    function renderUpcomingJobs() {
        const tableBody = document.querySelector('#overview-page .bookings-table tbody');
        if (!tableBody) return;

        const upcoming = currentBookings.filter(b => ['pending', 'confirmed'].includes(b.status));

        tableBody.innerHTML = '';
        if (upcoming.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5">No upcoming jobs.</td></tr>';
            return;
        }

        upcoming.forEach(booking => {
            tableBody.appendChild(createBookingRow(booking));
        });
    }

    function renderAllJobs(statusFilter = 'All Status') {
        const tableBody = document.querySelector('#bookings-page .full-table tbody');
        if (!tableBody) return;

        let filtered = currentBookings;
        if (statusFilter !== 'All Status') {
            filtered = currentBookings.filter(b => b.status.replace(/_/g, ' ').toLowerCase() === statusFilter.toLowerCase());
        }

        tableBody.innerHTML = '';
        if (filtered.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:20px;">No ${statusFilter} jobs found.</td></tr>`;
            return;
        }

        filtered.forEach(booking => {
            tableBody.appendChild(createBookingRow(booking));
        });
    }

    function createBookingRow(booking) {
        const row = document.createElement('tr');
        const earnings = booking.provider_amount || (booking.total_amount * 0.85);
        const customerName = booking.customer?.name || `Customer #${booking.customer_id}`;

        let actions = '';
        if (booking.status === 'pending') {
            actions = `
                <button class="btn-small" onclick="updateStatus(${booking.id}, 'confirmed')" style="background:green; color:white;">Accept</button>
                <button class="btn-small" onclick="openRescheduleModal(${booking.id})" style="background:#f59e0b; color:white;">Reschedule</button>
                <button class="btn-small" onclick="cancelBooking(${booking.id})" style="background:red; color:white;">Reject</button>
            `;
        } else if (booking.status === 'confirmed') {
            actions = `
                <button class="btn-small" onclick="updateStatus(${booking.id}, 'completed')" style="background:blue; color:white;">Complete</button>
                <button class="btn-small" onclick="openRescheduleModal(${booking.id})" style="background:#f59e0b; color:white;">Reschedule</button>
            `;
        } else if (booking.status === 'reschedule_requested') {
            actions = `<span style="color:#d97706; font-size:0.8rem;">Waiting for customer...</span>`;
        } else {
            actions = '-';
        }

        row.innerHTML = `
            <td>
                <div style="display:flex; flex-direction:column;">
                    <span style="font-weight:600;">${customerName}</span>
                    <span style="font-size:0.8rem; color:#666;">${booking.address || 'No address'}</span>
                </div>
            </td>
            <td>${booking.booking_date}</td>
            <td>${booking.booking_time}</td>
            <td>
                <div style="display:flex; flex-direction:column;">
                    <span class="badge ${booking.status}">${booking.status.replace(/_/g, ' ')}</span>
                    <span style="font-size:0.75rem; color:#059669; margin-top:4px;">Earn: ₹${earnings.toFixed(2)}</span>
                </div>
            </td>
            <td>${actions}</td>
        `;
        return row;
    }

    function calculateEarnings() {
        const totalEarnings = currentBookings
            .filter(b => b.status.toLowerCase() === 'completed')
            .reduce((sum, b) => sum + (Number(b.provider_amount) || (Number(b.total_amount) * 0.85) || 0), 0);

        const earningsEl = document.getElementById('total-earnings');
        if (earningsEl) {
            earningsEl.textContent = '₹' + totalEarnings.toLocaleString();
        }
    }

    function setupFilterListener() {
        const filterSelect = document.querySelector('.filter-select');
        if (filterSelect) {
            filterSelect.addEventListener('change', (e) => {
                renderAllJobs(e.target.value);
            });
        }
    }

    // Global handles for layout actions
    window.openRescheduleModal = (bookingId) => {
        document.getElementById('rescheduleBookingId').value = bookingId;
        document.getElementById('rescheduleModal').style.display = 'flex';
    };

    window.closeModal = () => {
        document.getElementById('rescheduleModal').style.display = 'none';
        document.getElementById('rescheduleForm').reset();
    };

    async function submitReschedule(e) {
        e.preventDefault();
        const bookingId = document.getElementById('rescheduleBookingId').value;
        const date = document.getElementById('newDate').value;
        const time = document.getElementById('newTime').value;

        try {
            await API.request(`/bookings/${bookingId}/reschedule?suggested_date=${date}&suggested_time=${time}`, 'PATCH');
            alert('Reschedule request sent!');
            window.location.reload();
        } catch (err) {
            alert('Failed to send request: ' + err.message);
        }
    }

    window.updateStatus = async (bookingId, status) => {
        if (!confirm(`Mark booking as ${status}?`)) return;
        try {
            await API.request(`/bookings/${bookingId}/status?new_status=${status}`, 'PATCH');
            window.location.reload();
        } catch (err) {
            alert(err.message);
        }
    };

    window.cancelBooking = async (bookingId) => {
        if (!confirm('Reject this booking?')) return;
        try {
            await API.request(`/bookings/${bookingId}`, 'DELETE');
            window.location.reload();
        } catch (err) {
            alert(err.message);
        }
    };
});

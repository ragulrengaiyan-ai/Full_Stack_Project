document.addEventListener('DOMContentLoaded', async () => {
    const user = JSON.parse(localStorage.getItem('user'));

    if (!user || user.role !== 'provider') {
        window.location.href = '../index.html';
        return;
    }


    let providerId = null;
    try {
        const providers = await API.get('/providers/');
        const myProfile = providers.find(p => p.user_id === user.id);

        if (myProfile) {
            providerId = myProfile.id;
       
            document.getElementById('total-jobs').textContent = myProfile.total_bookings;
          
        } else {
            console.error('Provider profile not found for user', user.id);
            alert('Error: Provider profile not found.');
            return;
        }

        await loadProviderBookings(providerId);

    } catch (err) {
        console.error('Error loading provider dashboard:', err);
    }
});

async function loadProviderBookings(providerId) {
    try {
        const bookings = await API.get(`/bookings/provider/${providerId}`);
        const tableBody = document.querySelector('.bookings-table tbody');
        tableBody.innerHTML = '';

        let totalEarnings = 0;

        if (bookings.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5">No jobs found.</td></tr>';
        }

        bookings.forEach(booking => {
          
            if (booking.status === 'completed') {
                totalEarnings += booking.total_amount;
            }

            const row = document.createElement('tr');

           
            let actions = '';
            if (booking.status === 'pending') {
                actions = `
                    <button class="btn-small" onclick="updateStatus(${booking.id}, 'confirmed')" style="background:green; color:white;">Accept</button>
                    <button class="btn-small" onclick="cancelBooking(${booking.id})" style="background:red; color:white;">Reject</button>
                `;
            } else if (booking.status === 'confirmed') {
                actions = `
                    <button class="btn-small" onclick="updateStatus(${booking.id}, 'completed')" style="background:blue; color:white;">Complete</button>
                `;
            } else {
                actions = '-';
            }

          
            const customerDisplay = `Customer #${booking.customer_id}`;

            row.innerHTML = `
                <td>${customerDisplay}</td>
                <td>${booking.booking_date}</td>
                <td>${booking.booking_time}</td>
                <td><span class="badge ${booking.status}">${booking.status}</span></td>
                <td>${actions}</td>
            `;
            tableBody.appendChild(row);
        });

        document.getElementById('total-earnings').textContent = '₹' + totalEarnings;

    } catch (err) {
        console.error('Failed to load bookings', err);
    }
}

async function updateStatus(bookingId, status) {
    if (!confirm(`Mark booking as ${status}?`)) return;
    try {
        await API.request(`/bookings/${bookingId}/status?new_status=${status}`, 'PATCH');
        location.reload(); 
    } catch (err) {
        alert(err.message);
    }
}

async function cancelBooking(bookingId) {
    if (!confirm('Reject this booking?')) return;
    try {
        await API.request(`/bookings/${bookingId}`, 'DELETE');
        location.reload();
    } catch (err) {
        alert(err.message);
    }
}

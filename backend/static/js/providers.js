document.addEventListener('DOMContentLoaded', async () => {
    // SERVICE_TYPE should be defined in the HTML file before this script
    if (typeof SERVICE_TYPE === 'undefined') {
        console.error('SERVICE_TYPE is not defined');
        return;
    }

    await loadProviders(SERVICE_TYPE);

    // Initialise Modal logic
    setupBookingModal();
});

async function loadProviders(serviceType) {
    try {
        const providers = await API.get(`/providers/?service_type=${serviceType}`);
        const container = document.querySelector('.providers-list');

        if (!container) return;
        container.innerHTML = ''; // Clear placeholder

        if (providers.length === 0) {
            container.innerHTML = '<p>No providers found for this service.</p>';
            return;
        }

        providers.forEach(provider => {
            const card = createProviderCard(provider);
            container.appendChild(card);
        });

    } catch (err) {
        console.error('Failed to load providers:', err);
    }
}

function createProviderCard(provider) {
    const card = document.createElement('div');
    card.className = 'provider-card';

    // Status Logic
    const isAvailable = provider.availability_status === 'available';
    const statusClass = isAvailable ? 'available' : 'busy';
    const statusText = isAvailable ? 'Available' : 'Busy';
    const btnDisabled = !isAvailable ? 'disabled' : '';

    card.innerHTML = `
        <div class="provider-header">
            <img src="https://ui-avatars.com/api/?name=${provider.user.name}&background=random" alt="${provider.user.name}" class="provider-image">
            <div class="provider-info">
                <h2 class="provider-name">${provider.user.name}</h2>
                <div class="provider-meta">
                    <span class="meta-item">📍 ${provider.location || 'Unknown'}</span>
                    <span class="meta-item">⏱ ${provider.experience_years} years experience</span>
                </div>
            </div>
            <div class="provider-price">
                <span class="price-amount">₹${provider.hourly_rate}/hour</span>
                <div class="provider-rating">
                    <span class="star">★</span>
                    <span class="rating-value">${provider.rating} (${provider.total_bookings})</span>
                </div>
            </div>
        </div>

        <div class="provider-services">
           <p class="bio">${provider.bio || 'No bio available'}</p>
           <span class="service-badge ${statusClass}">${statusText}</span>
        </div>

        <div class="provider-actions">
            <button class="btn-secondary" onclick="viewProfile(${provider.id})">View Profile</button>
            <button class="btn-primary" onclick="openBookingModal(${provider.id}, '${provider.user.name}', ${provider.hourly_rate})" ${btnDisabled}>Book Now</button>
        </div>
    `;
    return card;
}

function setupBookingModal() {
    // Inject Modal HTML into body if not present
    if (!document.getElementById('bookingModal')) {
        const modalHTML = `
            <div id="bookingModal" class="modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100vh; background:rgba(0,0,0,0.5); z-index:1000; align-items:center; justify-content:center;">
                <div class="modal-content" style="background:white; padding:2rem; border-radius:8px; max-width:500px; width:90%;">
                    <h2>Book Service</h2>
                    <p id="modalProviderName">Provider: </p>
                    <p id="modalRate">Rate: </p>
                    <form id="bookingForm">
                        <input type="hidden" id="bookingProviderId">
                        <div class="form-group" style="margin-bottom:1rem;">
                            <label>Date</label>
                            <input type="date" id="bookingDate" required style="width:100%; padding:8px;">
                        </div>
                        <div class="form-group" style="margin-bottom:1rem;">
                            <label>Time</label>
                            <div style="display:flex; gap:10px;">
                                <select id="timeHour" style="flex:1; padding:8px;" required>
                                    <option value="">Hour</option>
                                    ${Array.from({ length: 12 }, (_, i) => `<option value="${i + 1}">${i + 1}</option>`).join('')}
                                </select>
                                <select id="timeMinute" style="flex:1; padding:8px;" required>
                                    <option value="00">00</option>
                                    <option value="15">15</option>
                                    <option value="30">30</option>
                                    <option value="45">45</option>
                                </select>
                                <select id="timePeriod" style="flex:1; padding:8px;" required>
                                    <option value="AM">AM</option>
                                    <option value="PM">PM</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-group" style="margin-bottom:1rem;">
                            <label>Duration (Hours)</label>
                            <input type="number" id="bookingDuration" value="1" min="1" required style="width:100%; padding:8px;">
                        </div>
                         <div class="form-group" style="margin-bottom:1rem;">
                            <label>Notes</label>
                            <textarea id="bookingNotes" style="width:100%; padding:8px;"></textarea>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-top:20px;">
                            <button type="button" onclick="closeBookingModal()" style="padding:10px 20px; border:none; background:#ccc; cursor:pointer;">Cancel</button>
                            <button type="submit" style="padding:10px 20px; border:none; background:#2563eb; color:white; cursor:pointer;">Confirm Booking</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    // Modal Form Submit
    const form = document.getElementById('bookingForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const user = JSON.parse(localStorage.getItem('user'));
        if (!user) {
            alert('Please login to book a service');
            window.location.href = '../htmlpages/login.html';
            return;
        }

        const data = {
            provider_id: document.getElementById('bookingProviderId').value,
            service_name: SERVICE_TYPE,
            booking_date: document.getElementById('bookingDate').value,
            booking_time: convertTo24Hour(
                document.getElementById('timeHour').value,
                document.getElementById('timeMinute').value,
                document.getElementById('timePeriod').value
            ),
            duration_hours: document.getElementById('bookingDuration').value,
            notes: document.getElementById('bookingNotes').value
        };

        try {
            // Need to pass customer_id? 
            // In our modified bookings.py, it expects `create_booking(booking: BookingCreate, customer_id: int)` 
            // But usually customer_id is extracted from token.
            // Since we modified to simple auth, we might need to send it as query param or update the backend to accept it in body.
            // Let's check bookings.py again. It uses `customer_id: int` as a path/query param or dependency.
            // Wait, standard FastAPI `customer_id: int` without `Body(...)` and not in path `{}` means query param.

            await API.post(`/bookings/?customer_id=${user.id}`, data);

            alert('Booking created successfully!');
            closeBookingModal();
            // Maybe redirect to dashboard
            window.location.href = '../htmlpages/dashboard.html';
        } catch (err) {
            alert(err.message);
        }
    });
}

function openBookingModal(providerId, providerName, rate) {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user) {
        alert('Please login to book a service');
        window.location.href = '../htmlpages/login.html';
        return;
    }

    document.getElementById('bookingModal').style.display = 'flex';
    document.getElementById('bookingProviderId').value = providerId;
    document.getElementById('modalProviderName').textContent = `Provider: ${providerName}`;
    document.getElementById('modalRate').textContent = `Rate: ₹${rate}/hour`;
}

function closeBookingModal() {
    document.getElementById('bookingModal').style.display = 'none';
}

function viewProfile(id) {
    alert('Profile view not implemented yet');
}
function convertTo24Hour(hour, minute, period) {
    let h = parseInt(hour);
    if (period === 'PM' && h < 12) h += 12;
    if (period === 'AM' && h === 12) h = 0;
    return `${h.toString().padStart(2, '0')}:${minute}:00`;
}

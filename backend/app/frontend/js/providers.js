document.addEventListener('DOMContentLoaded', async () => {

    if (typeof SERVICE_TYPE === 'undefined') {
        console.error('SERVICE_TYPE is not defined');
        return;
    }

    // Check for initial filters in URL
    const urlParams = new URLSearchParams(window.location.search);
    const initialLocation = urlParams.get('location');
    const initialDate = urlParams.get('date');
    const initialFilters = {};

    if (initialLocation) {
        initialFilters.location = initialLocation;
        const locationInput = document.querySelector('.filter-input');
        if (locationInput) locationInput.value = initialLocation;
    }

    if (initialDate) {
        initialFilters.booking_date = initialDate;
        const dateInput = document.querySelector('.filter-date');
        if (dateInput) dateInput.value = initialDate;
    }

    await loadProviders(SERVICE_TYPE, initialFilters);

    setupBookingModal();
    updateNavAuth();
});

function updateNavAuth() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (user) {
        const signInLink = document.getElementById('signInLink');
        const joinBtn = document.getElementById('joinBtn');

        if (signInLink) {
            signInLink.textContent = 'Dashboard';
            signInLink.href = user.role === 'admin' ? 'admin_dashboard.html' :
                user.role === 'provider' ? 'provider_dashboard.html' : 'dashboard.html';
        }

        if (joinBtn) {
            joinBtn.textContent = 'Sign Out';
            joinBtn.href = '#';
            joinBtn.onclick = (e) => {
                e.preventDefault();
                localStorage.removeItem('user');
                localStorage.removeItem('token');
                window.location.reload();
            };
        }
    }
}

async function loadProviders(serviceType, filters = {}) {
    try {
        let query = `/providers/?service_type=${serviceType}`;

        if (filters.location) query += `&location=${encodeURIComponent(filters.location)}`;
        if (filters.min_price) query += `&min_price=${filters.min_price}`;
        if (filters.max_price) query += `&max_price=${filters.max_price}`;
        if (filters.min_experience) query += `&min_experience=${filters.min_experience}`;
        if (filters.booking_date) query += `&booking_date=${filters.booking_date}`;
        if (filters.sort_by) query += `&sort_by=${filters.sort_by}`;

        const providers = await API.get(query);
        const container = document.querySelector('.providers-list');
        const countText = document.querySelector('.providers-count');

        if (!container) return;
        container.innerHTML = '';

        if (countText) {
            countText.textContent = `${providers.length} providers found`;
        }

        if (providers.length === 0) {
            container.innerHTML = '<div style="text-align:center; padding: 40px; color: #666;"><h3>No providers found</h3><p>Try adjusting your filters to find more results.</p></div>';
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

// Global Filter Logic
document.addEventListener('DOMContentLoaded', () => {
    const applyBtn = document.querySelector('.btn-apply-filters');
    const sortDropdown = document.querySelector('.sort-dropdown');

    if (applyBtn) {
        applyBtn.addEventListener('click', () => {
            const filters = {};
            const locationInput = document.querySelector('.filter-input');
            const selects = document.querySelectorAll('.filter-select');

            if (locationInput && locationInput.value) {
                filters.location = locationInput.value;
            }

            // Price range - usually the first select
            if (selects[0]) {
                const range = selects[0].value;
                if (range && range !== 'Select range') {
                    const prices = parsePriceRange(range);
                    if (prices.min) filters.min_price = prices.min;
                    if (prices.max) filters.max_price = prices.max;
                }
            }

            // Experience - usually the second select
            if (selects[1]) {
                const exp = selects[1].value;
                if (exp && exp !== 'Any experience') {
                    filters.min_experience = parseInt(exp.split('-')[0]) || parseInt(exp) || 0;
                }
            }

            // Add sorting if selected
            if (sortDropdown) {
                filters.sort_by = getSortValue(sortDropdown.value);
            }

            // Date - usually the third select OR a date input
            const dateInput = document.querySelector('.filter-date');
            if (dateInput && dateInput.value) {
                filters.booking_date = dateInput.value;
            }

            loadProviders(SERVICE_TYPE, filters);
        });
    }

    if (sortDropdown) {
        sortDropdown.addEventListener('change', () => {
            if (applyBtn) applyBtn.click(); // Trigger apply filters which includes sorting
        });
    }
});

function parsePriceRange(range) {
    const res = { min: null, max: null };
    if (range.includes('+')) {
        res.min = parseInt(range.replace(/[^0-9]/g, ''));
    } else if (range.includes('-')) {
        const parts = range.split('-').map(p => parseInt(p.replace(/[^0-9]/g, '')));
        res.min = parts[0];
        res.max = parts[1];
    }
    return res;
}

function getSortValue(text) {
    if (text.includes('rating')) return 'rating';
    if (text.includes('low to high')) return 'price_low';
    if (text.includes('high to low')) return 'price_high';
    if (text.includes('experience')) return 'experience';
    return 'rating';
}

function createProviderCard(provider) {
    const card = document.createElement('div');
    card.className = 'provider-card';

    if (!provider.user) {
        provider.user = { name: 'Verified Professional' };
    }

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
                    ${provider.address && provider.address !== provider.location ? `<span class="meta-item">🏠 Area: ${provider.address}</span>` : ''}
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

    if (!document.getElementById('bookingModal')) {
        const modalHTML = `
            <style>
                .modal-overlay {
                    position: fixed; top: 0; left: 0; width: 100%; height: 100vh;
                    background: rgba(0,0,0,0.6); z-index: 2000;
                    display: none; align-items: center; justify-content: center;
                    backdrop-filter: blur(4px);
                    transition: all 0.3s ease;
                }
                .modal-container {
                    background: white; border-radius: 16px; width: 90%; max-width: 500px;
                    padding: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    animation: modalSlideUp 0.4s ease-out;
                }
                @keyframes modalSlideUp {
                    from { transform: translateY(50px); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }
                .modal-title { font-size: 1.5rem; margin-bottom: 5px; color: #1a1a1a; }
                .modal-subtitle { color: #666; margin-bottom: 25px; font-size: 0.95rem; }
                .form-row { margin-bottom: 20px; }
                .form-row label { display: block; margin-bottom: 8px; font-weight: 600; font-size: 0.9rem; color: #444; }
                .form-row input, .form-row select, .form-row textarea {
                    width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px;
                    font-family: inherit; font-size: 1rem;
                }
                .form-row input:focus { border-color: #2563eb; outline: none; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }
                .modal-actions { display: flex; gap: 15px; margin-top: 30px; }
                .btn-cancel { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 8px; background: white; cursor: pointer; font-weight: 600; }
                .btn-confirm { flex: 2; padding: 12px; border: none; border-radius: 8px; background: #2563eb; color: white; cursor: pointer; font-weight: 600; }
                .btn-confirm:hover { background: #1d4ed8; }
            </style>
            <div id="bookingModal" class="modal-overlay">
                <div class="modal-container">
                    <h2 class="modal-title">Complete Your Booking</h2>
                    <p class="modal-subtitle" id="modalProviderName"></p>
                    <p id="modalRate" style="font-weight:700; color:#2563eb; margin-bottom:20px;"></p>
                    
                    <form id="bookingForm">
                        <input type="hidden" id="bookingProviderId">
                        
                        <div class="form-row">
                            <label>Service Date</label>
                            <input type="date" id="bookingDate" required>
                        </div>
                        
                        <div class="form-row">
                            <label>Start Time</label>
                            <div style="display:flex; gap:10px;">
                                <select id="timeHour" required>
                                    <option value="">Hour</option>
                                    ${Array.from({ length: 12 }, (_, i) => `<option value="${i + 1}">${i + 1}</option>`).join('')}
                                </select>
                                <select id="timeMinute" required>
                                    <option value="00">00</option>
                                    <option value="15">15</option>
                                    <option value="30">30</option>
                                    <option value="45">45</option>
                                </select>
                                <select id="timePeriod" required>
                                    <option value="AM">AM</option>
                                    <option value="PM">PM</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <label>Duration (Hours)</label>
                            <input type="number" id="bookingDuration" value="1" min="1" max="12" required>
                        </div>
                        
                        <div class="form-row">
                            <label>Service Address</label>
                            <textarea id="bookingAddress" placeholder="Enter full address for the professional" required rows="3"></textarea>
                        </div>
                        
                        <div class="form-row">
                            <label>Additional Notes (Optional)</label>
                            <textarea id="bookingNotes" placeholder="Any special instructions?" rows="2"></textarea>
                        </div>
                        
                        <div class="modal-actions">
                            <button type="button" class="btn-cancel" onclick="closeBookingModal()">Cancel</button>
                            <button type="submit" class="btn-confirm" id="confirmButton">Confirm Booking</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }


    const form = document.getElementById('bookingForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const user = JSON.parse(localStorage.getItem('user'));
        if (!user) {
            alert('Please login to book a service');
            window.location.href = '/login.html';
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
            address: document.getElementById('bookingAddress').value,
            notes: document.getElementById('bookingNotes') ? document.getElementById('bookingNotes').value : ""
        };

        try {
            await API.post(`/bookings/?customer_id=${user.id}`, data);

            alert('Booking created successfully!');
            closeBookingModal();

            window.location.href = '/dashboard.html';
        } catch (err) {
            alert(err.message);
        }
    });
}

function openBookingModal(providerId, providerName, rate) {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user) {
        alert('Please login to book a service');
        window.location.href = '/login.html';
        return;
    }

    document.getElementById('bookingModal').style.display = 'flex';
    document.getElementById('bookingProviderId').value = providerId;
    document.getElementById('modalProviderName').textContent = `Professional: ${providerName}`;
    document.getElementById('modalRate').textContent = `Rate: ₹${rate}/hour`;

    // Set min date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('bookingDate').setAttribute('min', today);
}

function closeBookingModal() {
    document.getElementById('bookingModal').style.display = 'none';
}

function viewProfile(id) {
    window.location.href = `/profile.html?id=${id}`;
}

function convertTo24Hour(hour, minute, period) {
    let h = parseInt(hour);
    if (!h) return "09:00:00"; // default
    if (period === 'PM' && h < 12) h += 12;
    if (period === 'AM' && h === 12) h = 0;
    return `${h.toString().padStart(2, '0')}:${minute}:00`;
}

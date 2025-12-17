document.addEventListener('DOMContentLoaded', () => {
    // Carousel Logic
    const carousel = document.getElementById('serviceCarousel');
    const leftBtn = document.querySelector('.scroll-btn.left');
    const rightBtn = document.querySelector('.scroll-btn.right');

    if (carousel && leftBtn && rightBtn) {
        leftBtn.addEventListener('click', () => {
            carousel.scrollBy({ left: -320, behavior: 'smooth' });
        });

        rightBtn.addEventListener('click', () => {
            carousel.scrollBy({ left: 320, behavior: 'smooth' });
        });
    }

    // Search Logic
    const searchBtn = document.querySelector('.search-button');
    const serviceSelect = document.querySelector('.service-select');
    const locationInput = document.querySelector('.location-input input');

    if (searchBtn && serviceSelect) {
        searchBtn.addEventListener('click', () => {
            const service = serviceSelect.value.toLowerCase();
            const location = locationInput ? locationInput.value.trim() : '';

            if (service === 'select service') {
                alert('Please select a service first.');
                return;
            }

            // Map service names to filenames if needed, or simple lowercase
            // filenames: babysitter.html, cook.html, housekeeper.html, gardener.html, security.html
            // options: Babysitter, Cook, Housekeeper, Gardener, Security

            const validServices = ['babysitter', 'cook', 'housekeeper', 'gardener', 'security'];
            if (validServices.includes(service)) {
                let targetUrl = `htmlpages/${service}.html`;
                // If location is provided, we could pass it? 
                // Currently pages don't filter by location via URL, but we can add it for future.
                if (location) {
                    targetUrl += `?location=${encodeURIComponent(location)}`;
                }
                window.location.href = targetUrl; // This assumes we are on index.html at root or static/index.html
                // Since index.html is in static/, htmlpages/service.html is correct.
            } else {
                alert('Service page not found.');
            }
        });
    }
});

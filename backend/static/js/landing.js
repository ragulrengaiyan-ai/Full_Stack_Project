document.addEventListener('DOMContentLoaded', () => {

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

       

            const validServices = ['babysitter', 'cook', 'housekeeper', 'gardener', 'security'];
            if (validServices.includes(service)) {
                let targetUrl = `htmlpages/${service}.html`;
           
                if (location) {
                    targetUrl += `?location=${encodeURIComponent(location)}`;
                }
                window.location.href = targetUrl; 
            } else {
                alert('Service page not found.');
            }
        });
    }
});

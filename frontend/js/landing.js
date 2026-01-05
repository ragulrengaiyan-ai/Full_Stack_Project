document.addEventListener('DOMContentLoaded', () => {

    const carousel = document.getElementById('serviceCarousel');
    const leftBtn = document.querySelector('.scroll-btn.left');
    const rightBtn = document.querySelector('.scroll-btn.right');

    if (carousel && leftBtn && rightBtn) {
        let isAutoPlaying = true;
        let autoPlayInterval;

        const startAutoPlay = () => {
            autoPlayInterval = setInterval(() => {
                if (isAutoPlaying) {
                    const scrollAmount = 350;
                    if (carousel.scrollLeft + carousel.offsetWidth >= carousel.scrollWidth - 10) {
                        carousel.scrollTo({ left: 0, behavior: 'smooth' });
                    } else {
                        carousel.scrollBy({ left: scrollAmount, behavior: 'smooth' });
                    }
                }
            }, 3000);
        };

        const stopAutoPlay = () => clearInterval(autoPlayInterval);

        // Scroll buttons
        leftBtn.addEventListener('click', () => {
            isAutoPlaying = false;
            carousel.scrollBy({ left: -350, behavior: 'smooth' });
            setTimeout(() => isAutoPlaying = true, 5000); // Resume after 5s
        });

        rightBtn.addEventListener('click', () => {
            isAutoPlaying = false;
            carousel.scrollBy({ left: 350, behavior: 'smooth' });
            setTimeout(() => isAutoPlaying = true, 5000); // Resume after 5s
        });

        // Track active card for 3D effect
        const updateActiveCard = () => {
            const cards = carousel.querySelectorAll('.service-card');
            const carouselRect = carousel.getBoundingClientRect();
            const centerX = carouselRect.left + carouselRect.width / 2;

            let closestCard = null;
            let minDistance = Infinity;

            cards.forEach(card => {
                const rect = card.getBoundingClientRect();
                const cardMidX = rect.left + rect.width / 2;
                const distance = Math.abs(centerX - cardMidX);

                if (distance < minDistance) {
                    minDistance = distance;
                    closestCard = card;
                }
                card.classList.remove('active');
            });

            if (closestCard) closestCard.classList.add('active');
        };

        // Flip Logic
        const cards = carousel.querySelectorAll('.service-card');
        cards.forEach(card => {
            card.addEventListener('click', (e) => {
                // Don't flip if clicking the action button
                if (e.target.classList.contains('btn-flip-action')) return;

                const isFlipped = card.classList.contains('flipped');

                // Unflip all other cards
                cards.forEach(c => c.classList.remove('flipped'));

                // Toggle current card
                if (!isFlipped) {
                    card.classList.add('flipped');
                    isAutoPlaying = false; // Pause while exploring
                    setTimeout(() => isAutoPlaying = true, 10000); // Resume after 10s
                } else {
                    card.classList.remove('flipped');
                }
            });
        });

        carousel.addEventListener('scroll', updateActiveCard);
        carousel.addEventListener('mouseenter', () => isAutoPlaying = false);
        carousel.addEventListener('mouseleave', () => isAutoPlaying = true);

        // Initial setup
        startAutoPlay();
        setTimeout(updateActiveCard, 100);
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
                let targetUrl = `/${service}.html`;

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

document.addEventListener('DOMContentLoaded', () => {
    // Check for Login Form
    const loginForm = document.querySelector('.login-container form');
    if (loginForm) {
        handleLogin(loginForm);
    }

    // Check for Customer Signup Form
    const customerForm = document.getElementById('customerFormElement');
    if (customerForm) {
        handleCustomerSignup(customerForm);
    }

    // Check for Provider Signup Form
    const providerForm = document.getElementById('providerFormElement');
    if (providerForm) {
        handleProviderSignup(providerForm);
    }

    // Check for Logout Button (if any)
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }

    // Update UI based on Auth State
    updateNavAuth();
});

async function handleLogin(form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const res = await API.post('/users/login', { email, password });

            // Store User in LocalStorage (Simple Auth)
            localStorage.setItem('user', JSON.stringify(res.user));

            alert('Login successful!');

            // Redirect based on role
            if (res.user.role === 'provider') {
                window.location.href = '/static/htmlpages/provider_dashboard.html';
            } else if (res.user.role === 'admin') {
                window.location.href = '/static/htmlpages/admin_dashboard.html';
            } else {
                window.location.href = '/static/htmlpages/dashboard.html';
            }
        } catch (err) {
            alert(err.message);
        }
    });
}

async function handleCustomerSignup(form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        try {
            const res = await API.post('/users/register/customer', data);
            alert('Customer account created! Please sign in.');
            window.location.href = '/static/htmlpages/login.html';
        } catch (err) {
            alert(err.message);
        }
    });
}

async function handleProviderSignup(form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Ensure numeric fields are numbers
        data.hourly_rate = Number(data.hourly_rate);
        data.experience_years = Number(data.experience_years);

        // Add hardcoded location/bio if missing (though hidden inputs should handle it)
        if (!data.location) data.location = "Chennai";
        if (!data.bio) data.bio = "Service provider";

        try {
            const res = await API.post('/users/register/provider', data);
            alert('Provider account created! Please sign in.');
            window.location.href = '/static/htmlpages/login.html';
        } catch (err) {
            alert(err.message);
        }
    });
}

function updateNavAuth() {
    const user = JSON.parse(localStorage.getItem('user'));
    const nav = document.querySelector('nav');

    if (user && nav) {
        // Find "Sign in" and "Join Now" links and replace with "Profile" / "Logout"
        const links = nav.querySelectorAll('a');
        let signInLink = null;
        let joinLink = null;

        links.forEach(link => {
            if (link.textContent.includes('Sign in')) signInLink = link;
            if (link.textContent.includes('Join Now')) joinLink = link;
        });

        if (signInLink) {
            signInLink.textContent = user.name.split(' ')[0]; // Show First Name
            // If we are in index.html (root/static), path to dashboard is htmlpages/dashboard.html
            // If we are in htmlpages/, path is dashboard.html
            // Simple heuristic: check current path
            const dashboardPath = user.role === 'provider' ?
                '/static/htmlpages/provider_dashboard.html' :
                '/static/htmlpages/dashboard.html';

            signInLink.href = dashboardPath;
        }

        if (joinLink) {
            joinLink.textContent = 'Logout';
            joinLink.href = '#';
            joinLink.addEventListener('click', (e) => {
                e.preventDefault();
                logout();
            });
        }
    }
}

function logout() {
    localStorage.removeItem('user');
    // If in htmlpages, go up; if in index, stay
    window.location.href = '/static/index.html';
}
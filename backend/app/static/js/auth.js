document.addEventListener('DOMContentLoaded', () => {

    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        handleLogin(loginForm);
    }


    const customerForm = document.getElementById('customerFormElement');
    if (customerForm) {
        handleCustomerSignup(customerForm);
    }


    const providerForm = document.getElementById('providerFormElement');
    if (providerForm) {
        handleProviderSignup(providerForm);
    }


    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }


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
            if (res.access_token) {
                localStorage.setItem('token', res.access_token);
            }

            alert('Login successful!');

            // Redirect based on role
            if (res.user.role === 'provider') {
                window.location.href = '/provider_dashboard.html';
            } else if (res.user.role === 'admin') {
                window.location.href = '/admin_dashboard.html';
            } else {
                window.location.href = '/dashboard.html';
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
            window.location.href = '/login.html';
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

        // Add hardcoded bio if missing
        if (!data.bio) data.bio = "Dedicated service provider";

        try {
            const res = await API.post('/users/register/provider', data);
            alert('Provider account created! Please sign in.');
            window.location.href = '/login.html';
        } catch (err) {
            alert(err.message);
        }
    });
}

function updateNavAuth() {
    const user = JSON.parse(localStorage.getItem('user'));
    const nav = document.querySelector('nav');

    if (user && nav) {
        const links = nav.querySelectorAll('a');
        let signInLink = null;
        let joinLink = null;

        links.forEach(link => {
            if (link.textContent.includes('Sign in') || link.textContent === user.name.split(' ')[0]) signInLink = link;
            if (link.textContent.includes('Join Now') || link.textContent === 'Logout') joinLink = link;
        });

        if (signInLink) {
            signInLink.textContent = user.name.split(' ')[0];
            let dashboardPath = 'dashboard.html';
            if (user.role === 'provider') {
                dashboardPath = 'provider_dashboard.html';
            } else if (user.role === 'admin') {
                dashboardPath = 'admin_dashboard.html';
            }
            signInLink.href = dashboardPath;
        }

        if (joinLink) {
            joinLink.textContent = 'Logout';
            joinLink.href = '#';
            joinLink.onclick = (e) => {
                e.preventDefault();
                localStorage.removeItem('user');
                localStorage.removeItem('token');
                window.location.href = 'index.html';
            };
        }
    }
}

function logout() {
    localStorage.removeItem('user');
    window.location.href = '/index.html';
}


// “I implemented client-side authentication handling using a shared JavaScript module that manages login, signup, logout, role-based routing, and dynamic navbar updates using JWT tokens stored in localStorage.”
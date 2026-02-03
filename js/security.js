(function () {
    // List of pages that can be accessed without logging in
    const publicPages = ['index.html', 'about.html', 'contact.html', 'login.html', 'join.html', ''];

    // Get the current page name from the URL
    const pathname = window.location.pathname;
    const currentPage = pathname.split('/').pop() || 'index.html';

    // If the current page is not in the public list, check for authentication
    if (!publicPages.includes(currentPage)) {
        const token = localStorage.getItem('token');
        const user = localStorage.getItem('user');

        // If no token or user data found, redirect to login page
        if (!token || !user) {
            console.log('Access denied. Redirecting to login...');
            window.location.href = 'login.html';
        }
    }
})();

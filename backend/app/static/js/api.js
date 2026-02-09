class API {
    static async request(endpoint, method = 'GET', data = null) {
        const url = `${API_BASE_URL}${endpoint}`;
        const token = localStorage.getItem('token');
        const headers = {
            'Content-Type': 'application/json'
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            method,
            headers
        };

        if (data) {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, config);
            let responseData;

            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                responseData = await response.json();
            } else {
                responseData = { detail: await response.text() };
            }

            if (!response.ok) {
                // Try to get the most useful error message
                let errorDetails = responseData.detail || responseData.message;

                if (!errorDetails) {
                    if (typeof responseData === 'string') {
                        errorDetails = responseData;
                    } else {
                        errorDetails = JSON.stringify(responseData);
                    }
                }

                if (!errorDetails || errorDetails === '{}') {
                    errorDetails = response.statusText;
                }

                throw new Error(`HTTP ${response.status}: ${errorDetails}`);
            }

            return responseData;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    static async post(endpoint, data) {
        return this.request(endpoint, 'POST', data);
    }

    static async get(endpoint) {
        return this.request(endpoint, 'GET');
    }

    static async put(endpoint, data) {
        return this.request(endpoint, 'PUT', data);
    }
}


// “I created a centralized API utility class that wraps the Fetch API. It automatically attaches JWT tokens, handles JSON and non-JSON responses, standardizes error handling, and reduces duplicate code across the frontend.”
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
                // Return a more descriptive error if it's a known non-JSON format like 'Internal Server Error' string
                const errorMsg = responseData.detail || responseData.message || (typeof responseData === 'string' ? responseData : 'Something went wrong');
                throw new Error(errorMsg);
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

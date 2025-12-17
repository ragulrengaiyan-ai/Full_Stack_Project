class API {
    static async request(endpoint, method = 'GET', data = null) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json'
        };

        const config = {
            method,
            headers
        };

        if (data) {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, config);
            const responseData = await response.json();

            if (!response.ok) {
                throw new Error(responseData.detail || 'Something went wrong');
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

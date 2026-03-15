import axios from 'axios';

// Use nginx proxy path instead of direct port
// Direct link to your Railway backend
export const BASE_URL = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
    ? 'https://brain-stroke-detection-production.up.railway.app' 
    : 'http://localhost:8000';

const api = axios.create({
    baseURL: BASE_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const login = async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    const response = await api.post('/auth/login', formData);
    if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
    }
    return response.data;
};

export const register = async (email, password, full_name) => {
    const response = await api.post('/auth/register', { email, password, full_name });
    return response.data;
};

export const getMe = async () => {
    const response = await api.get('/auth/me');
    return response.data;
};

export const predictScan = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/predict/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const getHistory = async () => {
    const response = await api.get('/predict/history');
    return response.data;
};

export const askChatbot = async (message, context, history = []) => {
    const response = await api.post('/chatbot/ask', { 
        message, 
        current_context: context,
        chat_history: history 
    });
    return response.data;
};

export default api;

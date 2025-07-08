// Uygulama Yapılandırması
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000', // Backend API URL'ini buraya yazın
    TOKEN_KEY: 'access_token',
    ENDPOINTS: {
        LOGIN: '/api/login',
        REGISTER: '/api/register',
        REFRESH: '/api/token/refresh'
    }
};

// Toast Notification Sistemi
class ToastNotification {
    constructor() {
        this.toastElement = document.getElementById('toast');
        this.toastIcon = this.toastElement.querySelector('.toast-icon');
        this.toastMessage = this.toastElement.querySelector('.toast-message');
        this.hideTimeout = null;
    }

    show(message, type = 'success', duration = 4000) {
        // Önceki toast'u temizle
        this.hide();
        
        // Toast içeriğini güncelle
        this.toastMessage.textContent = message;
        this.toastElement.className = `toast ${type}`;
        
        // İkon'u güncelle
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        this.toastIcon.className = `toast-icon ${icons[type] || icons.success}`;
        
        // Toast'u göster
        this.toastElement.classList.add('show');
        
        // Otomatik gizleme
        this.hideTimeout = setTimeout(() => {
            this.hide();
        }, duration);
        
        // Tıklama ile kapat
        this.toastElement.onclick = () => this.hide();
    }

    hide() {
        if (this.hideTimeout) {
            clearTimeout(this.hideTimeout);
            this.hideTimeout = null;
        }
        this.toastElement.classList.remove('show');
        this.toastElement.onclick = null;
    }
}

// Form Validator
class FormValidator {
    constructor() {
        this.rules = {
            username: {
                required: true,
                minLength: 3,
                maxLength: 20,
                pattern: /^[a-zA-Z0-9_-]+$/
            },
            email: {
                required: true,
                pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
            },
            password: {
                required: true,
                minLength: 6,
                maxLength: 50
            }
        };
    }

    validate(fieldName, value) {
        const rule = this.rules[fieldName];
        if (!rule) return { isValid: true };

        const errors = [];

        // Required check
        if (rule.required && (!value || value.trim() === '')) {
            errors.push('Bu alan zorunludur');
        }

        if (value && value.trim() !== '') {
            // Min length check
            if (rule.minLength && value.length < rule.minLength) {
                errors.push(`En az ${rule.minLength} karakter olmalı`);
            }

            // Max length check
            if (rule.maxLength && value.length > rule.maxLength) {
                errors.push(`En fazla ${rule.maxLength} karakter olmalı`);
            }

            // Pattern check
            if (rule.pattern && !rule.pattern.test(value)) {
                if (fieldName === 'email') {
                    errors.push('Geçerli bir e-posta adresi giriniz');
                } else if (fieldName === 'username') {
                    errors.push('Sadece harf, rakam, tire ve alt çizgi kullanabilirsiniz');
                }
            }
        }

        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }

    validateForm(formData) {
        const results = {};
        let isFormValid = true;

        for (const [fieldName, value] of Object.entries(formData)) {
            const result = this.validate(fieldName, value);
            results[fieldName] = result;
            if (!result.isValid) {
                isFormValid = false;
            }
        }

        // Password confirmation check
        if (formData.password && formData.confirmPassword) {
            if (formData.password !== formData.confirmPassword) {
                results.confirmPassword = {
                    isValid: false,
                    errors: ['Şifreler eşleşmiyor']
                };
                isFormValid = false;
            }
        }

        return {
            isValid: isFormValid,
            fields: results
        };
    }
}

// API Client
class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        // Token varsa header'a ekle
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);
        if (token) {
            defaultOptions.headers['Authorization'] = `Bearer ${token}`;
        }

        const finalOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, finalOptions);
            
            let data;
            try {
                data = await response.json();
            } catch (parseError) {
                throw new Error('Sunucudan geçersiz yanıt alındı');
            }

            if (!response.ok) {
                // Validation errors için detaylı mesaj
                if (response.status === 422 && data.detail && Array.isArray(data.detail)) {
                    const errorMessages = data.detail.map(err => 
                        `${err.loc ? err.loc.join('.') : 'field'}: ${err.msg}`
                    ).join(', ');
                    throw new Error(`Doğrulama hatası: ${errorMessages}`);
                }
                
                throw new Error(data.detail || data.message || 'Bir hata oluştu');
            }

            return data;
        } catch (error) {
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('Sunucuya bağlanılamadı. Lütfen daha sonra tekrar deneyin.');
            }
            throw error;
        }
    }

    async login(username, password) {
        // OAuth2PasswordRequestForm için application/x-www-form-urlencoded formatı
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        return await this.makeRequest(CONFIG.ENDPOINTS.LOGIN, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData,
        });
    }

    async register(userData) {
        return await this.makeRequest(CONFIG.ENDPOINTS.REGISTER, {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    }
}

// Password Toggle Functionality
class PasswordToggle {
    constructor() {
        this.setupToggleButtons();
    }

    setupToggleButtons() {
        const toggleButtons = document.querySelectorAll('.password-toggle');
        toggleButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const inputContainer = e.target.closest('.input-container');
                const passwordInput = inputContainer.querySelector('input[type="password"], input[type="text"]');
                
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    e.target.classList.remove('fa-eye-slash');
                    e.target.classList.add('fa-eye');
                } else {
                    passwordInput.type = 'password';
                    e.target.classList.remove('fa-eye');
                    e.target.classList.add('fa-eye-slash');
                }
            });
        });
    }
}

// Form Handler
class FormHandler {
    constructor() {
        this.toast = new ToastNotification();
        this.validator = new FormValidator();
        this.apiClient = new APIClient(CONFIG.API_BASE_URL);
        this.passwordToggle = new PasswordToggle();
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Login Form
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', this.handleLogin.bind(this));
            this.setupRealTimeValidation('loginForm');
        }

        // Register Form
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', this.handleRegister.bind(this));
            this.setupRealTimeValidation('registerForm');
        }
    }

    setupRealTimeValidation(formId) {
        const form = document.getElementById(formId);
        const inputs = form.querySelectorAll('input');
        
        inputs.forEach(input => {
            input.addEventListener('blur', (e) => {
                this.validateField(e.target);
            });
            
            input.addEventListener('input', (e) => {
                // Hata mesajını temizle
                this.clearFieldError(e.target);
            });
        });
    }

    validateField(field) {
        const fieldName = field.id;
        const value = field.value.trim();
        
        // Confirm password için özel kontrol
        if (fieldName === 'confirmPassword') {
            const passwordField = document.getElementById('password');
            const passwordValue = passwordField ? passwordField.value : '';
            
            if (value !== passwordValue) {
                this.showFieldError(field, 'Şifreler eşleşmiyor');
                return false;
            }
        } else {
            const result = this.validator.validate(fieldName, value);
            if (!result.isValid) {
                this.showFieldError(field, result.errors[0]);
                return false;
            }
        }

        this.clearFieldError(field);
        return true;
    }

    showFieldError(field, message) {
        const errorElement = document.getElementById(field.id + 'Error');
        if (errorElement) {
            errorElement.textContent = message;
        }
        field.classList.add('error');
    }

    clearFieldError(field) {
        const errorElement = document.getElementById(field.id + 'Error');
        if (errorElement) {
            errorElement.textContent = '';
        }
        field.classList.remove('error');
    }

    showLoading(button) {
        button.disabled = true;
        button.classList.add('loading');
    }

    hideLoading(button) {
        button.disabled = false;
        button.classList.remove('loading');
    }

    async handleLogin(e) {
        e.preventDefault();
        
        const form = e.target;
        const button = form.querySelector('button[type="submit"]');
        const formData = new FormData(form);
        
        const username = formData.get('username') || document.getElementById('username').value;
        const password = formData.get('password') || document.getElementById('password').value;

        // Validation
        const validationResult = this.validator.validateForm({ username, password });
        
        if (!validationResult.isValid) {
            this.showValidationErrors(validationResult.fields);
            return;
        }

        this.showLoading(button);

        try {
            const response = await this.apiClient.login(username, password);
            
            // Token'ı localStorage'a kaydet
            localStorage.setItem(CONFIG.TOKEN_KEY, response.access_token);
            
            this.toast.show('Giriş başarılı! Yönlendiriliyorsunuz...', 'success');
            
            // Dashboard'a yönlendir, orada profil kontrolü yapılacak
            setTimeout(() => {
                window.location.href = '/static/dashboard.html';
            }, 1500);
            
        } catch (error) {
            this.toast.show(error.message, 'error');
        } finally {
            this.hideLoading(button);
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        
        const form = e.target;
        const button = form.querySelector('button[type="submit"]');
        const formData = new FormData(form);
        
        const userData = {
            username: formData.get('username') || document.getElementById('username').value,
            email: formData.get('email') || document.getElementById('email').value,
            password: formData.get('password') || document.getElementById('password').value,
            confirmPassword: document.getElementById('confirmPassword').value
        };

        // Validation
        const validationResult = this.validator.validateForm(userData);
        
        if (!validationResult.isValid) {
            this.showValidationErrors(validationResult.fields);
            return;
        }

        this.showLoading(button);

        try {
            // confirmPassword'u API'ye gönderme ve eksik alanları ekle
            const { confirmPassword, ...apiData } = userData;
            
            // Eksik alanları null olarak ekle
            const completeData = {
                ...apiData,
                full_name: null,
                profession: null,
                experience_level: null,
                career_goals: null
            };
            
            const response = await this.apiClient.register(completeData);
            
            this.toast.show('Kayıt başarılı! Giriş sayfasına yönlendiriliyorsunuz...', 'success');
            
            // Login sayfasına yönlendir
            setTimeout(() => {
                window.location.href = '/static/login.html';
            }, 1500);
            
        } catch (error) {
            this.toast.show(error.message, 'error');
        } finally {
            this.hideLoading(button);
        }
    }

    showValidationErrors(fields) {
        for (const [fieldName, result] of Object.entries(fields)) {
            if (!result.isValid) {
                const field = document.getElementById(fieldName);
                if (field) {
                    this.showFieldError(field, result.errors[0]);
                }
            }
        }
    }
}

// Authentication Check
class AuthManager {
    constructor() {
        this.token = localStorage.getItem(CONFIG.TOKEN_KEY);
    }

    isAuthenticated() {
        return !!this.token;
    }

    logout() {
        localStorage.removeItem(CONFIG.TOKEN_KEY);
        window.location.href = '/static/login.html';
    }

    getToken() {
        return this.token;
    }

    // Token'ın geçerliliğini kontrol et (JWT decode gerektirir)
    isTokenValid() {
        if (!this.token) return false;
        
        try {
            const payload = JSON.parse(atob(this.token.split('.')[1]));
            const currentTime = Date.now() / 1000;
            return payload.exp > currentTime;
        } catch (error) {
            return false;
        }
    }
}

// Utility Functions
const Utils = {
    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Sanitize input
    sanitizeInput(input) {
        const div = document.createElement('div');
        div.textContent = input;
        return div.innerHTML;
    },

    // Format error message
    formatErrorMessage(error) {
        if (typeof error === 'string') return error;
        if (error.message) return error.message;
        return 'Bilinmeyen bir hata oluştu';
    }
};



// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    // Form handler'ı başlat
    const formHandler = new FormHandler();
    
    // Auth manager'ı başlat
    const authManager = new AuthManager();
    
    // Otomatik yönlendirme kaldırıldı - Manuel login gerekli
    
    // Accessibility improvements
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && input.type !== 'submit') {
                const form = input.closest('form');
                const nextInput = form.querySelector(`input[tabindex="${parseInt(input.tabIndex) + 1}"]`);
                if (nextInput) {
                    nextInput.focus();
                } else {
                    const submitButton = form.querySelector('button[type="submit"]');
                    if (submitButton) {
                        submitButton.click();
                    }
                }
            }
        });
    });
    
    // Set tab indexes for better keyboard navigation
    const allInputs = document.querySelectorAll('input, button');
    allInputs.forEach((element, index) => {
        element.setAttribute('tabindex', index + 1);
    });
});

// Export for use in other files if needed
window.FormHandler = FormHandler;
window.AuthManager = AuthManager;
window.ToastNotification = ToastNotification; 
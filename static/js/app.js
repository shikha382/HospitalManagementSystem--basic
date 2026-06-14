const { createApp } = Vue;
const app = createApp({
    data() {
        return {
            user: null,
            token: null
        };
    },
    mounted() {
        const savedToken = localStorage.getItem('token');
        const savedUser = localStorage.getItem('user');
        if (savedToken && savedUser) {
            this.token = savedToken;
            this.user = JSON.parse(savedUser);
            if (window.location.pathname === '/login' || window.location.pathname === '/') {
                this.syncUrl();
            }
        } else {
            if (window.location.pathname !== '/login') {
                window.history.replaceState({}, '', '/login');
            }
        }
        window.onpopstate = () => { this.handleUrlChange(); };
    },
    methods: {
        onLoginSuccess(data) {
            this.token = data.token;
            this.user = data.user;
            localStorage.setItem('token', this.token);
            localStorage.setItem('user', JSON.stringify(this.user));
            this.syncUrl();
        },
        logout() {
            this.user = null;
            this.token = null;
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        },
        syncUrl() {
            if (!this.user) return;
            const path = `/${this.user.role}/dashboard`;
            if (window.location.pathname !== path) {
                window.history.pushState({}, '', path);
            }
        },
        handleUrlChange() {
            const path = window.location.pathname;
            if (!this.user && (path.includes('dashboard') || path === '/')) {
                window.history.pushState({}, '', '/login');
            }
            if (this.user && path === '/login') {
                this.syncUrl();
            }
        }
    }
});
app.component('login-form', LoginForm);
app.component('admin-dashboard', AdminDashboard);
app.component('doctor-dashboard', DoctorDashboard);
app.component('patient-dashboard', PatientDashboard);
app.mount('#app');

const LoginForm = {
  template: `
  <div class="container d-flex align-items-center justify-content-center min-vh-100">
    <div class="card border-0 shadow-lg p-0 animate-fade-in overflow-hidden" 
         style="max-width: 900px; width: 100%; background:lightblue; border-radius: 30px;">
      <div class="row g-0">
        <div class="col-md-6 d-none d-md-block p-4" style="background: #fbf6dd;">
           <div class="h-100 rounded-4 " style="border: 1px solid #e2e8f0;">
              <img src="/static/images/hero.png" class="w-100 h-100" style="object-fit: cover; opacity: 1;">
           </div>
        </div>
        <div class="col-md-6 p-5">
        <div class="text-center mb-4">
          <div class="mb-3">
             <img src="/static/images/logo.png" class="img-fluid" style="max-height: 100px; transition: transform 0.3s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
          </div>
          <h2 class="fw-bold" style="color: var(--primary);">Ur R Precious</h2>
          <p class="text-muted small">Your health companion 🏥✨</p>
        </div>
          <div class="nav nav-pills mb-4 justify-content-center bg-light p-1 rounded-pill">
            <button class="nav-link border-0" :class="{active: authMode === 'login'}" @click="authMode = 'login'">Login</button>
            <button class="nav-link border-0" :class="{active: authMode === 'register'}" @click="authMode = 'register'">Register</button>
          </div>
          <form v-if="authMode === 'login'" @submit.prevent="onLogin" class="animate-fade-in">
            <div class="mb-3">
              <label class="small fw-bold text-muted mb-1 ms-2">Username</label>
              <input type="text" class="form-control" v-model="loginForm.username" required placeholder="admin">
            </div>
            <div class="mb-4">
              <label class="small fw-bold text-muted mb-1 ms-2">Password</label>
              <input type="password" class="form-control" v-model="loginForm.password" required placeholder="••••••••">
            </div>
            <div v-if="error" class="alert alert-danger py-2 small border-0 mb-3 rounded-pill text-center">
               {{ error }}
            </div>
            <button type="submit" class="btn btn-primary w-100 py-3 rounded-pill fw-bold shadow-sm" :style="{backgroundColor: color}">
                ENTER 🚀
            </button>
          </form>
          <form v-if="authMode === 'register'" @submit.prevent="onRegister" class="row g-3 animate-fade-in" style="max-height: 400px; overflow-y: auto;">
            <div class="col-12"><input type="text" class="form-control" v-model="registerForm.username" placeholder="Username" required></div>
            <div class="col-12"><input type="text" class="form-control" v-model="registerForm.name" placeholder="Full Name" required></div>
            <div class="col-12"><input type="number" class="form-control" v-model="registerForm.age" placeholder="Age" required></div>
            <div class="col-12"><input type="text" class="form-control" v-model="registerForm.contact" placeholder="Phone No" required></div>
            <div class="col-12"><input type="email  " class="form-control" v-model="registerForm.email" placeholder="Email address" required></div>
            <div class="col-12"><input type="password" class="form-control" v-model="registerForm.password" placeholder="Password" required></div>
            <div class="col-12"><button type="submit" class="btn btn-primary w-100 py-3 rounded-pill fw-bold shadow-sm" style="background-color: #6a084b; border-color: #6a080a;">Start My Journey! 🌿</button></div>
          </form>
          <div class="text-center mt-4 opacity-50">
          </div>
        </div>
      </div>
    </div>
  </div>
  `,
  data() {
    return {
      authMode: 'login',
      loginForm: { username: '', password: '' },
      registerForm: { username: '', email: '', password: '', name: '', age: '', gender: 'Male', contact: '' },
      error: null,
      success: null,
      color: "red"
    }
  },
  methods: {
    async onLogin() {
      try {
        this.error = null;
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.loginForm)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Login failed');
        this.$emit('login-success', data);
      } catch (e) { this.error = e.message; }
    },
    async onRegister() {
      try {
        this.error = null; this.success = null;
        const res = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.registerForm)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Registration failed');
        this.success = 'Registration successful! Please login.';
        this.authMode = 'login';
      } catch (e) { this.error = e.message; }
    }
  }
};
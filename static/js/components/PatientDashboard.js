const PatientDashboard = {
  props: ['token'],

  template: `
  <div class="container py-4">

    <h3 class="fw-bold mb-4" style="color:var(--primary)">🧸 Patient Dashboard</h3>

    <ul class="nav nav-pills mb-4">
      <li class="nav-item"><button class="nav-link" :class="{active:tab==='home'}" @click="tab='home'">Home</button></li>
      <li class="nav-item"><button class="nav-link" :class="{active:tab==='doctors'}" @click="tab='doctors'">Doctors</button></li>
      <li class="nav-item"><button class="nav-link" :class="{active:tab==='history'}" @click="tab='history'">History</button></li>
    </ul>

    <!-- HOME TAB -->
    <div v-if="tab==='home'">
      <div class="row g-4">

        <div class="col-md-4">
          <div class="card p-4" style="border: 2px solid #ffeb3b !important;">
            <h5 class="fw-bold">My Summary</h5>
            <hr>
            <p class="mb-3">Total Completed Visits: <strong>{{ history.length }}</strong></p>
            <div class="d-grid gap-2">
              <button class="btn text-white" style="background-color: #e91e63 !important; border: none !important;" @click="goBookDoctor">Book New Visit</button>
              <button class="btn text-white" style="background-color: #ff9800 !important; border: none !important;" @click="showProfile=true">Edit Profile</button>
            </div>
          </div>
        </div>

        <div class="col-md-8">
          <div class="card overflow-hidden" style="border: 2px solid #ffeb3b !important;">
            <div class="card-header py-3" style="background-color: #e91e63 !important; color: white !important;">
              <h6 class="mb-0 fw-bold">Upcoming Appointments</h6>
            </div>
            <div class="card-body p-0">
              <div v-if="upcoming.length===0" class="text-center text-muted py-5">
                No upcoming visits scheduled.
              </div>
              <ul class="list-group list-group-flush" v-else>
                <li v-for="a in upcoming" :key="a.id" class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <div>
                    <div class="fw-bold">Dr. {{ a.doctor_name }}</div>
                    <small class="text-muted">{{ a.date }} at {{ a.time }} ({{ a.specialization }})</small>
                  </div>
                  <button class="btn btn-sm text-white" style="background-color: #ff9800 !important; border: none !important;" @click="cancelAppt(a.id)">Cancel</button>
                </li>
              </ul>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- DOCTORS TAB -->
    <div v-if="tab==='doctors'">
      
      <div class="mb-4">
        <label class="fw-bold mb-2">Filter by Department:</label>
        <div class="d-flex flex-wrap gap-2">
          <button class="btn btn-sm" :class="!filterDept ? 'btn-primary':'btn-outline-primary'" @click="filterDept=null">All</button>
          <button v-for="d in departments" :key="d.id" class="btn btn-sm" :class="filterDept===d.id ? 'btn-primary':'btn-outline-primary'" @click="filterDept=d.id">{{ d.name }}</button>
        </div>
      </div>

      <div class="card overflow-hidden" style="border: 2px solid #ffeb3b !important;">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th class="ps-4">Doctor Name</th>
                <th>Specialization</th>
                <th class="text-end pe-4">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="d in filteredDoctors" :key="d.id">
                <td class="ps-4 fw-bold">Dr. {{ d.name }}</td>
                <td><span class="badge bg-light text-dark border">{{ d.specialization }}</span></td>
                <td class="text-end pe-4">
                  <button class="btn btn-sm text-white" style="background-color: #e91e63 !important; border: none !important;" @click="openBooking(d)">Book Visit</button>
                </td>
              </tr>
              <tr v-if="filteredDoctors.length===0">
                <td colspan="3" class="text-center py-4 text-muted">No doctors found for this department.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- HISTORY TAB -->
    <div v-if="tab==='history'">

      <div class="card p-0 overflow-hidden shadow-sm border-0">

        <div class="table-responsive">

          <table class="table table-hover align-middle mb-0">

            <thead class="table-light">
              <tr>
                <th class="ps-4">Date</th>
                <th>Doctor</th>
                <th>Diagnosis</th>
                <th>Prescription</th>
              </tr>
            </thead>

            <tbody>

              <tr v-if="history.length===0">
                <td colspan="4" class="text-center py-4 text-muted">
                  No history found.
                </td>
              </tr>

              <tr v-for="h in history" :key="h.id">

                <td class="ps-4 fw-bold text-primary">
                  {{ h.date }}
                </td>

                <td>
                  Dr. {{ h.doctor_name }}
                </td>

                <td>
                  {{ h.diagnosis }}
                </td>

                <td>
                  <span class="badge bg-light border text-dark">
                    {{ h.prescription || 'None' }}
                  </span>
                </td>

              </tr>

            </tbody>

          </table>

        </div>
      </div>

      <button
        v-if="history.length > 0"
        class="btn btn-link btn-sm p-0 mt-3 text-primary text-decoration-none fw-bold"
        @click="exportRecords">

        Download Medical Record

      </button>

    </div>

    <!-- BOOKING MODAL -->
    <div v-if="showBooking" class="modal-backdrop"></div>
    <div v-if="showBooking" class="modal show d-block" style="z-index:1055">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">Book Visit</h5>
            <button class="btn-close" @click="showBooking=false"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-12">
                <label class="form-label small fw-bold">Date</label>
                <input type="date" class="form-control" v-model="booking.date" :min="minDate" :max="maxDate" @change="fetchSlots">
                <small v-if="dateError" class="text-danger">{{ dateError }}</small>
              </div>
              <div class="col-12" v-if="slots.length > 0">
                <label class="form-label small fw-bold">Available Slots</label>
                <div class="d-flex flex-wrap gap-2 mt-2">
                  <button v-for="s in slots" :key="s" class="btn btn-sm rounded-pill" 
                          :class="booking.time===s ? 'btn-primary':'btn-outline-primary'" 
                          @click="booking.time=s">{{ s }}</button>
                </div>
              </div>
              <div class="col-12 text-center text-muted py-3" v-else-if="booking.date && !dateError">
                No slots available for this date.
              </div>
            </div>
          </div>
          <div class="modal-footer border-0">
            <button class="btn btn-secondary" @click="showBooking=false">Cancel</button>
            <button class="btn btn-primary" :disabled="!booking.time" @click="submitBooking">Confirm Booking</button>
          </div>
        </div>
      </div>
    </div>

    <!-- PROFILE MODAL -->
    <div v-if="showProfile" class="modal-backdrop"></div>
    <div v-if="showProfile" class="modal show d-block" style="z-index:1055">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">My Profile</h5>
            <button class="btn-close" @click="showProfile=false"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-12"><label class="form-label small fw-bold">Full Name</label><input class="form-control" v-model="profile.name"></div>
              <div class="col-12"><label class="form-label small fw-bold">Age</label><input type="number" class="form-control" v-model="profile.age"></div>
              <div class="col-12"><label class="form-label small fw-bold">Gender</label>
                <select class="form-select" v-model="profile.gender">
                  <option>Male</option><option>Female</option><option>Other</option>
                </select>
              </div>
              <div class="col-12"><label class="form-label small fw-bold">Phone No</label><input class="form-control" v-model="profile.contact"></div>
              <div class="col-12"><label class="form-label small fw-bold">Email</label><input type="email" class="form-control" v-model="profile.email" readonly></div>
            </div>
          </div>
          <div class="modal-footer border-0">
            <button class="btn btn-secondary" @click="showProfile=false">Close</button>
            <button class="btn btn-primary" @click="saveProfile">Save Changes</button>
          </div>
        </div>
      </div>
    </div>

  </div>
  `,

  data() {
    return {
      tab: 'home',
      upcoming: [],
      history: [],
      doctors: [],
      departments: [],
      filterDept: null,
      showBooking: false,
      showProfile: false,
      booking: { doctor_id: '', date: '', time: '' },
      slots: [],
      profile: {},
      dateError: null
    };
  },

  computed: {

    minDate() {
      return new Date().toISOString().split('T')[0];
    },

    maxDate() {
      const d = new Date();
      d.setMonth(d.getMonth() + 3);
      return d.toISOString().split('T')[0];
    },

    filteredDoctors() {
      if (!this.filterDept) return this.doctors;
      return this.doctors.filter(
        d => d.specialization_id === this.filterDept
      );
    }

  },

  mounted() {
    this.load();
    this.loadProfile();
  },

  methods: {

    async api(url, method = 'GET', body = null) {

      const r = await fetch('/api' + url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + this.token
        },
        body: body ? JSON.stringify(body) : null
      });

      if (r.status === 401) {
        localStorage.clear();
        location.href = '/login';
        return null;
      }

      return r.json();
    },

    async load() {

      const dash = await this.api('/patient/dashboard');
      if (dash) this.upcoming = dash.upcoming_appointments || [];

      const hist = await this.api('/patient/treatments');
      this.history = Array.isArray(hist) ? hist : [];

      const docs = await this.api('/patient/doctors');
      this.doctors = Array.isArray(docs) ? docs : [];

      const depts = await this.api('/patient/departments');
      this.departments = Array.isArray(depts) ? depts : [];

    },

    async loadProfile() {
      const p = await this.api('/patient/profile');
      if (p && !p.error) this.profile = p;
    },

    async saveProfile() {
      await this.api('/patient/profile', 'PUT', this.profile);
      this.showProfile = false;
      alert('Profile saved!');
    },

    goBookDoctor() {
      this.tab = 'doctors';
      this.filterDept = null;
    },

    openBooking(doc) {
      this.booking = {
        doctor_id: doc.id,
        date: this.minDate,
        time: ''
      };
      this.slots = [];
      this.dateError = null;
      this.showBooking = true;
      this.fetchSlots();
    },

    async fetchSlots() {

      this.booking.time = '';
      this.slots = [];
      this.dateError = null;

      if (!this.booking.doctor_id || !this.booking.date) return;

      if (this.booking.date < this.minDate) {
        this.dateError = 'Cannot book on a past date.';
        return;
      }

      const res = await this.api(
        '/patient/doctors/' + this.booking.doctor_id + '/availability'
      );

      if (!res) return;

      const day = (res.availability || [])
        .find(a => a.date === this.booking.date);

      if (!day) return;

      let cur = new Date('1970-01-01T' + day.start_time);
      const end = new Date('1970-01-01T' + day.end_time);

      const booked = res.booked_slots || [];

      while (cur < end) {

        const t = cur.toTimeString().slice(0, 5);

        if (!booked.some(
          b => b.date === this.booking.date && b.time === t
        )) {
          this.slots.push(t);
        }

        cur.setMinutes(cur.getMinutes() + 30);

      }

    },

    async submitBooking() {

      if (this.booking.date < this.minDate) {
        this.dateError = 'Cannot book on a past date.';
        return;
      }

      if (!this.booking.time) {
        alert('Please select a time slot.');
        return;
      }

      const res = await this.api(
        '/patient/appointments',
        'POST',
        this.booking
      );

      if (!res) return;

      if (res.error) {
        alert(res.error);
        return;
      }

      this.showBooking = false;
      this.dateError = null;

      alert('Appointment booked!');

      this.load();
    },

    async cancelAppt(id) {

      if (!confirm('Cancel this appointment?')) return;

      await this.api('/patient/appointments/' + id, 'DELETE');

      this.load();

    },

    async exportRecords() {

      const res = await this.api('/patient/export', 'POST');

      if (res && res.status === 'completed') {

        window.location.href =
          '/api/patient/export/' + res.file +
          '/download_direct?token=' + this.token;

      }

    }

  }

};
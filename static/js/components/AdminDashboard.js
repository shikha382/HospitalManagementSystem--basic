const AdminDashboard = {
  props: ['token'],
  template: `
  <div class="container py-4">

    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="fw-bold" style="color:var(--primary)">🦉 Admin Dashboard</h3>
      <button v-if="tab==='doctors'" class="btn btn-primary btn-custom" @click="showAdd=true">+ Add Doctor</button>
    </div>

    <!-- STATS -->
    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <div class="card text-center p-3" style="border: 2px solid #f973a0 !important;">
          <div class="fs-2">🩺</div>
          <small class="text-muted fw-bold text-uppercase">Doctors</small>
          <h3 class="fw-bold" style="color:var(--primary)">{{ stats.total_doctors || 0 }}</h3>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card text-center p-3" style="border: 2px solid #facc15 !important;">
          <div class="fs-2">🤒</div>
          <small class="text-muted fw-bold text-uppercase">Patients</small>
          <h3 class="fw-bold" style="color:var(--secondary)">{{ stats.total_patients || 0 }}</h3>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card text-center p-3" style="border: 2px solid #22c55e !important;">
          <div class="fs-2">🗓️</div>
          <small class="text-muted fw-bold text-uppercase">Visits</small>
          <h3 class="fw-bold" style="color:#6ed3cf">{{ stats.total_appointments || 0 }}</h3>
        </div>
      </div>
    </div>

    <!-- TABS -->
    <ul class="nav nav-pills mb-4">
      <li class="nav-item"><button class="nav-link" :class="{active:tab==='doctors'}" @click="tab='doctors'">Doctors</button></li>
      <li class="nav-item"><button class="nav-link" :class="{active:tab==='patients'}" @click="tab='patients'">Patients</button></li>
      <li class="nav-item"><button class="nav-link" :class="{active:tab==='appointments'}" @click="tab='appointments'">Schedule</button></li>
    </ul>

    <!-- SEARCH -->
    <div class="mb-3" v-if="tab!=='appointments'">
      <input class="form-control" style="max-width:400px" v-model="search" @input="doSearch" placeholder="Search...">
    </div>

    <!-- DOCTORS TABLE -->
    <div v-if="tab==='doctors'" class="card p-0 overflow-hidden">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light"><tr><th class="ps-4">Name</th><th>Dept</th><th>Status</th><th class="text-end pe-4">Actions</th></tr></thead>
          <tbody>
            <tr v-if="doctors.length===0"><td colspan="4" class="text-center py-4 text-muted">No doctors found.</td></tr>
            <tr v-for="d in doctors" :key="d.id">
              <td class="ps-4 fw-bold">{{ d.name }}</td>
              <td><span class="badge bg-light border text-dark">{{ d.specialization }}</span></td>
              <td><span class="badge" :class="d.active ? 'bg-success':'bg-danger'">{{ d.active ? 'Active' : 'Inactive' }}</span></td>
              <td class="text-end pe-4">
                <button class="btn btn-sm btn-outline-primary me-1" title="View" @click="viewItem(d)">👁️</button>
                <button class="btn btn-sm btn-outline-primary me-1" title="Edit" @click="editItem(d)">✏️</button>
                <button class="btn btn-sm" title="Toggle Status"
                  :class="d.active ? 'btn-outline-danger':'btn-outline-success'"
                  @click="toggleDoctor(d.id)">{{ d.active ? '🚫' : '✅' }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- PATIENTS TABLE -->
    <div v-if="tab==='patients'" class="card p-0 overflow-hidden">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light"><tr><th class="ps-4">Name</th><th>Phone</th><th>Status</th><th class="text-end pe-4">Actions</th></tr></thead>
          <tbody>
            <tr v-if="patients.length===0"><td colspan="4" class="text-center py-4 text-muted">No patients found.</td></tr>
            <tr v-for="p in patients" :key="p.id">
              <td class="ps-4 fw-bold">{{ p.name }}</td>
              <td>{{ p.contact || '---' }}</td>
              <td><span class="badge" :class="p.active ? 'bg-info':'bg-warning text-dark'">{{ p.active ? 'Active':'Blocked' }}</span></td>
              <td class="text-end pe-4">
                <button class="btn btn-sm btn-outline-primary me-1" title="View" @click="viewItem(p)">👁️</button>
                <button class="btn btn-sm" title="Toggle Status"
                  :class="p.active ? 'btn-outline-danger':'btn-outline-success'"
                  @click="togglePatient(p.id)">{{ p.active ? '🚫' : '✅' }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- APPOINTMENTS TABLE -->
    <div v-if="tab==='appointments'" class="card p-0 overflow-hidden">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light"><tr><th class="ps-4">Patient</th><th>Doctor</th><th>Date</th><th>Time</th><th>Status</th></tr></thead>
          <tbody>
            <tr v-if="appointments.length===0"><td colspan="5" class="text-center py-4 text-muted">No appointments found.</td></tr>
            <tr v-for="a in appointments" :key="a.id">
              <td class="ps-4 fw-bold">{{ a.patient_name }}</td>
              <td>Dr. {{ a.doctor_name }}</td>
              <td>{{ a.date }}</td>
              <td>{{ a.time }}</td>
              <td><span class="badge bg-light border text-dark">{{ a.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ADD DOCTOR MODAL -->
    <div v-if="showAdd" class="modal-backdrop"></div>
    <div v-if="showAdd" class="modal show d-block" style="z-index:1055">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header"><h5 class="modal-title fw-bold">Add Doctor</h5><button class="btn-close" @click="showAdd=false"></button></div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-12"><label class="form-label small fw-bold">Name</label><input class="form-control" v-model="newDoc.name" placeholder="Full Name"></div>
              <div class="col-12"><label class="form-label small fw-bold">Username</label><input class="form-control" v-model="newDoc.username"></div>
              <div class="col-12"><label class="form-label small fw-bold">Password</label><input type="password" class="form-control" v-model="newDoc.password"></div>
              <div class="col-12"><label class="form-label small fw-bold">Email</label><input type="email" class="form-control" v-model="newDoc.email"></div>
              <div class="col-12"><label class="form-label small fw-bold">Department</label>
                <select class="form-select" v-model="newDoc.specialization_id">
                  <option disabled value="">Select...</option>
                  <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
                </select>
              </div>
              <div class="col-12"><label class="form-label small fw-bold">Experience (yrs)</label><input type="number" class="form-control" v-model="newDoc.experience"></div>
              <div class="col-12"><label class="form-label small fw-bold">Phone</label><input class="form-control" v-model="newDoc.contact"></div>
            </div>
          </div>
          <div class="modal-footer border-0">
            <button class="btn btn-secondary" @click="showAdd=false">Cancel</button>
            <button class="btn btn-primary" @click="addDoctor">Save</button>
          </div>
        </div>
      </div>
    </div>

    <!-- EDIT DOCTOR MODAL -->
    <div v-if="editing" class="modal-backdrop"></div>
    <div v-if="editing" class="modal show d-block" style="z-index:1055">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header"><h5 class="modal-title fw-bold">Edit Doctor</h5><button class="btn-close" @click="editing=null"></button></div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-12"><label class="form-label small fw-bold">Name</label><input class="form-control" v-model="editing.name"></div>
              <div class="col-12"><label class="form-label small fw-bold">Department</label>
                <select class="form-select" v-model="editing.specialization_id">
                  <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
                </select>
              </div>
              <div class="col-12"><label class="form-label small fw-bold">Experience</label><input type="number" class="form-control" v-model="editing.experience"></div>
              <div class="col-12"><label class="form-label small fw-bold">Phone</label><input class="form-control" v-model="editing.contact"></div>
            </div>
          </div>
          <div class="modal-footer border-0">
            <button class="btn btn-secondary" @click="editing=null">Cancel</button>
            <button class="btn btn-primary" @click="saveEdit">Update</button>
          </div>
        </div>
      </div>
    </div>

    <!-- VIEW MODAL -->
    <div v-if="viewing" class="modal-backdrop"></div>
    <div v-if="viewing" class="modal show d-block" style="z-index:1055">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">
              {{ viewing.specialization !== undefined ? '🩺 Doctor Details' : '🤒 Patient Details' }}
            </h5>
            <button class="btn-close" @click="viewing=null"></button>
          </div>
          <div class="modal-body px-4 pb-4">
            <table class="table table-bordered table-sm mb-0">
              <tbody>
                <tr><td class="fw-bold text-muted" style="width:40%">ID</td><td>{{ viewing.id }}</td></tr>
                <tr><td class="fw-bold text-muted">Name</td><td>{{ viewing.name }}</td></tr>
                <tr v-if="viewing.specialization !== undefined">
                  <td class="fw-bold text-muted">Department</td><td>{{ viewing.specialization }}</td>
                </tr>
                <tr v-if="viewing.experience !== undefined">
                  <td class="fw-bold text-muted">Experience</td><td>{{ viewing.experience }} yrs</td>
                </tr>
                <tr v-if="viewing.contact !== undefined">
                  <td class="fw-bold text-muted">Phone</td><td>{{ viewing.contact || '---' }}</td>
                </tr>
                <tr v-if="viewing.age !== undefined">
                  <td class="fw-bold text-muted">Age</td><td>{{ viewing.age || '---' }}</td>
                </tr>
                <tr v-if="viewing.gender !== undefined">
                  <td class="fw-bold text-muted">Gender</td><td>{{ viewing.gender || '---' }}</td>
                </tr>

                <tr>
                  <td class="fw-bold text-muted">Status</td>
                  <td><span class="badge" :class="viewing.active ? 'bg-success':'bg-danger'">{{ viewing.active ? 'Active' : 'Inactive' }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

  </div>
  `,
  data() {
    return {
      tab: 'doctors',
      stats: {},
      doctors: [],
      patients: [],
      appointments: [],
      departments: [],
      search: '',
      showAdd: false,
      editing: null,
      viewing: null,
      showEmailPanel: false,
      emailBusy: false,
      emailStatus: null,
      newDoc: { name: '', username: '', password: '', email: '', specialization_id: '', experience: '', contact: '' }
    };
  },
  mounted() { this.load(); },
  methods: {
    async api(url, method = 'GET', body = null) {
      const r = await fetch('/api' + url, {
        method,
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + this.token },
        body: body ? JSON.stringify(body) : null
      });
      if (r.status === 401) { localStorage.clear(); location.href = '/login'; return null; }
      return r.json();
    },
    async load() {
      const s = await this.api('/admin/dashboard');
      if (s) this.stats = s;
      const docs = await this.api('/admin/doctors');
      this.doctors = Array.isArray(docs) ? docs : [];
      const pts = await this.api('/admin/patients');
      this.patients = Array.isArray(pts) ? pts : [];
      const appts = await this.api('/admin/appointments');
      this.appointments = Array.isArray(appts) ? appts : [];
      const depts = await this.api('/admin/departments');
      this.departments = Array.isArray(depts) ? depts : [];
    },
    async doSearch() {
      if (!this.search) { this.load(); return; }
      if (this.tab === 'doctors') {
        const r = await this.api('/admin/search/doctors?q=' + this.search);
        this.doctors = Array.isArray(r) ? r : [];
      } else if (this.tab === 'patients') {
        const r = await this.api('/admin/search/patients?q=' + this.search);
        this.patients = Array.isArray(r) ? r : [];
      }
    },
    editItem(item) { this.editing = { ...item }; },
    async saveEdit() {
      await this.api('/admin/doctors/' + this.editing.id, 'PUT', this.editing);
      this.editing = null;
      this.load();
      alert('Updated!');
    },
    async addDoctor() {
      const r = await this.api('/admin/doctors', 'POST', this.newDoc);
      if (!r) return;
      if (r.error) { alert(r.error); return; }
      this.showAdd = false;
      this.newDoc = { name: '', username: '', password: '', email: '', specialization_id: '', experience: '', contact: '' };
      this.load();
      alert('Doctor added!');
    },
    async toggleDoctor(id) {
      await this.api('/admin/doctors/' + id + '/toggle', 'PUT');
      this.load();
    },
    async togglePatient(id) {
      await this.api('/admin/patients/' + id + '/toggle', 'PUT');
      this.load();
    },
    viewItem(item) { this.viewing = item; },
    async sendReminders() {
      this.emailBusy = true;
      this.emailStatus = null;
      const r = await this.api('/admin/reminders/trigger', 'POST');
      this.emailBusy = false;
      if (r && r.message) this.emailStatus = { ok: true, msg: r.message };
      else this.emailStatus = { ok: false, msg: (r && r.error) || 'Failed to send reminders.' };
    },
    async sendReports() {
      this.emailBusy = true;
      this.emailStatus = null;
      const r = await this.api('/admin/reports/monthly', 'POST');
      this.emailBusy = false;
      if (r && r.message) this.emailStatus = { ok: true, msg: r.message };
      else this.emailStatus = { ok: false, msg: (r && r.error) || 'Failed to send reports.' };
    }
  }
};
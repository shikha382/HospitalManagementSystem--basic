const DoctorDashboard = {
  props: ['token'],
  template: `
  <div class="container py-4">

    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="fw-bold" style="color:var(--primary)">🩺 Doctor Dashboard</h3>
      <div class="d-flex gap-2">
        <button class="btn btn-secondary btn-custom" @click="showAvail=true">⏰ Timings</button>
      </div>
    </div>

    <!-- STATS -->
    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <div class="card text-center p-3" style="border: 2px solid #ffeb3b !important;">
          <div class="fs-2">📋</div>
          <small class="text-muted fw-bold">Total Patients</small>
          <h3 class="fw-bold" style="color:var(--primary)">{{ stats.total_patients || 0 }}</h3>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card text-center p-3" style="border: 2px solid #ffeb3b !important;">
          <div class="fs-2">✅</div>
          <small class="text-muted fw-bold">Completed Today</small>
          <h3 class="fw-bold" style="color:var(--secondary)">{{ stats.completed_today || 0 }}</h3>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card text-center p-3" style="border: 2px solid #ffeb3b !important;">
          <div class="fs-2">📅</div>
          <small class="text-muted fw-bold">Upcoming This Week</small>
          <h3 class="fw-bold" style="color:#6ed3cf">{{ stats.upcoming_appointments ? stats.upcoming_appointments.length : 0 }}</h3>
        </div>
      </div>
    </div>

    <!-- TABS -->
    <ul class="nav nav-pills mb-4">
      <li class="nav-item"><button class="nav-link" :class="{active:tab==='appointments'}" @click="tab='appointments'">Appointments</button></li>
      <li class="nav-item"><button class="nav-link" :class="{active:tab==='patients'}" @click="tab='patients'">My Patients</button></li>
      <li class="nav-item"><button class="nav-link" :class="{active:tab==='timings'}" @click="tab='timings'">My Timings</button></li>
    </ul>

    <!-- APPOINTMENTS TAB -->
    <div v-if="tab==='appointments'" class="card p-0 overflow-hidden" style="border: 2px solid #ffeb3b !important;">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light"><tr><th class="ps-4">Date</th><th>Time</th><th>Patient</th><th>Status</th><th class="text-end pe-4">Action</th></tr></thead>
          <tbody>
            <tr v-if="appointments.length===0"><td colspan="5" class="text-center py-4 text-muted">No appointments.</td></tr>
            <tr v-for="a in appointments" :key="a.id">
              <td class="ps-4 fw-bold">{{ a.date }}</td>
              <td class="text-primary fw-bold">{{ a.time }}</td>
              <td>{{ a.patient_name }}</td>
              <td>
                <span class="badge" :class="statusClass(a.status)">{{ a.status }}</span>
              </td>
              <td class="text-end pe-4">
                <button v-if="a.status==='booked'" class="btn btn-sm btn-primary" @click="startConsult(a)">Consult</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- PATIENTS TAB -->
    <div v-if="tab==='patients'" class="card p-0 overflow-hidden" style="border: 2px solid #ffeb3b !important;">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light"><tr><th class="ps-4">Patient</th><th class="pe-4">History</th></tr></thead>
          <tbody>
            <tr v-if="myPatients.length===0"><td colspan="2" class="text-center py-4 text-muted">No patients yet.</td></tr>
            <tr v-for="p in myPatients" :key="p.id">
              <td class="ps-4 fw-bold">{{ p.name }}</td>
              <td class="pe-4">
                <button class="btn btn-sm btn-outline-primary" @click="viewHistory(p.id, p.name)">View History</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- TIMINGS TAB -->
    <div v-if="tab==='timings'" class="card p-0 overflow-hidden" style="border: 2px solid #ffeb3b !important;">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light"><tr><th class="ps-4">Date</th><th>Status</th><th>Hours</th></tr></thead>
          <tbody>
            <tr v-if="availability.length===0"><td colspan="3" class="text-center py-4 text-muted">No timings set.</td></tr>
            <tr v-for="v in availability" :key="v.date">
              <td class="ps-4 fw-bold">{{ v.date }}</td>
              <td>
                <span class="badge" :class="v.is_available ? 'bg-success':'bg-danger'">
                  {{ v.is_available ? 'Open' : 'Closed' }}
                </span>
              </td>
              <td>{{ v.is_available ? (v.start_time + ' - ' + v.end_time) : '---' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- CONSULT MODAL -->
    <div v-if="consulting" class="modal-backdrop"></div>
    <div v-if="consulting" class="modal show d-block" style="z-index:1055">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header"><h5 class="modal-title fw-bold">Add Treatment - {{ consulting.patient_name }}</h5><button class="btn-close" @click="consulting=null"></button></div>
          <div class="modal-body">
            <div class="mb-3"><label class="form-label fw-bold small">Diagnosis</label><textarea class="form-control" v-model="treatment.diagnosis" rows="2"></textarea></div>
            <div class="mb-3"><label class="form-label fw-bold small">Prescription</label><textarea class="form-control" v-model="treatment.prescription" rows="2"></textarea></div>
            <div class="mb-3"><label class="form-label fw-bold small">Notes</label><textarea class="form-control" v-model="treatment.notes" rows="2"></textarea></div>
          </div>
          <div class="modal-footer border-0">
            <button class="btn btn-secondary" @click="consulting=null">Cancel</button>
            <button class="btn btn-primary" :disabled="!treatment.diagnosis" @click="submitTreatment">Complete</button>
          </div>
        </div>
      </div>
    </div>

    <!-- PATIENT HISTORY MODAL -->
    <div v-if="historyModal" class="modal-backdrop"></div>
    <div v-if="historyModal" class="modal show d-block" style="z-index:1055">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content border-0 shadow">
          <div class="modal-header"><h5 class="modal-title fw-bold">History - {{ historyModal.name }}</h5><button class="btn-close" @click="historyModal=null"></button></div>
          <div class="modal-body p-0">
            <div class="table-responsive">
              <table class="table align-middle mb-0">
                <thead class="table-light"><tr><th class="ps-4">Date</th><th>Diagnosis</th><th>Prescription</th></tr></thead>
                <tbody>
                  <tr v-if="!historyModal.records.length"><td colspan="3" class="text-center py-4 text-muted">No records.</td></tr>
                  <tr v-for="r in historyModal.records" :key="r.id">
                    <td class="ps-4">{{ r.date }}</td>
                    <td>{{ r.treatment ? r.treatment.diagnosis : 'N/A' }}</td>
                    <td>{{ r.treatment ? r.treatment.prescription : 'N/A' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="modal-footer border-0"><button class="btn btn-secondary" @click="historyModal=null">Close</button></div>
        </div>
      </div>
    </div>

    <!-- AVAILABILITY MODAL -->
    <div v-if="showAvail" class="modal-backdrop"></div>
    <div v-if="showAvail" class="modal show d-block" style="z-index:1055">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header"><h5 class="modal-title fw-bold">Set Timings (Next 7 Days)</h5><button class="btn-close" @click="showAvail=false"></button></div>
          <div class="modal-body" style="max-height:60vh;overflow-y:auto">
            <div v-for="(day, i) in availForm" :key="i" class="border rounded-3 p-3 mb-3">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <strong>{{ day.date }}</strong>
                <div class="form-check form-switch">
                  <input class="form-check-input" type="checkbox" v-model="day.is_available">
                  <label class="form-check-label">Available</label>
                </div>
              </div>
              <div class="row g-2" v-if="day.is_available">
                <div class="col-6"><label class="form-label small">Start</label><input type="time" class="form-control" v-model="day.start_time"></div>
                <div class="col-6"><label class="form-label small">End</label><input type="time" class="form-control" v-model="day.end_time"></div>
              </div>
            </div>
          </div>
          <div class="modal-footer border-0">
            <button class="btn btn-secondary" @click="showAvail=false">Cancel</button>
            <button class="btn btn-primary" @click="saveAvail">Save</button>
          </div>
        </div>
      </div>
    </div>

  </div>
  `,
  data() {
    return {
      tab: 'appointments',
      stats: {},
      appointments: [],
      myPatients: [],
      availability: [],
      showAvail: false,
      availForm: [],
      consulting: null,
      treatment: { diagnosis: '', prescription: '', notes: '' },
      historyModal: null
    };
  },
  mounted() { this.load(); this.buildAvailForm(); },
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
      const dash = await this.api('/doctor/dashboard');
      if (dash && !dash.error) this.stats = dash;

      const appts = await this.api('/doctor/appointments');
      this.appointments = Array.isArray(appts) ? appts : [];

      const avail = await this.api('/doctor/availability');
      this.availability = Array.isArray(avail) ? avail : [];

      const uniqueMap = {};
      this.appointments.forEach(a => {
        if (a.patient_id && !uniqueMap[a.patient_id]) {
          uniqueMap[a.patient_id] = { id: a.patient_id, name: a.patient_name };
        }
      });
      this.myPatients = Object.values(uniqueMap);
    },
    statusClass(s) {
      if (s === 'booked') return 'bg-warning text-dark';
      if (s === 'completed') return 'bg-success';
      if (s === 'cancelled') return 'bg-danger';
      return 'bg-secondary';
    },
    startConsult(appt) {
      this.consulting = appt;
      this.treatment = { diagnosis: '', prescription: '', notes: '' };
    },
    async submitTreatment() {
      const res = await this.api('/doctor/treatment', 'POST', {
        appointment_id: this.consulting.id,
        diagnosis: this.treatment.diagnosis,
        prescription: this.treatment.prescription,
        notes: this.treatment.notes
      });
      if (!res) return;
      if (res.error) { alert(res.error); return; }
      this.consulting = null;
      this.load();
      alert('Treatment saved!');
    },
    async viewHistory(pid, pname) {
      const records = await this.api('/doctor/patients/' + pid + '/history');
      this.historyModal = { name: pname, records: Array.isArray(records) ? records : [] };
    },
    async downloadReport() {
      const r = await fetch('/api/doctor/report/monthly', {
        headers: { 'Authorization': 'Bearer ' + this.token }
      });
      if (r.ok) {
        const blob = await r.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = 'Monthly_Report.html'; a.click();
      } else alert('Report error');
    },
    buildAvailForm() {
      this.availForm = [];
      for (let i = 0; i < 7; i++) {
        const d = new Date();
        d.setDate(d.getDate() + i);
        this.availForm.push({
          date: d.toISOString().split('T')[0],
          is_available: true,
          start_time: '09:00',
          end_time: '17:00'
        });
      }
    },
    async saveAvail() {
      await this.api('/doctor/availability', 'POST', { availability: this.availForm });
      this.showAvail = false;
      this.load();
      alert('Timings saved!');
    }
  }
};

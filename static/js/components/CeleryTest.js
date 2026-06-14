const CeleryTest = {
  template: `
    <div style="background:white; padding: 20px; border: 1px solid #ccc; margin: 20px;">
      <h4>Simple Celery Add</h4>
      <input v-model.number="x" type="number"> + 
      <input v-model.number="y" type="number">
      <button @click="runTask">Add</button>
      <hr>
      <button @click="exportCSV">Export Appointments to CSV</button>
      <div v-if="status">Status: {{ status }}</div>
      <div v-if="result">Result: {{ result }}</div>
      <div v-if="csvLink">
        <a :href="'/api/test/download/' + csvLink" target="_blank">Download CSV</a>
      </div>
    </div>
  `,
  data() {
    return { x: 0, y: 0, result: null, status: '', csvLink: null };
  },
  methods: {
    async exportCSV() {
      const resp = await fetch('/api/test/export_appointments');
      const data = await resp.json();
      this.status = 'Exporting...';
      this.csvLink = null;
      
      const check = setInterval(async () => {
        const r = await fetch(`/api/test/status/${data.task_id}`);
        const d = await r.json();
        this.status = 'Export: ' + d.status;
        if (d.status === 'SUCCESS') {
          this.csvLink = d.result;
          this.status = 'Ready!';
          clearInterval(check);
        }
      }, 1000);
    },
    async runTask() {
      // 1. Submit task
      const resp = await fetch(`/api/test/add?x=${this.x}&y=${this.y}`);
      const data = await resp.json();
      
      
      
      const check = setInterval(async () => {
        const r = await fetch(`/api/test/status/${data.task_id}`);
        const d = await r.json();
        this.status = d.status;
        if (d.status === 'SUCCESS') {
          this.result = d.result;
          clearInterval(check);
        }
      }, 1000);
    }
  }
};

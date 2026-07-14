<template>
  <div class="user-page">
    <div class="page-header">
      <h2 class="page-title">My Applications</h2>
      <div style="display:flex; gap:.75rem;">
        <button class="btn-add" style="background:#3498db;" @click="triggerExport"
          :disabled="exporting">
          {{ exporting ? 'Preparing…' : '⬇ Export CSV' }}
        </button>
      </div>
    </div>

    <!-- Export status -->
    <div v-if="exportMsg" class="alert-strip" :class="exportMsgType" style="margin-bottom:1rem;">
      {{ exportMsg }}
      <button v-if="exportReady" class="action-btn action-approve"
        style="margin-left:1rem;" @click="downloadExport">
        ⬇ Download Now
      </button>
    </div>

    <!-- Summary bar -->
    <div style="display:flex; gap:1rem; flex-wrap:wrap; margin-bottom:1.5rem;">
      <div v-for="s in summary" :key="s.label"
        style="background:#fff; border-radius:8px; padding:.65rem 1.2rem; box-shadow:0 1px 4px rgba(0,0,0,.08); display:flex; align-items:center; gap:.6rem;">
        <span style="font-size:1.5rem; font-weight:700;" :style="{ color: s.color }">{{ s.val }}</span>
        <span style="font-size:.82rem; color:#7f8c8d;">{{ s.label }}</span>
      </div>
    </div>

    <!-- Filter -->
    <div class="toolbar" style="margin-bottom:1rem;">
      <div class="toolbar-fields">
        <select v-model="filterStatus" class="toolbar-select" style="width:auto; min-width:150px;">
          <option value="">All Status</option>
          <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
    </div>

    <p v-if="loading" class="loading-text">Loading applications…</p>

    <div v-else-if="filtered.length === 0"
      style="text-align:center; padding:3rem; color:#7f8c8d;">
      No applications found.
      <br><br>
      <router-link to="/student_dashboard/drives" class="action-btn action-apply">Browse Drives</router-link>
    </div>

    <!-- Application cards grid -->
    <div v-else style="display:grid; grid-template-columns:repeat(auto-fill, minmax(300px,1fr)); gap:1.2rem;">
      <div v-for="a in filtered" :key="a.id"
        style="background:#fff; border-radius:10px; overflow:hidden; border:1px solid #e0e0e0; box-shadow:0 2px 6px rgba(0,0,0,.06);"
        :style="{ borderLeftWidth: '4px', borderLeftColor: statusColor(a.status) }">

        <!-- Header -->
        <div style="padding:1rem 1.2rem; border-bottom:1px solid #f0f0f0;">
          <div style="font-size:.95rem; font-weight:700; color:#2c3e50;">{{ a.drive_name }}</div>
          <div style="font-size:.82rem; color:#7f8c8d; margin-top:.2rem;">{{ a.company_name }}</div>
        </div>

        <!-- Body -->
        <div style="padding:1rem 1.2rem;">
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:.4rem .75rem; margin-bottom:.75rem;">
            <div style="font-size:.8rem; color:#7f8c8d;">
               {{ a.job_title }}
            </div>
            <div style="font-size:.8rem; color:#7f8c8d;">
              {{ fmtDate(a.application_date) }}
            </div>
            <div v-if="a.interview_type" style="font-size:.8rem; color:#7f8c8d;">
              {{ a.interview_type }}
            </div>
            <div v-if="a.remarks" style="font-size:.8rem; color:#7f8c8d; grid-column:1/-1; font-style:italic;">
              {{ a.remarks }}
            </div>
          </div>

          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span :class="['status', a.status]">{{ a.status }}</span>
            <button class="action-btn action-reject"
              v-if="a.status === 'applied'"
              @click="withdraw(a.id)">
              Withdraw
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import api from '@/utils/api'

const store = useStore()
const applications = ref([])
const loading = ref(true)
const filterStatus = ref('')
const statuses = ['applied', 'shortlisted', 'selected', 'rejected']

const exporting = ref(false)
const exportMsg = ref('')
const exportMsgType = ref('info')
const exportReady  = ref(false)
const exportTaskId = ref('')
let   pollInterval = null

const filtered = computed(() => {
  if (!filterStatus.value) return applications.value
  return applications.value.filter(a => a.status === filterStatus.value)
})

const summary = computed(() => [
  { label: 'Total', val: applications.value.length, color: '#3498db' },
  { label: 'Shortlisted', val: applications.value.filter(a => a.status === 'shortlisted').length, color: '#e67e22' },
  { label: 'Selected', val: applications.value.filter(a => a.status === 'selected').length, color: '#27ae60' },
  { label: 'Rejected', val: applications.value.filter(a => a.status === 'rejected').length, color: '#e74c3c' },
])

const fmtDate = d => d
  ? new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
  : '—'

const statusColor = s => ({
  applied: '#3498db',
  shortlisted: '#e67e22',
  selected: '#27ae60',
  rejected: '#e74c3c',
}[s] || '#bdc3c7')

async function fetchApplications() {
  loading.value = true
  try {
    const r = await api.get('/applications')
    applications.value = r.data || []
  } catch { applications.value = [] }
  finally { loading.value = false }
}

async function withdraw(id) {
  if (!confirm('Withdraw this application?')) return
  try {
    await api.delete(`/applications/${id}`)
    fetchApplications()
  } catch (e) { alert(e.message) }
}

/* ── CSV Export (async batch job) ─────────────── */
async function triggerExport() {
  exporting.value   = true
  exportMsg.value   = 'Export job queued…'
  exportMsgType.value = 'info'
  exportReady.value = false
  exportTaskId.value = ''
  if (pollInterval) clearInterval(pollInterval)

  try {
    const uid = store.state.userId
    const r = await api.post(`/students/${uid}/export-csv`)
    exportTaskId.value = r.task_id
    exportMsg.value  = ' Export in progress… please wait.'

    // Poll every 2 s
    pollInterval = setInterval(() => pollExport(uid, r.task_id), 2000)
  } catch (e) {
    exportMsg.value = ' ' + (e.message || 'Export failed.')
    exportMsgType.value = 'error'
    exporting.value = false
  }
}

async function pollExport(uid, taskId) {
  try {
    const r = await api.get(`/students/${uid}/export-csv/${taskId}`)
    const d = r.data
    if (d.status === 'SUCCESS' && d.download_ready) {
      clearInterval(pollInterval)
      exportReady.value = true
      exporting.value = false
      exportMsg.value = 'Export ready! Click Download to save your CSV.'
      exportMsgType.value = 'success'
    } else if (d.status === 'FAILURE') {
      clearInterval(pollInterval)
      exporting.value  = false
      exportMsg.value = ' Export failed: ' + (d.error || 'Unknown error')
      exportMsgType.value = 'error'
    }
  } catch { /* keep polling */ }
}

async function downloadExport() {
  const uid = store.state.userId
  try {
    await api.download(
      `/students/${uid}/export-csv/${exportTaskId.value}/download`,
      `applications_${uid}.csv`
    )
  } catch (e) { alert(e.message) }
}

onMounted(fetchApplications)
</script>

<template>
  <div class="user-page">
    <div class="page-header">
      <h2 class="page-title">Student Applications</h2>
      <button class="btn-add" style="background:#3498db;" @click="exportCSV">
        ⬇ Export CSV
      </button>
    </div>

    <div class="toolbar">
      <div class="toolbar-fields">
        <input v-model="search" type="text" class="toolbar-input"
          placeholder="Search student name or drive…" />
        <select v-model="filterDrive" class="toolbar-select" style="width:auto; min-width:160px;">
          <option value="">All Drives</option>
          <option v-for="d in myDrives" :key="d.id" :value="d.id">{{ d.drive_name }}</option>
        </select>
        <select v-model="filterStatus" class="toolbar-select" style="width:auto; min-width:140px;">
          <option value="">All Status</option>
          <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
    </div>

    <!-- Summary chips -->
    <div style="display:flex; gap:1rem; flex-wrap:wrap; margin-bottom:1rem;">
      <div v-for="s in summary" :key="s.label"
        style="background:#fff; border-radius:8px; padding:.6rem 1.2rem; box-shadow:0 1px 4px rgba(0,0,0,.08); display:flex; align-items:center; gap:.6rem;">
        <span style="font-size:1.4rem; font-weight:700;" :style="{ color: s.color }">{{ s.val }}</span>
        <span style="font-size:.82rem; color:#7f8c8d;">{{ s.label }}</span>
      </div>
    </div>

    <p v-if="loading" class="loading-text">Loading applications…</p>
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>Student</th><th>Branch</th><th>CGPA</th><th>Resume</th>
            <th>Drive</th><th>Applied On</th><th>Interview</th><th>Status</th><th>Update</th><th>Remarks</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filtered.length === 0">
            <td colspan="10" class="empty-state">No applications found.</td>
          </tr>
          <tr v-for="a in filtered" :key="a.id">
            <td><strong>{{ a.student_name }}</strong></td>
            <td>{{ a.student_branch || '—' }}</td>
            <td>{{ a.student_cgpa ?? '—' }}</td>
            <td>
              <button v-if="a.has_resume" class="action-btn action-view"
                @click="viewResume(a.student_id, a.student_name)"
                :disabled="resumeLoading === a.student_id">
                {{ resumeLoading === a.student_id ? '…' : ' View' }}
              </button>
              <span v-else style="color:#95a5a6; font-size:.82rem;">—</span>
            </td>
            <td>{{ a.drive_name }}</td>
            <td>{{ fmtDate(a.application_date) }}</td>
            <td>
              <select :value="a.interview_type || ''"
                @change="updateApp(a.id, { interview_type: $event.target.value })"
                style="border:1px solid #ddd; border-radius:4px; padding:3px 6px; font-size:.8rem;">
                <option value="">— Type —</option>
                <option value="In-Person">In-Person</option>
                <option value="Online">Online</option>
                <option value="Phone">Phone</option>
                <option value="Group Discussion">Group Discussion</option>
              </select>
            </td>
            <td><span :class="['status', a.status]">{{ a.status }}</span></td>
            <td>
              <select :value="a.status"
                @change="updateApp(a.id, { status: $event.target.value })"
                style="border:1px solid #ddd; border-radius:4px; padding:3px 6px; font-size:.8rem;">
                <option value="applied">Applied</option>
                <option value="shortlisted">Shortlisted</option>
                <option value="selected">Selected</option>
                <option value="rejected">Rejected</option>
              </select>
            </td>
            <td>
              <input type="text" :value="a.remarks || ''"
                @blur="updateApp(a.id, { remarks: $event.target.value })"
                placeholder="Add remark…"
                style="border:1px solid #ddd; border-radius:4px; padding:3px 6px; font-size:.8rem; width:120px;" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- PDF Viewer Modal -->
    <div v-if="pdfModal" class="modal-overlay" @click.self="closePdf">
      <div style="background:#fff; border-radius:10px; width:95%; max-width:960px; height:90vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 5px 30px rgba(0,0,0,.3);">
        <div style="display:flex; justify-content:space-between; align-items:center; padding:.75rem 1.2rem; border-bottom:1px solid #ddd; background:#f5f5f5;">
          <strong>{{ pdfName }} — Resume</strong>
          <button class="close-btn" @click="closePdf">&times;</button>
        </div>
        <div v-if="pdfError" class="alert-strip error" style="margin:.75rem;">{{ pdfError }}</div>
        <iframe v-if="pdfSrc" :src="pdfSrc" style="flex:1; border:none; width:100%;"></iframe>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/utils/api'

const applications = ref([])
const myDrives = ref([])
const loading = ref(true)
const search = ref('')
const filterDrive  = ref('')
const filterStatus = ref('')
const statuses = ['applied', 'shortlisted', 'selected', 'rejected']

const resumeLoading = ref(null)
const pdfModal = ref(false)
const pdfSrc = ref('')
const pdfError = ref('')
const pdfName = ref('')

const filtered = computed(() => {
  let list = applications.value
  if (filterDrive.value)  list = list.filter(a => a.drive_id  === Number(filterDrive.value))
  if (filterStatus.value) list = list.filter(a => a.status === filterStatus.value)
  const q = search.value.toLowerCase()
  if (q) list = list.filter(a =>
    a.student_name?.toLowerCase().includes(q) ||
    a.drive_name?.toLowerCase().includes(q)
  )
  return list
})

const summary = computed(() => [
  { label: 'Total', val: applications.value.length,  color: '#3498db' },
  { label: 'Shortlisted', val: applications.value.filter(a => a.status === 'shortlisted').length, color: '#e67e22' },
  { label: 'Selected', val: applications.value.filter(a => a.status === 'selected').length, color: '#27ae60' },
  { label: 'Rejected', val: applications.value.filter(a => a.status === 'rejected').length, color: '#e74c3c' },
])

const fmtDate = d => d
  ? new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
  : '—'

async function load() {
  loading.value = true
  try {
    const [aR, dR] = await Promise.allSettled([api.get('/applications'), api.get('/drives')])
    if (aR.status === 'fulfilled') applications.value = aR.value.data || []
    if (dR.status === 'fulfilled') myDrives.value = dR.value.data || []
  } finally { loading.value = false }
}

async function updateApp(id, data) {
  try { await api.patch(`/applications/${id}`, data); load() }
  catch (e) { alert(e.message) }
}

async function viewResume(studentId, name) {
  resumeLoading.value = studentId; pdfError.value = ''
  try {
    const r   = await api.get(`/students/${studentId}/resume`)
    pdfSrc.value = r.data.resume
    pdfName.value = name
    pdfModal.value = true
  } catch (e) {
    pdfError.value = e.message; pdfSrc.value = ''; pdfModal.value = true
  } finally { resumeLoading.value = null }
}

function closePdf() { pdfModal.value = false; pdfSrc.value = ''; pdfError.value = '' }

function exportCSV() {
  const rows = [['Student','Branch','CGPA','Drive','Date','Status','Interview','Remarks']]
  filtered.value.forEach(a => rows.push([
    a.student_name, a.student_branch||'', a.student_cgpa||'',
    a.drive_name, fmtDate(a.application_date), a.status,
    a.interview_type||'', a.remarks||''
  ]))
  const csv  = rows.map(r => r.map(c => `"${c}"`).join(',')).join('\n')
  const el = document.createElement('a')
  el.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }))
  el.download = 'applications.csv'; el.click()
}

onMounted(load)
</script>

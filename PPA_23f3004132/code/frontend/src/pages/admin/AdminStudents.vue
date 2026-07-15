<template>
  <div class="user-page">
    <div class="page-header"><h2 class="page-title">Students</h2></div>

    <div class="toolbar">
      <div class="toolbar-fields">
        <input v-model="search" type="text" class="toolbar-input" placeholder="Search by name, email or branch…" />
      </div>
    </div>

    <p v-if="loading" class="loading-text">Loading…</p>
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr><th>Name</th><th>Email</th><th>Branch</th><th>CGPA</th><th>Year</th><th>Resume</th><th>Status</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-if="filtered.length === 0"><td colspan="8" class="empty-state">No students found.</td></tr>
          <tr v-for="s in filtered" :key="s.user_id">
            <td>{{ s.name }}</td>
            <td>{{ s.email }}</td>
            <td>{{ s.branch || '—' }}</td>
            <td>{{ s.cgpa ?? '—' }}</td>
            <td>{{ s.year ? `Year ${s.year}` : '—' }}</td>
            <td>
              <button v-if="s.has_resume" class="action-btn action-view" @click="viewResume(s.user_id, s.name)"
                :disabled="resumeLoading === s.user_id">
                {{ resumeLoading === s.user_id ? '…' : 'View PDF' }}
              </button>
              <span v-else style="color:#95a5a6; font-size:.82rem;">—</span>
            </td>
            <td><span :class="['status', s.active ? 'active' : 'blocked']">{{ s.active ? 'Active' : 'Blocked' }}</span></td>
            <td>
              <button class="action-btn action-view" @click="viewStudent(s)">View</button>
              <button v-if="s.active"  class="action-btn action-block"   @click="toggleActive(s, false)">Block</button>
              <button v-if="!s.active" class="action-btn action-unblock" @click="toggleActive(s, true)">Unblock</button>
              <button class="action-btn action-delete" @click="deleteStudent(s.user_id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="modal" class="modal-overlay" @click.self="modal=false">
      <div class="modal-card modal-content">
        <div class="modal-top">
          <h3>{{ sel.name }}</h3>
          <button class="close-btn" @click="modal=false">&times;</button>
        </div>
        <div class="profile-grid">
          <div class="profile-field"><span>Email</span><span>{{ sel.email }}</span></div>
          <div class="profile-field"><span>Branch</span><span>{{ sel.branch || '—' }}</span></div>
          <div class="profile-field"><span>CGPA</span><span>{{ sel.cgpa ?? '—' }}</span></div>
          <div class="profile-field"><span>Year</span><span>{{ sel.year ? `Year ${sel.year}` : '—' }}</span></div>
          <div class="profile-field"><span>Contact</span><span>{{ sel.contact_number || '—' }}</span></div>
          <div class="profile-field"><span>Address</span><span>{{ sel.address || '—' }}</span></div>
          <div class="profile-field"><span>Status</span><span :class="['status', sel.active ? 'active' : 'blocked']">{{ sel.active ? 'Active' : 'Blocked' }}</span></div>
        </div>
        <div v-if="sel.skills" style="margin-top:.75rem;">
          <p class="section-title">Skills</p>
          <div class="skill-tags">
            <span v-for="sk in sel.skills.split(',')" :key="sk" class="skill-tag">{{ sk.trim() }}</span>
          </div>
        </div>
        <div style="margin-top:1rem; display:flex; gap:.75rem; flex-wrap:wrap;">
          <button v-if="sel.has_resume" class="action-btn action-view"
            @click="viewResume(sel.user_id, sel.name)" :disabled="resumeLoading === sel.user_id">
            {{ resumeLoading === sel.user_id ? 'Loading…' : ' View Resume' }}
          </button>
          <button v-if="sel.has_resume" class="action-btn action-edit"
            @click="downloadResume(sel.user_id, sel.name)">⬇ Download</button>
          <button class="action-btn action-view" @click="modal=false">Close</button>
        </div>
      </div>
    </div>

    <div v-if="pdfModal" class="modal-overlay" @click.self="closePdf">
      <div style="background:#fff; border-radius:10px; width:95%; max-width:960px; height:90vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 5px 30px rgba(0,0,0,.3);">
        <div style="display:flex; justify-content:space-between; align-items:center; padding:.75rem 1.2rem; border-bottom:1px solid #ddd; background:#f5f5f5;">
          <strong> {{ pdfName }} — Resume</strong>
          <div style="display:flex; gap:.5rem;">
            <button class="action-btn action-edit" @click="downloadResume(pdfUserId, pdfName)">⬇ Download</button>
            <button class="close-btn" @click="closePdf">&times;</button>
          </div>
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

const students = ref([])
const loading = ref(true)
const search = ref('')
const modal = ref(false)
const sel = ref({})
const resumeLoading = ref(null)
const pdfModal = ref(false)
const pdfSrc = ref('')
const pdfError = ref('')
const pdfName = ref('')
const pdfUserId = ref(null)

const filtered = computed(() => {
  const q = search.value.toLowerCase()
  return q ? students.value.filter(s =>
    s.name?.toLowerCase().includes(q) ||
    s.email?.toLowerCase().includes(q) ||
    s.branch?.toLowerCase().includes(q)
  ) : students.value
})

async function load() {
  loading.value = true
  try { const r = await api.get('/students'); students.value = r.data || [] }
  finally { loading.value = false }
}
async function toggleActive(s, active) { await api.patch(`/students/${s.user_id}`, { active }); load() }
async function deleteStudent(id) { if (!confirm('Delete?')) return; await api.delete(`/students/${id}`); load() }
function viewStudent(s) { sel.value = s; modal.value = true }

async function fetchResumeB64(userId) {
  const r = await api.get(`/students/${userId}/resume`)
  return r.data.resume
}
async function viewResume(userId, name) {
  resumeLoading.value = userId; pdfError.value = ''
  try {
    const b64 = await fetchResumeB64(userId)
    pdfSrc.value = b64; pdfName.value = name; pdfUserId.value = userId
    pdfModal.value = true; modal.value = false
  } catch (e) {
    pdfError.value = e.message; pdfSrc.value = ''; pdfModal.value = true
  } finally { resumeLoading.value = null }
}
async function downloadResume(userId, name) {
  try {
    const b64 = await fetchResumeB64(userId)
    const raw  = b64.split(',')[1]
    const bytes = Uint8Array.from(atob(raw), c => c.charCodeAt(0))
    const blob  = new Blob([bytes], { type: 'application/pdf' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `${name.replace(/\s+/g,'_')}_resume.pdf`
    a.click(); URL.revokeObjectURL(a.href)
  } catch (e) { alert('Download failed: ' + e.message) }
}
function closePdf() { pdfModal.value = false; pdfSrc.value = ''; pdfError.value = '' }

onMounted(load)
</script>

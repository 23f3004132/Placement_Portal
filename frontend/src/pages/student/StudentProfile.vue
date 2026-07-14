<template>
  <div class="user-page">
    <div class="page-header">
      <h2 class="page-title">My Profile</h2>
    </div>

    <div v-if="saveSuccess" class="alert-strip success">{{ saveSuccess }}</div>
    <div v-if="saveError"   class="alert-strip error">{{ saveError }}</div>
    <p    v-if="loadingProfile" class="loading-text">Loading profile…</p>

    <div v-else style="display:grid; grid-template-columns:1fr 1.8fr; gap:1.5rem; align-items:start;">

      <!-- ── Left: Resume & Completeness ── -->
      <div>
        <!-- Resume card -->
        <div class="user-page" style="padding:1.2rem; margin-bottom:1.2rem;">
          <h3 style="margin-bottom:1rem;">Resume</h3>

          <div v-if="hasResume" style="background:#f0fff4; border:1px solid #c3e6cb; border-radius:8px; padding:1rem; text-align:center; margin-bottom:1rem;">
            <div style="font-size:2rem;"></div>
            <div style="font-weight:600; color:#155724; margin:.3rem 0;">Resume Uploaded</div>
            <div style="display:flex; gap:.5rem; justify-content:center; margin-top:.5rem;">
              <button class="action-btn action-view"  @click="viewResume"
                :disabled="resumeLoading">
                {{ resumeLoading ? '…' : 'View' }}
              </button>
              <button class="action-btn action-edit" @click="downloadResume"
                :disabled="resumeLoading">
                ⬇ Download
              </button>
            </div>
          </div>

          <!-- Upload zone -->
          <div class="resume-drop-zone"
            :class="{ 'drag-over': dragging, 'has-file': pickedFile }"
            @dragover.prevent="dragging = true"
            @dragleave.prevent="dragging = false"
            @drop.prevent="onDrop"
            @click="$refs.fileInput.click()">
            <input ref="fileInput" type="file" accept=".pdf"
              style="display:none" @change="onFilePicked" />
            <div style="font-size:1.8rem; margin-bottom:.4rem;"></div>
            <div v-if="!pickedFile" style="font-size:.85rem; color:#7f8c8d;">
              Click or drag a PDF here to {{ hasResume ? 'replace' : 'upload' }} your resume
            </div>
            <div v-else style="font-size:.85rem; font-weight:600; color:#27ae60;">
              {{ pickedFile.name }}
              <span style="font-weight:400; color:#7f8c8d;">({{ fmtSize(pickedFile.size) }})</span>
            </div>
          </div>

          <div v-if="uploadError"   class="alert-strip error"   style="margin-top:.75rem;">{{ uploadError }}</div>
          <div v-if="uploadSuccess" class="alert-strip success" style="margin-top:.75rem;">{{ uploadSuccess }}</div>

          <button v-if="pickedFile" class="btn-add" style="width:100%; margin-top:.75rem;"
            :disabled="uploading" @click="uploadResume">
            {{ uploading ? 'Uploading…' : '⬆ Upload Resume' }}
          </button>
        </div>

        <!-- Profile completeness -->
        <div class="user-page" style="padding:1.2rem;">
          <h3 style="margin-bottom:.75rem;">Profile Completeness</h3>
          <div style="background:#e0e0e0; border-radius:20px; height:10px; overflow:hidden; margin-bottom:.5rem;">
            <div :style="{ width: completeness + '%', background: completeness === 100 ? '#27ae60' : '#3498db', height:'100%', borderRadius:'20px', transition:'width .4s' }"></div>
          </div>
          <div style="font-size:.82rem; color:#7f8c8d; margin-bottom:.75rem;">{{ completeness }}% complete</div>
          <div style="display:flex; flex-direction:column; gap:.4rem;">
            <div v-for="item in checklist" :key="item.label"
              style="display:flex; align-items:center; gap:.5rem; font-size:.82rem;">
              <span :style="{ color: item.done ? '#27ae60' : '#bdc3c7', fontSize:'1rem' }">
                {{ item.done ? '✔' : '○' }}
              </span>
              <span :style="{ color: item.done ? '#2c3e50' : '#95a5a6' }">{{ item.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Right: Edit form ── -->
      <div class="user-page" style="padding:1.2rem;">
        <h3 style="margin-bottom:1.2rem;">Edit Information</h3>
        <form class="form-stack" @submit.prevent="saveProfile">

          <p class="section-title">Personal Details</p>
          <div class="form-row">
            <div class="form-group">
              <label>Full Name *</label>
              <input v-model="form.name" type="text" required />
            </div>
            <div class="form-group">
              <label>Email Address *</label>
              <input v-model="form.email" type="email" required />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Contact Number</label>
              <input v-model="form.contact_number" type="tel" placeholder="+91 9876543210" />
            </div>
            <div class="form-group">
              <label>Address</label>
              <input v-model="form.address" type="text" placeholder="City, State" />
            </div>
          </div>

          <p class="section-title">Academic Details</p>
          <div class="form-row">
            <div class="form-group">
              <label>Branch *</label>
              <input v-model="form.branch" type="text" required placeholder="Computer Science" />
            </div>
            <div class="form-group">
              <label>CGPA *</label>
              <input v-model.number="form.cgpa" type="number" step="0.01"
                min="0" max="10" required placeholder="8.5" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Current Year *</label>
              <select v-model.number="form.year" required>
                <option value="">Select year</option>
                <option v-for="y in [1,2,3,4]" :key="y" :value="y">Year {{ y }}</option>
              </select>
            </div>
          </div>

          <p class="section-title">Skills</p>
          <div class="form-group">
            <label>Skills <span style="font-weight:400; font-size:.8rem; color:#7f8c8d;">(comma-separated)</span></label>
            <input v-model="form.skills" type="text" placeholder="Python, React, SQL, Machine Learning…" />
            <div v-if="skillTags.length" class="skill-tags" style="margin-top:.5rem;">
              <span v-for="sk in skillTags" :key="sk" class="skill-tag">{{ sk }}</span>
            </div>
          </div>

          <p class="section-title">Change Password</p>
          <div class="form-group" style="max-width:320px;">
            <label>New Password <span style="font-weight:400; font-size:.8rem; color:#7f8c8d;">(leave blank to keep current)</span></label>
            <input v-model="form.password" type="password" placeholder="••••••••" autocomplete="new-password" />
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Saving…' : 'Save Changes' }}
            </button>
            <button type="button" class="btn-secondary" @click="loadProfile">Reset</button>
          </div>
        </form>
      </div>
    </div>

    <!-- PDF Viewer Modal -->
    <div v-if="pdfModal" class="modal-overlay" @click.self="closePdf">
      <div style="background:#fff; border-radius:10px; width:95%; max-width:960px; height:90vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 5px 30px rgba(0,0,0,.3);">
        <div style="display:flex; justify-content:space-between; align-items:center; padding:.75rem 1.2rem; border-bottom:1px solid #ddd; background:#f5f5f5;">
          <strong>My Resume</strong>
          <div style="display:flex; gap:.5rem;">
            <button class="action-btn action-edit" @click="downloadResume">⬇ Download</button>
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
import { useStore } from 'vuex'
import api from '@/utils/api'

const store = useStore()


const form = ref({
  name:'', email:'', contact_number:'', address:'',
  branch:'', cgpa:'', year:'', skills:'', password:'',
})
const loadingProfile = ref(true)
const saving = ref(false)
const saveSuccess = ref('')
const saveError = ref('')
const hasResume = ref(false)


const pickedFile = ref(null)
const uploading = ref(false)
const uploadError = ref('')
const uploadSuccess = ref('')
const dragging = ref(false)
const fileInput = ref(null)
const resumeLoading = ref(false)

const pdfModal = ref(false)
const pdfSrc = ref('')
const pdfError = ref('')

/* ── computed ── */
const skillTags = computed(() =>
  form.value.skills ? form.value.skills.split(',').map(s => s.trim()).filter(Boolean) : []
)

const checklist = computed(() => [
  { label: 'Full Name', done: !!form.value.name },
  { label: 'Email', done: !!form.value.email },
  { label: 'Branch', done: !!form.value.branch },
  { label: 'CGPA', done: !!form.value.cgpa },
  { label: 'Year', done: !!form.value.year },
  { label: 'Contact Number', done: !!form.value.contact_number },
  { label: 'Address', done: !!form.value.address },
  { label: 'Skills', done: skillTags.value.length > 0 },
  { label: 'Resume PDF', done: hasResume.value },
])

const completeness = computed(() => {
  const done = checklist.value.filter(c => c.done).length
  return Math.round((done / checklist.value.length) * 100)
})

const fmtSize = bytes => bytes < 1024 * 1024
  ? (bytes / 1024).toFixed(1) + ' KB'
  : (bytes / (1024 * 1024)).toFixed(1) + ' MB'


async function loadProfile() {
  loadingProfile.value = true
  saveSuccess.value = ''; saveError.value = ''
  try {
    const r = await api.get(`/students/${store.state.userId}`)
    const d = r.data || {}
    form.value = {
      name: d.name  || '',
      email: d.email || '',
      contact_number: d.contact_number || '',
      address: d.address || '',
      branch: d.branch || '',
      cgpa: d.cgpa || '',
      year: d.year || '',
      skills: d.skills || '',
      password: '',
    }
    hasResume.value = d.has_resume || false
  } catch (e) {
    saveError.value = 'Could not load profile: ' + e.message
  } finally {
    loadingProfile.value = false
  }
}

async function saveProfile() {
  saving.value = true; saveSuccess.value = ''; saveError.value = ''
  try {
    const payload = { ...form.value }
    if (!payload.password) delete payload.password
    await api.patch(`/students/${store.state.userId}`, payload)
    saveSuccess.value   = 'Profile saved successfully!'
    form.value.password = ''
  } catch (e) {
    saveError.value = e.message || 'Error saving profile.'
  } finally {
    saving.value = false
  }
}

function onFilePicked(e) {
  const file = e.target.files[0]
  if (file) validateFile(file)
}
function onDrop(e) {
  dragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) validateFile(file)
}
function validateFile(file) {
  uploadError.value = ''; uploadSuccess.value = ''
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    uploadError.value = 'Only PDF files are accepted.'; return
  }
  if (file.size > 5 * 1024 * 1024) {
    uploadError.value = 'File size must be under 5 MB.'; return
  }
  pickedFile.value = file
}

async function uploadResume() {
  if (!pickedFile.value) return
  uploading.value = true; uploadError.value = ''; uploadSuccess.value = ''
  try {
    const fd = new FormData()
    fd.append('resume', pickedFile.value)
    await api.upload(`/students/${store.state.userId}/resume`, fd)
    uploadSuccess.value = 'Resume uploaded successfully!'
    hasResume.value = true
    pickedFile.value = null
  } catch (e) {
    uploadError.value = e.message || 'Upload failed.'
  } finally {
    uploading.value = false
  }
}

async function viewResume() {
  resumeLoading.value = true; pdfError.value = ''
  try {
    const r = await api.get(`/students/${store.state.userId}/resume`)
    pdfSrc.value   = r.data.resume
    pdfModal.value = true
  } catch (e) {
    pdfError.value = e.message; pdfModal.value = true; pdfSrc.value = ''
  } finally {
    resumeLoading.value = false
  }
}

async function downloadResume() {
  resumeLoading.value = true
  try {
    const r   = await api.get(`/students/${store.state.userId}/resume`)
    const b64 = r.data.resume.split(',')[1]
    const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0))
    const blob  = new Blob([bytes], { type: 'application/pdf' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `${(form.value.name || 'my').replace(/\s+/g,'_')}_resume.pdf`
    a.click(); URL.revokeObjectURL(a.href)
  } catch (e) { alert('Download failed: ' + e.message) }
  finally { resumeLoading.value = false }
}

function closePdf() { pdfModal.value = false; pdfSrc.value = ''; pdfError.value = '' }

onMounted(loadProfile)
</script>

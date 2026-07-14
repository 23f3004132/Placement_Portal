<template>
  <div class="user-page">
    <div class="page-header">
      <h2 class="page-title">Student Dashboard</h2>
    </div>

    <!-- Stats -->
    <div class="stats-grid">
      <div class="stat-card stat-blue">
        <div class="stat-num">{{ openDrives.length }}</div>
        <div class="stat-label">Open Drives</div>
      </div>
      <div class="stat-card stat-orange">
        <div class="stat-num">{{ applications.length }}</div>
        <div class="stat-label">My Applications</div>
      </div>
      <div class="stat-card stat-green">
        <div class="stat-num">{{ selected }}</div>
        <div class="stat-label">Selections</div>
      </div>
      <div class="stat-card stat-purple">
        <div class="stat-num">{{ shortlisted }}</div>
        <div class="stat-label">Shortlisted</div>
      </div>
    </div>

    <!-- Profile summary -->
    <div class="user-page" style="margin-bottom:1.5rem; padding:1.2rem;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
        <h3>My Profile</h3>
        <router-link to="/student_dashboard/profile" class="action-btn action-edit">✏ Edit Profile</router-link>
      </div>
      <p v-if="loadingProfile" class="loading-text">Loading…</p>
      <div v-else class="profile-grid">
        <div class="profile-field"><span>Branch</span><span>{{ student.branch || '—' }}</span></div>
        <div class="profile-field"><span>CGPA</span><span>{{ student.cgpa ?? '—' }}</span></div>
        <div class="profile-field"><span>Year</span><span>{{ student.year ? `Year ${student.year}` : '—' }}</span></div>
        <div class="profile-field"><span>Contact</span><span>{{ student.contact_number || '—' }}</span></div>
        <div class="profile-field"><span>Resume</span>
          <span :style="{ color: student.has_resume ? '#27ae60' : '#e74c3c' }">
            {{ student.has_resume ? 'Uploaded' : 'Not uploaded' }}
          </span>
        </div>
      </div>
      <div v-if="student.skills" style="margin-top:.5rem;">
        <div class="skill-tags">
          <span v-for="sk in student.skills.split(',')" :key="sk" class="skill-tag">{{ sk.trim() }}</span>
        </div>
      </div>
    </div>

    <!-- Available Drives -->
    <div class="user-page" style="margin-bottom:1.5rem; padding:1.2rem;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
        <h3>Available Drives</h3>
        <router-link to="/student_dashboard/drives" class="action-btn action-view">Browse All</router-link>
      </div>
      <p v-if="loadingDrives" class="loading-text">Loading…</p>
      <div v-else-if="openDrives.length === 0" style="color:#7f8c8d;">No open drives right now.</div>
      <table v-else class="data-table">
        <thead><tr><th>Drive</th><th>Company</th><th>Job Title</th><th>Deadline</th><th>Action</th></tr></thead>
        <tbody>
          <tr v-for="d in openDrives.slice(0,5)" :key="d.id">
            <td>{{ d.drive_name }}</td>
            <td>{{ d.company_name }}</td>
            <td>{{ d.job_title }}</td>
            <td>{{ fmtDate(d.application_deadline) }}</td>
            <td>
              <button v-if="!appliedIds.has(d.id)"
                class="action-btn action-apply" @click="quickApply(d)">Apply</button>
              <span v-else class="status applied">Applied</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Application History -->
    <div class="user-page" style="padding:1.2rem;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
        <h3>Application History</h3>
        <router-link to="/student_dashboard/applications" class="action-btn action-view">View All</router-link>
      </div>
      <p v-if="loadingApps" class="loading-text">Loading…</p>
      <div v-else-if="applications.length === 0" style="color:#7f8c8d;">No applications yet.</div>
      <table v-else class="data-table">
        <thead><tr><th>Drive</th><th>Company</th><th>Date</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="a in applications.slice(0,5)" :key="a.id">
            <td>{{ a.drive_name }}</td>
            <td>{{ a.company_name }}</td>
            <td>{{ fmtDate(a.application_date) }}</td>
            <td><span :class="['status', a.status]">{{ a.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Apply confirm modal -->
    <div v-if="applyModal" class="modal-overlay" @click.self="applyModal = false">
      <div class="modal-card" style="max-width:460px;">
        <div class="modal-top">
          <h3>Confirm Application</h3>
          <button class="close-btn" @click="applyModal = false">&times;</button>
        </div>
        <div v-if="applyError" class="auth-error">{{ applyError }}</div>
        <div v-if="applyOk"    class="auth-success">{{ applyOk }}</div>
        <div class="profile-grid" style="margin-bottom:1rem;">
          <div class="profile-field"><span>Drive</span><span>{{ pending?.drive_name }}</span></div>
          <div class="profile-field"><span>Company</span><span>{{ pending?.company_name }}</span></div>
          <div class="profile-field"><span>Role</span><span>{{ pending?.job_title }}</span></div>
          <div class="profile-field" v-if="pending?.salary"><span>Salary</span><span>{{ pending.salary }}</span></div>
        </div>
        <div class="form-actions">
          <button class="btn-primary" :disabled="applying || !!applyOk" @click="confirmApply">
            {{ applying ? 'Applying…' : 'Confirm Apply' }}
          </button>
          <button class="btn-secondary" @click="applyModal = false">Cancel</button>
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
const student = ref({})
const drives = ref([])
const applications = ref([])
const loadingProfile = ref(true)
const loadingDrives = ref(true)
const loadingApps = ref(true)
const applyModal = ref(false)
const applying = ref(false)
const applyError = ref('')
const applyOk = ref('')
const pending = ref(null)

const openDrives = computed(() => drives.value.filter(d => d.status === 'approved'))
const appliedIds = computed(() => new Set(applications.value.map(a => a.drive_id)))
const selected = computed(() => applications.value.filter(a => a.status === 'selected').length)
const shortlisted = computed(() => applications.value.filter(a => a.status === 'shortlisted').length)

const fmtDate = d => d
  ? new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
  : '—'

async function fetchAll() {
  const uid = store.state.userId
  try {
    const r = await api.get(`/students/${uid}`)
    student.value = r.data || {}
  } catch { student.value = {} }
  finally { loadingProfile.value = false }

  try {
    const r = await api.get('/drives')
    drives.value = r.data || []
  } catch { drives.value = [] }
  finally { loadingDrives.value = false }

  try {
    const r = await api.get('/applications')
    applications.value = r.data || []
  } catch { applications.value = [] }
  finally { loadingApps.value = false }
}

function quickApply(d) {
  pending.value  = d
  applyError.value = ''; applyOk.value = ''
  applyModal.value = true
}

async function confirmApply() {
  applying.value = true; applyError.value = ''; applyOk.value = ''
  try {
    await api.post('/applications', { student_id: store.state.userId, drive_id: pending.value.id })
    applyOk.value = 'Applied successfully!'
    setTimeout(() => { applyModal.value = false; fetchAll() }, 1200)
  } catch (e) {
    applyError.value = e.message || 'Application failed.'
  } finally { applying.value = false }
}

onMounted(fetchAll)
</script>

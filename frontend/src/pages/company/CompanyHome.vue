<template>
  <div class="user-page">
    <div class="page-header">
      <h2 class="page-title">Company Dashboard</h2>
    </div>

    <!-- Approval banner -->
    <div v-if="company.approval_status === 'pending'"    class="alert-strip warn">
      Your company registration is pending admin approval. You can create drives once approved.
    </div>
    <div v-if="company.approval_status === 'rejected'"   class="alert-strip error">
      Your registration was rejected. Contact the placement cell.
    </div>
    <div v-if="company.approval_status === 'blacklisted'" class="alert-strip error">
      Your account has been blacklisted. Contact the placement cell.
    </div>

    <!-- Stats -->
    <div class="stats-grid">
      <div class="stat-card stat-blue">
        <div class="stat-num">{{ drives.length }}</div>
        <div class="stat-label">Total Drives</div>
      </div>
      <div class="stat-card stat-green">
        <div class="stat-num">{{ totalApplicants }}</div>
        <div class="stat-label">Total Applicants</div>
      </div>
      <div class="stat-card stat-orange">
        <div class="stat-num">{{ shortlisted }}</div>
        <div class="stat-label">Shortlisted</div>
      </div>
      <div class="stat-card stat-purple">
        <div class="stat-num">{{ selected }}</div>
        <div class="stat-label">Selected</div>
      </div>
    </div>

    <!-- Company Profile summary -->
    <div class="user-page" style="margin-bottom:1.5rem; padding:1.2rem;">
      <h3 style="margin-bottom:1rem;">Company Profile</h3>
      <p v-if="loadingProfile" class="loading-text">Loading…</p>
      <div v-else class="profile-grid">
        <div class="profile-field"><span>Company</span><span>{{ company.company_name }}</span></div>
        <div class="profile-field"><span>Industry</span><span>{{ company.industry || '—' }}</span></div>
        <div class="profile-field"><span>Location</span><span>{{ company.location || '—' }}</span></div>
        <div class="profile-field"><span>HR Contact</span><span>{{ company.hr_contact || '—' }}</span></div>
        <div class="profile-field"><span>Website</span><span>{{ company.website || '—' }}</span></div>
        <div class="profile-field"><span>Status</span>
          <span :class="['status', company.approval_status]">{{ company.approval_status }}</span>
        </div>
      </div>
      <router-link to="/company_dashboard/profile" class="action-btn action-edit" style="display:inline-block; margin-top:.75rem;">
        ✏ Edit Profile
      </router-link>
    </div>

    <!-- Upcoming Drives -->
    <div class="user-page" style="margin-bottom:1.5rem; padding:1.2rem;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
        <h3> My Drives</h3>
        <router-link to="/company_dashboard/drives" class="action-btn action-view">Manage Drives</router-link>
      </div>
      <p v-if="loadingDrives" class="loading-text">Loading…</p>
      <div v-else-if="drives.length === 0" style="color:#7f8c8d;">No drives created yet.</div>
      <table v-else class="data-table">
        <thead><tr><th>Drive</th><th>Job Title</th><th>Deadline</th><th>Applicants</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="d in drives.slice(0, 6)" :key="d.id">
            <td>{{ d.drive_name }}</td>
            <td>{{ d.job_title }}</td>
            <td>{{ fmtDate(d.application_deadline) }}</td>
            <td>{{ d.applicant_count }}</td>
            <td><span :class="['status', d.status]">{{ d.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Recent Applications -->
    <div class="user-page" style="padding:1.2rem;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
        <h3>Recent Applications</h3>
        <router-link to="/company_dashboard/applications" class="action-btn action-view">View All</router-link>
      </div>
      <p v-if="loadingApps" class="loading-text">Loading…</p>
      <div v-else-if="applications.length === 0" style="color:#7f8c8d;">No applications yet.</div>
      <table v-else class="data-table">
        <thead><tr><th>Student</th><th>Branch</th><th>CGPA</th><th>Drive</th><th>Date</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="a in applications.slice(0, 6)" :key="a.id">
            <td>{{ a.student_name }}</td>
            <td>{{ a.student_branch || '—' }}</td>
            <td>{{ a.student_cgpa ?? '—' }}</td>
            <td>{{ a.drive_name }}</td>
            <td>{{ fmtDate(a.application_date) }}</td>
            <td><span :class="['status', a.status]">{{ a.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import api from '@/utils/api'

const store          = useStore()
const company        = ref({})
const drives         = ref([])
const applications   = ref([])
const loadingProfile = ref(true)
const loadingDrives  = ref(true)
const loadingApps    = ref(true)

const totalApplicants = computed(() => drives.value.reduce((s, d) => s + (d.applicant_count || 0), 0))
const shortlisted     = computed(() => applications.value.filter(a => a.status === 'shortlisted').length)
const selected        = computed(() => applications.value.filter(a => a.status === 'selected').length)

const fmtDate = d => d
  ? new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
  : '—'

async function fetchAll() {
  const uid = store.state.userId
  try {
    const r = await api.get(`/companies/${uid}`)
    company.value = r.data || {}
  } catch { company.value = {} }
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

onMounted(fetchAll)
</script>

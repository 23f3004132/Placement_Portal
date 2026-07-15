<template>
  <div class="user-page">
    <div class="page-header">
      <h2 class="page-title">Admin Dashboard</h2>
    </div>

    <div class="stats-grid">
      <div class="stat-card stat-blue">
        <div class="stat-num">{{ stats.students }}</div>
        <div class="stat-label">Total Students</div>
      </div>
      <div class="stat-card stat-green">
        <div class="stat-num">{{ stats.companies }}</div>
        <div class="stat-label">Total Companies</div>
      </div>
      <div class="stat-card stat-orange">
        <div class="stat-num">{{ stats.drives }}</div>
        <div class="stat-label">Placement Drives</div>
      </div>
      <div class="stat-card stat-purple">
        <div class="stat-num">{{ stats.applications }}</div>
        <div class="stat-label">Applications</div>
      </div>
    </div>

    <div class="user-page" style="margin-bottom:1.5rem; padding:1.2rem;">
      <h3 style="margin-bottom:1rem;">Search</h3>
      <div class="toolbar">
        <div class="toolbar-fields">
          <input v-model="searchQ" @keyup.enter="doSearch" type="text"
            class="toolbar-input" placeholder="Search students, companies, drives…" />
          <select v-model="searchType" class="toolbar-select" style="width:auto; min-width:140px;">
            <option value="student">Students</option>
            <option value="company">Companies</option>
            <option value="drive">Drives</option>
          </select>
        </div>
        <div class="toolbar-actions">
          <button class="btn-primary" @click="doSearch">Search</button>
          <button class="btn-secondary" @click="clearSearch">Clear</button>
        </div>
      </div>
      <div v-if="searchResults.length" class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th v-for="col in searchCols" :key="col">{{ col }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, i) in searchResults" :key="i">
              <td v-for="col in searchKeys" :key="col">
                <span v-if="col === 'status' || col === 'approval_status'"
                  :class="['status', row[col]]">{{ row[col] }}</span>
                <span v-else>{{ row[col] ?? '—' }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else-if="searched" style="color:#7f8c8d; margin-top:.75rem;">No results found.</p>
    </div>

    <div class="user-page" style="margin-bottom:1.5rem; padding:1.2rem;">
      <h3 style="margin-bottom:1rem;">Company Registrations Pending Approval</h3>
      <p v-if="loading" class="loading-text">Loading…</p>
      <div v-else-if="pendingCompanies.length === 0" style="color:#7f8c8d;">No pending company registrations.</div>
      <table v-else class="data-table">
        <thead><tr><th>#</th><th>Company</th><th>Email</th><th>Action</th></tr></thead>
        <tbody>
          <tr v-for="c in pendingCompanies" :key="c.user_id">
            <td>{{ c.user_id }}</td>
            <td>{{ c.company_name }}</td>
            <td>{{ c.email }}</td>
            <td>
              <button class="action-btn action-approve" @click="approveCompany(c.user_id)">Approve</button>
              <button class="action-btn action-reject"  @click="rejectCompany(c.user_id)">Reject</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="user-page" style="margin-bottom:1.5rem; padding:1.2rem;">
      <h3 style="margin-bottom:1rem;">Drives Pending Approval</h3>
      <p v-if="loading" class="loading-text">Loading…</p>
      <div v-else-if="pendingDrives.length === 0" style="color:#7f8c8d;">No pending drives.</div>
      <table v-else class="data-table">
        <thead><tr><th>#</th><th>Drive</th><th>Company</th><th>Job Title</th><th>Action</th></tr></thead>
        <tbody>
          <tr v-for="d in pendingDrives" :key="d.id">
            <td>{{ d.id }}</td>
            <td>{{ d.drive_name }}</td>
            <td>{{ d.company_name }}</td>
            <td>{{ d.job_title }}</td>
            <td>
              <button class="action-btn action-approve" @click="approveDrive(d.id)">Approve</button>
              <button class="action-btn action-reject"  @click="rejectDrive(d.id)">Reject</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="user-page" style="padding:1.2rem;">
      <h3 style="margin-bottom:1rem;">Recent Student Applications</h3>
      <p v-if="loading" class="loading-text">Loading…</p>
      <div v-else-if="applications.length === 0" style="color:#7f8c8d;">No applications yet.</div>
      <table v-else class="data-table">
        <thead><tr><th>#</th><th>Student</th><th>Drive</th><th>Company</th><th>Date</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="a in applications.slice(0,10)" :key="a.id">
            <td>{{ a.id }}</td>
            <td>{{ a.student_name }}</td>
            <td>{{ a.drive_name }}</td>
            <td>{{ a.company_name }}</td>
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
import api from '@/utils/api'

const loading = ref(true)
const companies = ref([])
const drives = ref([])
const applications = ref([])
const students = ref([])

const searchQ = ref('')
const searchType = ref('student')
const searchResults = ref([])
const searched = ref(false)

const stats = computed(() => ({
  students: students.value.length,
  companies: companies.value.length,
  drives: drives.value.length,
  applications: applications.value.length,
}))

const pendingCompanies = computed(() => companies.value.filter(c => c.approval_status === 'pending'))
const pendingDrives = computed(() => drives.value.filter(d => d.status === 'pending'))

const searchColMap = {
  student: { cols: ['Name','Email','Branch','CGPA','Status'], keys: ['name','email','branch','cgpa','active'] },
  company: { cols: ['Company','Email','Industry','Location','Status'], keys: ['company_name','email','industry','location','approval_status'] },
  drive:   { cols: ['Drive','Company','Job Title','Deadline','Status'], keys: ['drive_name','company_name','job_title','application_deadline','status'] },
}
const searchCols = computed(() => searchColMap[searchType.value]?.cols || [])
const searchKeys = computed(() => searchColMap[searchType.value]?.keys || [])

const fmtDate = d => d ? new Date(d).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' }) : '—'

async function fetchAll() {
  loading.value = true
  try {
    const [c, d, a, s] = await Promise.allSettled([
      api.get('/companies'), api.get('/drives'),
      api.get('/applications'), api.get('/students'),
    ])
    if (c.status === 'fulfilled') companies.value = c.value.data || []
    if (d.status === 'fulfilled') drives.value = d.value.data || []
    if (a.status === 'fulfilled') applications.value = a.value.data || []
    if (s.status === 'fulfilled') students.value = s.value.data || []
  } finally { loading.value = false }
}

async function approveCompany(id) {
  await api.patch(`/companies/${id}`, { approval_status: 'approved' })
  fetchAll()
}
async function rejectCompany(id) {
  await api.patch(`/companies/${id}`, { approval_status: 'rejected' })
  fetchAll()
}
async function approveDrive(id) {
  await api.patch(`/drives/${id}`, { status: 'approved' })
  fetchAll()
}
async function rejectDrive(id) {
  await api.patch(`/drives/${id}`, { status: 'rejected' })
  fetchAll()
}

async function doSearch() {
  searched.value = true
  const q = searchQ.value.trim()
  try {
    let res
    if (searchType.value === 'student') res = await api.get(`/students/search?name=${q}`)
    else if (searchType.value === 'company') res = await api.get(`/companies/search?name=${q}`)
    else res = await api.get(`/drives/search?name=${q}`)
    searchResults.value = res.data || []
  } catch { searchResults.value = [] }
}
function clearSearch() { searchQ.value = ''; searchResults.value = []; searched.value = false }

onMounted(fetchAll)
</script>

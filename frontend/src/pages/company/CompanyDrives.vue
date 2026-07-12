<template>
  <div class="user-page">
    <div class="page-header">
      <h2 class="page-title">My Placement Drives</h2>
      <button class="btn-add" @click="openCreate" :disabled="!isApproved">
        + Create Drive
      </button>
    </div>
    <div v-if="!isApproved" class="alert-strip warn" style="margin-bottom:1rem;">
      Your company must be approved before creating drives.
    </div>

    <p v-if="loading" class="loading-text">Loading drives…</p>
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr><th>#</th><th>Drive</th><th>Job Title</th><th>Deadline</th><th>Applicants</th><th>Status</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-if="drives.length === 0">
            <td colspan="7" class="empty-state">No drives yet. Create your first drive!</td>
          </tr>
          <tr v-for="d in drives" :key="d.id">
            <td>{{ d.id }}</td>
            <td><strong>{{ d.drive_name }}</strong></td>
            <td>{{ d.job_title }}</td>
            <td>{{ fmtDate(d.application_deadline) }}</td>
            <td>{{ d.applicant_count }}</td>
            <td><span :class="['status', d.status]">{{ d.status }}</span></td>
            <td>
              <button class="action-btn action-view"  @click="viewDrive(d)">View</button>
              <button class="action-btn action-edit"  @click="openEdit(d)"
                :disabled="d.status !== 'pending'">Edit</button>
              <button v-if="d.status === 'approved'"
                class="action-btn action-close" @click="closeDrive(d.id)">Close</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create / Edit Modal -->
    <div v-if="formModal" class="modal-overlay" @click.self="formModal = false">
      <div class="modal-card" style="max-width:580px;">
        <div class="modal-top">
          <h3>{{ editing ? 'Edit Drive' : 'Create New Drive' }}</h3>
          <button class="close-btn" @click="formModal = false">&times;</button>
        </div>
        <div v-if="formError" class="auth-error">{{ formError }}</div>
        <form class="form-stack" @submit.prevent="saveDrive">
          <div class="form-group">
            <label>Drive Name *</label>
            <input v-model="form.drive_name" type="text" required placeholder="e.g. Campus Hiring 2025" />
          </div>
          <div class="form-group">
            <label>Job Title *</label>
            <input v-model="form.job_title" type="text" required placeholder="e.g. Software Engineer" />
          </div>
          <div class="form-group">
            <label>Job Description</label>
            <textarea v-model="form.job_description" rows="3"
              placeholder="Describe the role, responsibilities…"></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Salary Package</label>
              <input v-model="form.salary" type="text" placeholder="e.g. ₹8 LPA" />
            </div>
            <div class="form-group">
              <label>Location</label>
              <input v-model="form.location" type="text" placeholder="e.g. Bangalore" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Eligible Branch</label>
              <input v-model="form.eligibility_branch" type="text" placeholder="CSE, ECE or Any" />
            </div>
            <div class="form-group">
              <label>Min CGPA</label>
              <input v-model.number="form.eligibility_cgpa" type="number" step="0.1" min="0" max="10" placeholder="0 = Any" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Eligible Year</label>
              <select v-model.number="form.eligibility_year">
                <option value="">Any</option>
                <option v-for="y in [1,2,3,4]" :key="y" :value="y">Year {{ y }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Application Deadline</label>
              <input v-model="form.application_deadline" type="date" />
            </div>
          </div>
          <div class="form-actions">
            <button type="submit"  class="btn-primary"   :disabled="saving">
              {{ saving ? 'Saving…' : (editing ? 'Save Changes' : 'Create Drive') }}
            </button>
            <button type="button"  class="btn-secondary" @click="formModal = false">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <!-- View Drive Modal -->
    <div v-if="viewModal" class="modal-overlay" @click.self="viewModal = false">
      <div class="modal-card modal-content">
        <div class="modal-top">
          <h3>{{ sel.drive_name }}</h3>
          <button class="close-btn" @click="viewModal = false">&times;</button>
        </div>
        <div class="profile-grid">
          <div class="profile-field"><span>Job Title</span><span>{{ sel.job_title }}</span></div>
          <div class="profile-field"><span>Salary</span><span>{{ sel.salary || '—' }}</span></div>
          <div class="profile-field"><span>Location</span><span>{{ sel.location || '—' }}</span></div>
          <div class="profile-field"><span>Deadline</span><span>{{ fmtDate(sel.application_deadline) }}</span></div>
          <div class="profile-field"><span>Min CGPA</span><span>{{ sel.eligibility_cgpa || 'Any' }}</span></div>
          <div class="profile-field"><span>Branch</span><span>{{ sel.eligibility_branch || 'Any' }}</span></div>
          <div class="profile-field"><span>Year</span><span>{{ sel.eligibility_year ? `Year ${sel.eligibility_year}` : 'Any' }}</span></div>
          <div class="profile-field"><span>Applicants</span><span>{{ sel.applicant_count }}</span></div>
          <div class="profile-field"><span>Status</span><span :class="['status', sel.status]">{{ sel.status }}</span></div>
        </div>
        <p v-if="sel.job_description" class="detail-text">{{ sel.job_description }}</p>
        <div class="modal-actions">
          <button class="action-btn action-view" @click="viewModal = false">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import api from '@/utils/api'

const store      = useStore()
const drives     = ref([])
const company    = ref(null)
const loading    = ref(true)
const formModal  = ref(false)
const viewModal  = ref(false)
const editing    = ref(false)
const editId     = ref(null)
const saving     = ref(false)
const formError  = ref('')
const sel        = ref({})

const isApproved = computed(() => company.value?.approval_status === 'approved')

const blank = () => ({
  drive_name: '', job_title: '', job_description: '',
  salary: '', location: '', eligibility_branch: '',
  eligibility_cgpa: '', eligibility_year: '', application_deadline: '',
})
const form = ref(blank())

const fmtDate = d => d
  ? new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
  : '—'

async function load() {
  loading.value = true
  const uid = store.state.userId
  try {
    const [dR, cR] = await Promise.allSettled([api.get('/drives'), api.get(`/companies/${uid}`)])
    if (dR.status === 'fulfilled') drives.value  = dR.value.data  || []
    if (cR.status === 'fulfilled') company.value = cR.value.data  || null
  } finally { loading.value = false }
}

function openCreate() { editing.value = false; editId.value = null; form.value = blank(); formError.value = ''; formModal.value = true }
function openEdit(d)  {
  editing.value = true; editId.value = d.id; formError.value = ''
  form.value = { drive_name: d.drive_name, job_title: d.job_title, job_description: d.job_description,
    salary: d.salary, location: d.location, eligibility_branch: d.eligibility_branch,
    eligibility_cgpa: d.eligibility_cgpa, eligibility_year: d.eligibility_year,
    application_deadline: d.application_deadline }
  formModal.value = true
}
function viewDrive(d) { sel.value = d; viewModal.value = true }

async function saveDrive() {
  saving.value = true; formError.value = ''
  try {
    const payload = { ...form.value, company_id: store.state.userId }
    if (editing.value) await api.patch(`/drives/${editId.value}`, payload)
    else               await api.post('/drives', payload)
    formModal.value = false; load()
  } catch (e) { formError.value = e.message || 'Error saving drive.' }
  finally { saving.value = false }
}

async function closeDrive(id) {
  if (!confirm('Close this drive?')) return
  try { await api.patch(`/drives/${id}`, { status: 'closed' }); load() }
  catch (e) { alert(e.message) }
}

onMounted(load)
</script>

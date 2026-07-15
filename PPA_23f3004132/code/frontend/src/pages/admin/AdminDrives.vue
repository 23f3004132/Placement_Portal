<template>
  <div class="user-page">
    <div class="page-header">
      <h2 class="page-title">Placement Drives</h2>
    </div>

    <div class="toolbar">
      <div class="toolbar-fields">
        <input v-model="search" type="text" class="toolbar-input"
          placeholder="Search by drive name or company…" />
        <select v-model="filterStatus" class="toolbar-select" style="width:auto; min-width:140px;">
          <option value="">All Status</option>
          <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
    </div>

    <p v-if="loading" class="loading-text">Loading drives…</p>
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>#</th><th>Drive</th><th>Company</th><th>Job Title</th>
            <th>Deadline</th><th>Applicants</th><th>Status</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filtered.length === 0">
            <td colspan="8" class="empty-state">No drives found.</td>
          </tr>
          <tr v-for="d in filtered" :key="d.id">
            <td>{{ d.id }}</td>
            <td><strong>{{ d.drive_name }}</strong></td>
            <td>{{ d.company_name }}</td>
            <td>{{ d.job_title }}</td>
            <td>{{ fmtDate(d.application_deadline) }}</td>
            <td>{{ d.applicant_count }}</td>
            <td><span :class="['status', d.status]">{{ d.status }}</span></td>
            <td>
              <button class="action-btn action-view" @click="viewDrive(d)">View</button>
              <button v-if="d.status === 'pending'"
                class="action-btn action-approve" @click="updateDrive(d.id,'approved')">Approve</button>
              <button v-if="d.status === 'pending'"
                class="action-btn action-reject" @click="updateDrive(d.id,'rejected')">Reject</button>
              <button v-if="d.status === 'approved'"
                class="action-btn action-close" @click="updateDrive(d.id,'closed')">Close</button>
              <button class="action-btn action-delete" @click="deleteDrive(d.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="modal" class="modal-overlay" @click.self="modal = false">
      <div class="modal-card modal-content">
        <div class="modal-top">
          <h3>{{ sel.drive_name }}</h3>
          <button class="close-btn" @click="modal = false">&times;</button>
        </div>

        <div class="profile-grid">
          <div class="profile-field"><span>Company</span><span>{{ sel.company_name }}</span></div>
          <div class="profile-field"><span>Job Title</span><span>{{ sel.job_title }}</span></div>
          <div class="profile-field"><span>Salary</span><span>{{ sel.salary || '—' }}</span></div>
          <div class="profile-field"><span>Location</span><span>{{ sel.location || '—' }}</span></div>
          <div class="profile-field"><span>Deadline</span><span>{{ fmtDate(sel.application_deadline) }}</span></div>
          <div class="profile-field"><span>Applicants</span><span>{{ sel.applicant_count }}</span></div>
          <div class="profile-field"><span>Min CGPA</span><span>{{ sel.eligibility_cgpa || 'Any' }}</span></div>
          <div class="profile-field"><span>Branch</span><span>{{ sel.eligibility_branch || 'Any' }}</span></div>
          <div class="profile-field"><span>Year</span><span>{{ sel.eligibility_year ? `Year ${sel.eligibility_year}` : 'Any' }}</span></div>
          <div class="profile-field"><span>Status</span>
            <span :class="['status', sel.status]">{{ sel.status }}</span>
          </div>
        </div>

        <p v-if="sel.job_description" class="detail-text">{{ sel.job_description }}</p>

        <div class="modal-actions">
          <button v-if="sel.status === 'pending'"
            class="action-btn action-approve" @click="updateDrive(sel.id,'approved'); modal=false">Approve</button>
          <button v-if="sel.status === 'pending'"
            class="action-btn action-reject"  @click="updateDrive(sel.id,'rejected'); modal=false">Reject</button>
          <button v-if="sel.status === 'approved'"
            class="action-btn action-close"   @click="updateDrive(sel.id,'closed'); modal=false">Close Drive</button>
          <button class="action-btn action-view" @click="modal = false">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/utils/api'

const drives = ref([])
const loading = ref(true)
const search = ref('')
const filterStatus = ref('')
const modal = ref(false)
const sel = ref({})
const statuses = ['pending', 'approved', 'rejected', 'closed']

const filtered = computed(() => {
  let list = drives.value
  if (filterStatus.value) list = list.filter(d => d.status === filterStatus.value)
  const q = search.value.toLowerCase()
  if (q) list = list.filter(d =>
    d.drive_name?.toLowerCase().includes(q) ||
    d.company_name?.toLowerCase().includes(q) ||
    d.job_title?.toLowerCase().includes(q)
  )
  return list
})

const fmtDate = d => d
  ? new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
  : '—'

async function load() {
  loading.value = true
  try { const r = await api.get('/drives'); drives.value = r.data || [] }
  catch (e) { drives.value = [] }
  finally { loading.value = false }
}

async function updateDrive(id, status) {
  try { await api.patch(`/drives/${id}`, { status }); load() }
  catch (e) { alert(e.message) }
}

async function deleteDrive(id) {
  if (!confirm('Delete this drive? This cannot be undone.')) return
  try { await api.delete(`/drives/${id}`); load() }
  catch (e) { alert(e.message) }
}

function viewDrive(d) { sel.value = d; modal.value = true }

onMounted(load)
</script>

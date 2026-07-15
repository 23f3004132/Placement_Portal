<template>
  <div class="user-page">
    <div class="page-header">
      <h2 class="page-title">Companies</h2>
    </div>

    <div class="toolbar">
      <div class="toolbar-fields">
        <input v-model="search" type="text" class="toolbar-input" placeholder="Search by name or industry…" />
        <select v-model="filterStatus" class="toolbar-select" style="width:auto; min-width:150px;">
          <option value="">All Status</option>
          <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
    </div>

    <p v-if="loading" class="loading-text">Loading companies…</p>
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>Company</th><th>Email</th><th>Industry</th>
            <th>Location</th><th>Drives</th><th>Status</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filtered.length === 0"><td colspan="7" class="empty-state">No companies found.</td></tr>
          <tr v-for="c in filtered" :key="c.user_id">
            <td><strong>{{ c.company_name }}</strong></td>
            <td>{{ c.email }}</td>
            <td>{{ c.industry || '—' }}</td>
            <td>{{ c.location || '—' }}</td>
            <td>{{ c.drive_count }}</td>
            <td><span :class="['status', c.approval_status]">{{ c.approval_status }}</span></td>
            <td>
              <button class="action-btn action-view" @click="viewCompany(c)">View</button>
              <button v-if="c.approval_status === 'pending'"
                class="action-btn action-approve" @click="updateStatus(c.user_id,'approved')">Approve</button>
              <button v-if="c.approval_status === 'pending'"
                class="action-btn action-reject" @click="updateStatus(c.user_id,'rejected')">Reject</button>
              <button v-if="c.approval_status === 'approved'"
                class="action-btn action-block" @click="updateStatus(c.user_id,'blacklisted')">Blacklist</button>
              <button v-if="c.approval_status === 'blacklisted' || c.approval_status === 'rejected'"
                class="action-btn action-unblock" @click="updateStatus(c.user_id,'approved')">Restore</button>
              <button class="action-btn action-delete" @click="deleteCompany(c.user_id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="modal" class="modal-overlay" @click.self="modal=false">
      <div class="modal-card modal-content">
        <div class="modal-top">
          <h3>{{ sel.company_name }}</h3>
          <button class="close-btn" @click="modal=false">&times;</button>
        </div>
        <div class="profile-grid">
          <div class="profile-field"><span>Email</span><span>{{ sel.email }}</span></div>
          <div class="profile-field"><span>Industry</span><span>{{ sel.industry || '—' }}</span></div>
          <div class="profile-field"><span>Location</span><span>{{ sel.location || '—' }}</span></div>
          <div class="profile-field"><span>HR Contact</span><span>{{ sel.hr_contact || '—' }}</span></div>
          <div class="profile-field"><span>HR Email</span><span>{{ sel.hr_email || '—' }}</span></div>
          <div class="profile-field"><span>Website</span><span>{{ sel.website || '—' }}</span></div>
          <div class="profile-field"><span>Status</span><span :class="['status', sel.approval_status]">{{ sel.approval_status }}</span></div>
          <div class="profile-field"><span>Drives</span><span>{{ sel.drive_count }}</span></div>
        </div>
        <p v-if="sel.description" class="detail-text">{{ sel.description }}</p>
        <div class="modal-actions">
          <button v-if="sel.approval_status === 'pending'"
            class="action-btn action-approve" @click="updateStatus(sel.user_id,'approved'); modal=false">Approve</button>
          <button v-if="sel.approval_status === 'pending'"
            class="action-btn action-reject" @click="updateStatus(sel.user_id,'rejected'); modal=false">Reject</button>
          <button v-if="sel.approval_status === 'approved'"
            class="action-btn action-block" @click="updateStatus(sel.user_id,'blacklisted'); modal=false">Blacklist</button>
          <button class="action-btn action-view" @click="modal=false">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/utils/api'

const companies = ref([])
const loading = ref(true)
const search = ref('')
const filterStatus = ref('')
const modal = ref(false)
const sel = ref({})
const statuses = ['pending','approved','rejected','blacklisted']

const filtered = computed(() => {
  let list = companies.value
  if (filterStatus.value) list = list.filter(c => c.approval_status === filterStatus.value)
  const q = search.value.toLowerCase()
  if (q) list = list.filter(c => c.company_name?.toLowerCase().includes(q) || c.industry?.toLowerCase().includes(q))
  return list
})

async function load() {
  loading.value = true
  try { const r = await api.get('/companies'); companies.value = r.data || [] }
  finally { loading.value = false }
}

async function updateStatus(id, approval_status) {
  await api.patch(`/companies/${id}`, { approval_status }); load()
}
async function deleteCompany(id) {
  if (!confirm('Delete this company?')) return
  await api.delete(`/companies/${id}`); load()
}
function viewCompany(c) { sel.value = c; modal.value = true }

onMounted(load)
</script>

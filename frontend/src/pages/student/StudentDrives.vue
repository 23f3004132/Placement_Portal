<template>
  <div class="user-page">
    <div class="page-header">
      <h2 class="page-title">Browse Placement Drives</h2>
    </div>

    <!-- Search & Filter bar -->
    <div class="toolbar">
      <div class="toolbar-fields">
        <input v-model="search" type="text" class="toolbar-input"
          placeholder="Search by drive name, company or role…" />
        <input v-model="filterBranch" type="text" class="toolbar-input"
          placeholder="Filter branch…" style="max-width:160px;" />
        <input v-model.number="filterCgpa" type="number" step="0.1"
          min="0" max="10" class="toolbar-input"
          placeholder="My CGPA" style="max-width:110px;" />
      </div>
      <div class="toolbar-actions">
        <button class="btn-secondary" @click="resetFilters">Clear</button>
      </div>
    </div>

    <p style="font-size:.85rem; color:#7f8c8d; margin-bottom:1rem;">
      Showing {{ filtered.length }} drive(s)
    </p>

    <p v-if="loading" class="loading-text">Loading drives…</p>

    <div v-else-if="filtered.length === 0"
      style="text-align:center; padding:3rem; color:#7f8c8d;">
      No drives match your search criteria.
    </div>

    <!-- Drive cards -->
    <div v-else style="display:grid; grid-template-columns:repeat(auto-fill, minmax(320px,1fr)); gap:1.2rem;">
      <div v-for="d in filtered" :key="d.id"
        style="background:#fff; border-radius:10px; border:1px solid #e0e0e0; overflow:hidden; box-shadow:0 2px 6px rgba(0,0,0,.06); transition:box-shadow .2s;"
        @mouseenter="$event.currentTarget.style.boxShadow='0 4px 16px rgba(0,0,0,.12)'"
        @mouseleave="$event.currentTarget.style.boxShadow='0 2px 6px rgba(0,0,0,.06)'">

        <!-- Card header -->
        <div style="background:linear-gradient(135deg,#2c3e50,#34495e); padding:1rem 1.2rem;">
          <div style="font-size:1rem; font-weight:700; color:#fff;">{{ d.drive_name }}</div>
          <div style="font-size:.82rem; color:#ecf0f1; margin-top:.2rem;">{{ d.company_name }}</div>
        </div>

        <!-- Card body -->
        <div style="padding:1rem 1.2rem;">
          <div style="font-size:.92rem; font-weight:600; color:#2c3e50; margin-bottom:.75rem;">
            {{ d.job_title }}
          </div>

          <div style="display:grid; grid-template-columns:1fr 1fr; gap:.4rem .75rem; margin-bottom:.75rem;">
            <div style="font-size:.8rem; color:#7f8c8d;">
              {{ d.salary || 'Not disclosed' }}
            </div>
            <div style="font-size:.8rem; color:#7f8c8d;">
              {{ d.location || 'Not specified' }}
            </div>
            <div style="font-size:.8rem; color:#7f8c8d;">
              Deadline: {{ fmtDate(d.application_deadline) }}
            </div>
            <div style="font-size:.8rem; color:#7f8c8d;">
              {{ d.applicant_count }} applicant(s)
            </div>
          </div>

          <!-- Eligibility tags -->
          <div style="display:flex; gap:.4rem; flex-wrap:wrap; margin-bottom:.85rem;">
            <span v-if="d.eligibility_cgpa"
              style="background:#e8f4fd; color:#2980b9; padding:.2rem .65rem; border-radius:20px; font-size:.75rem; font-weight:600;">
              CGPA ≥ {{ d.eligibility_cgpa }}
            </span>
            <span v-if="d.eligibility_branch && d.eligibility_branch.toLowerCase() !== 'any'"
              style="background:#e8f4fd; color:#2980b9; padding:.2rem .65rem; border-radius:20px; font-size:.75rem; font-weight:600;">
              {{ d.eligibility_branch }}
            </span>
            <span v-if="d.eligibility_year"
              style="background:#e8f4fd; color:#2980b9; padding:.2rem .65rem; border-radius:20px; font-size:.75rem; font-weight:600;">
              Year {{ d.eligibility_year }}
            </span>
            <span v-if="!d.eligibility_cgpa && !d.eligibility_branch && !d.eligibility_year"
              style="background:#d4edda; color:#155724; padding:.2rem .65rem; border-radius:20px; font-size:.75rem; font-weight:600;">
              Open to All
            </span>
          </div>

          <p v-if="d.job_description"
            style="font-size:.8rem; color:#7f8c8d; line-height:1.5; margin-bottom:.85rem; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;">
            {{ d.job_description }}
          </p>

          <!-- Action row -->
          <div style="display:flex; gap:.6rem; justify-content:space-between; align-items:center;">
            <button class="action-btn action-view" @click="viewDrive(d)">View Details</button>
            <button v-if="!appliedIds.has(d.id)"
              class="action-btn action-apply" @click="openApply(d)">
              Apply Now
            </button>
            <span v-else class="status applied" style="font-size:.82rem;"> Applied</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Drive Detail Modal -->
    <div v-if="detailModal" class="modal-overlay" @click.self="detailModal = false">
      <div class="modal-card modal-content">
        <div class="modal-top">
          <h3>{{ sel.drive_name }}</h3>
          <button class="close-btn" @click="detailModal = false">&times;</button>
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
          <div class="profile-field"><span>Year</span>
            <span>{{ sel.eligibility_year ? `Year ${sel.eligibility_year}` : 'Any' }}</span>
          </div>
        </div>

        <p v-if="sel.job_description" class="detail-text">{{ sel.job_description }}</p>

        <div v-if="applyError" class="auth-error">{{ applyError }}</div>
        <div v-if="applyOk"    class="auth-success">{{ applyOk }}</div>

        <div class="modal-actions">
          <button v-if="!appliedIds.has(sel.id)"
            class="action-btn action-apply" :disabled="applying || !!applyOk"
            @click="confirmApply(sel)">
            {{ applying ? 'Applying…' : 'Apply Now' }}
          </button>
          <span v-else class="status applied">Already Applied</span>
          <button class="action-btn action-view" @click="detailModal = false">Close</button>
        </div>
      </div>
    </div>

    <!-- Quick Apply Confirm Modal -->
    <div v-if="applyModal" class="modal-overlay" @click.self="applyModal = false">
      <div class="modal-card" style="max-width:440px;">
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
          <div v-if="pending?.salary" class="profile-field">
            <span>Salary</span><span>{{ pending.salary }}</span>
          </div>
        </div>
        <div class="form-actions">
          <button class="btn-primary" :disabled="applying || !!applyOk"
            @click="confirmApply(pending)">
            {{ applying ? 'Applying…' : 'Confirm' }}
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
const drives = ref([])
const applications = ref([])
const loading = ref(true)

const search = ref('')
const filterBranch = ref('')
const filterCgpa = ref('')

const detailModal = ref(false)
const applyModal = ref(false)
const applying = ref(false)
const applyError = ref('')
const applyOk = ref('')
const sel = ref({})
const pending = ref(null)

const appliedIds = computed(() => new Set(applications.value.map(a => a.drive_id)))

const filtered = computed(() => {
  let list = drives.value.filter(d => d.status === 'approved')
  const q  = search.value.toLowerCase()
  if (q) list = list.filter(d =>
    d.drive_name?.toLowerCase().includes(q)    ||
    d.company_name?.toLowerCase().includes(q)  ||
    d.job_title?.toLowerCase().includes(q)
  )
  if (filterBranch.value) {
    const fb = filterBranch.value.toLowerCase()
    list = list.filter(d =>
      !d.eligibility_branch ||
      d.eligibility_branch.toLowerCase() === 'any' ||
      d.eligibility_branch.toLowerCase().includes(fb)
    )
  }
  if (filterCgpa.value) {
    list = list.filter(d =>
      !d.eligibility_cgpa || d.eligibility_cgpa <= Number(filterCgpa.value)
    )
  }
  return list
})

const fmtDate = d => d
  ? new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
  : '—'

function resetFilters() {
  search.value = ''; filterBranch.value = ''; filterCgpa.value = ''
}

function viewDrive(d) {
  sel.value = d; applyError.value = ''; applyOk.value = ''; detailModal.value = true
}

function openApply(d) {
  pending.value = d; applyError.value = ''; applyOk.value = ''; applyModal.value = true
}

async function confirmApply(drive) {
  applying.value = true; applyError.value = ''; applyOk.value = ''
  try {
    await api.post('/applications', {
      student_id: store.state.userId,
      drive_id:   drive.id,
    })
    applyOk.value = ' Applied successfully!'
    setTimeout(() => {
      applyModal.value  = false
      detailModal.value = false
      fetchData()
    }, 1200)
  } catch (e) {
    applyError.value = e.message || 'Application failed. Check eligibility.'
  } finally {
    applying.value = false
  }
}

async function fetchData() {
  loading.value = true
  try {
    const [dR, aR] = await Promise.allSettled([
      api.get('/drives'),
      api.get('/applications'),
    ])
    if (dR.status === 'fulfilled') drives.value = dR.value.data || []
    if (aR.status === 'fulfilled') applications.value = aR.value.data || []
  } catch { /* silent */ }
  finally { loading.value = false }
}

onMounted(fetchData)
</script>

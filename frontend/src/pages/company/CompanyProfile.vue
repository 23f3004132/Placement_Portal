<template>
  <div class="user-page">
    <div class="page-header">
      <h2 class="page-title">Company Profile</h2>
    </div>

    <div v-if="success" class="alert-strip success">{{ success }}</div>
    <div v-if="error"   class="alert-strip error">{{ error }}</div>
    <p v-if="loading"   class="loading-text">Loading profile…</p>

    <form v-else class="form-stack" @submit.prevent="save" style="max-width:680px;">
      <h3 class="section-title">Company Information</h3>
      <div class="form-row">
        <div class="form-group">
          <label>Company Name *</label>
          <input v-model="form.company_name" type="text" required placeholder="Google India Pvt. Ltd." />
        </div>
        <div class="form-group">
          <label>Industry</label>
          <input v-model="form.industry" type="text" placeholder="e.g. Technology" />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Location</label>
          <input v-model="form.location" type="text" placeholder="Bangalore, India" />
        </div>
        <div class="form-group">
          <label>Website</label>
          <input v-model="form.website" type="text" placeholder="https://yourcompany.com" />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>HR Contact Person</label>
          <input v-model="form.hr_contact" type="text" placeholder="Priya Mehta" />
        </div>
        <div class="form-group">
          <label>HR Email</label>
          <input v-model="form.hr_email" type="email" placeholder="hr@yourcompany.com" />
        </div>
      </div>
      <div class="form-group">
        <label>Company Description</label>
        <textarea v-model="form.description" rows="4"
          placeholder="Tell students about your company, culture, and what makes you a great employer…"></textarea>
      </div>

      <h3 class="section-title" style="margin-top:.5rem;">Account Security</h3>
      <div class="form-group" style="max-width:320px;">
        <label>New Password <span class="form-hint">(leave blank to keep current)</span></label>
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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import api from '@/utils/api'

const store   = useStore()
const loading = ref(true)
const saving  = ref(false)
const success = ref('')
const error   = ref('')

const form = ref({
  company_name: '', industry: '', location: '', website: '',
  hr_contact: '', hr_email: '', description: '', password: '',
})

async function loadProfile() {
  loading.value = true
  success.value = ''; error.value = ''
  try {
    const r = await api.get(`/companies/${store.state.userId}`)
    const d = r.data || {}
    form.value = {
      company_name: d.company_name || '',
      industry:     d.industry     || '',
      location:     d.location     || '',
      website:      d.website      || '',
      hr_contact:   d.hr_contact   || '',
      hr_email:     d.hr_email     || '',
      description:  d.description  || '',
      password:     '',
    }
  } catch (e) { error.value = 'Could not load profile.' }
  finally { loading.value = false }
}

async function save() {
  saving.value = true; success.value = ''; error.value = ''
  try {
    const payload = { ...form.value }
    if (!payload.password) delete payload.password
    await api.patch(`/companies/${store.state.userId}`, payload)
    success.value = 'Profile updated successfully!'
    form.value.password = ''
  } catch (e) { error.value = e.message || 'Error saving profile.' }
  finally { saving.value = false }
}

onMounted(loadProfile)
</script>

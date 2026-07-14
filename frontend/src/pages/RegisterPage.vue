<template>
  <div class="full-page-center theme-gradient-bg">
    <div class="auth-card auth-card-wide">
      <h1 class="auth-title">Placement Portal</h1>
      <p class="auth-subtitle">Create your account</p>

      <!-- Role Toggle -->
      <div class="role-toggle">
        <button type="button"
          :class="['role-toggle-btn', { active: role === 'student' }]"
          @click="switchRole('student')">Student</button>
        <button type="button"
          :class="['role-toggle-btn', { active: role === 'company' }]"
          @click="switchRole('company')">Company</button>
      </div>

      <div v-if="error"   class="auth-error">{{ error }}</div>
      <div v-if="success" class="auth-success">{{ success }}</div>

      <!-- Student Form -->
      <form v-if="role === 'student'" @submit.prevent="handleRegister">
        <div class="auth-form-group">
          <label>Full Name *</label>
          <input v-model="student.name" type="text" class="auth-field" placeholder="XYZ" required />
        </div>
        <div class="auth-form-group">
          <label>Email Address *</label>
          <input v-model="student.email" type="email" class="auth-field" placeholder="you@example.com" required />
        </div>
        <div class="auth-form-group">
          <label>Password *</label>
          <input v-model="student.password" type="password" class="auth-field" placeholder="••••••••" />
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:.75rem;">
          <div class="auth-form-group">
            <label>Branch *</label>
            <input v-model="student.branch" type="text" class="auth-field" placeholder="CSE" required />
          </div>
          <div class="auth-form-group">
            <label>CGPA *</label>
            <input v-model.number="student.cgpa" type="number" step="0.01" min="0" max="10" class="auth-field" placeholder="8.5" required />
          </div>
          <div class="auth-form-group">
            <label>Year *</label>
            <select v-model.number="student.year" class="auth-field" required>
              <option value="">Select year</option>
              <option v-for="y in [1,2,3,4]" :key="y" :value="y">Year {{ y }}</option>
            </select>
          </div>
          <div class="auth-form-group">
            <label>Contact Number</label>
            <input v-model="student.contact_number" type="tel" class="auth-field" placeholder="+91 1234567890" />
          </div>
        </div>
        <div class="auth-form-group">
          <label>Skills <span style="font-weight:400; font-size:.82rem">(comma-separated)</span></label>
          <input v-model="student.skills" type="text" class="auth-field" placeholder="Python, React, SQL…" />
        </div>
        <div class="auth-form-group">
          <label>Address</label>
          <input v-model="student.address" type="text" class="auth-field" placeholder="City, State" />
        </div>
        <button type="submit" class="auth-submit" :disabled="loading">
          {{ loading ? 'Registering…' : 'Create Student Account' }}
        </button>
      </form>

      <!-- Company Form -->
      <form v-if="role === 'company'" @submit.prevent="handleRegister">
        <div class="auth-form-group">
          <label>Company Name *</label>
          <input v-model="company.company_name" type="text" class="auth-field" placeholder="Google India Pvt. Ltd." required />
        </div>
        <div class="auth-form-group">
          <label>Company Email *</label>
          <input v-model="company.email" type="email" class="auth-field" placeholder="company@gmail.com" required />
        </div>
        <div class="auth-form-group">
          <label>Password *</label>
          <input v-model="company.password" type="password" class="auth-field" placeholder="Min 6 characters" required minlength="6" />
        </div>
        <div class="auth-form-group" style="background:#fff8e1; border-radius:6px; padding:.85rem; font-size:.84rem; color:#856404; margin-bottom:.5rem;">
            Additional company details (HR contact, industry, website, description) can be filled in from your Company Dashboard after registration.
        </div>
        <button type="submit" class="auth-submit" :disabled="loading">
          {{ loading ? 'Registering…' : 'Register Company' }}
        </button>
      </form>

      <p class="auth-footer">
        Already have an account?
        <router-link to="/login">Sign in</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useStore }  from 'vuex'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()
const role = ref('student')
const loading = ref(false)
const error = ref('')
const success = ref('')

const blankStudent = () => ({ name:'', email:'', password:'', branch:'', cgpa:'', year:'', contact_number:'', skills:'', address:'' })
const blankCompany = () => ({ company_name:'', email:'', password:'' })

const student = ref(blankStudent())
const company = ref(blankCompany())

function switchRole(r) {
  role.value = r
  error.value = ''
  success.value = ''
  student.value = blankStudent()
  company.value = blankCompany()
}

async function handleRegister() {
  loading.value = true
  error.value   = ''
  success.value = ''
  try {
    if (role.value === 'student') {
      await store.dispatch('registerStudent', student.value)
      success.value = ' Student account created! You can now log in.'
    } else {
      await store.dispatch('registerCompany', company.value)
      success.value = ' Company registered! Awaiting admin approval. You can log in once approved.'
    }
    setTimeout(() => router.push('/login'), 2500)
  } catch (e) {
    error.value = e.message || 'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

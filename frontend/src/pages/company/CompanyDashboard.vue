<template>
  <div class="user-dashboard">
    <nav class="navbar">
      <div class="navbar-container">
        <span class="navbar-brand"> Placement Portal</span>
        <span class="navbar-welcome">Welcome, {{ store.state.name }}</span>
        <ul class="nav-links">
          <li><router-link to="/company_dashboard/home" class="nav-link">Dashboard</router-link></li>
          <li><router-link to="/company_dashboard/drives" class="nav-link">My Drives</router-link></li>
          <li><router-link to="/company_dashboard/applications" class="nav-link">Applications</router-link></li>
          <li><router-link to="/company_dashboard/profile" class="nav-link">Profile</router-link></li>
          <li><button class="logout-btn nav-link" @click="logout">Logout</button></li>
        </ul>
      </div>
    </nav>
    <div class="user-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { useStore }  from 'vuex'
import { useRouter } from 'vue-router'
const store  = useStore()
const router = useRouter()
function logout() { store.dispatch('logout'); router.push('/login') }
</script>

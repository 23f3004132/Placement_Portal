<template>
  <div class="user-dashboard">
    <nav class="navbar">
      <div class="navbar-container">
        <span class="navbar-brand">Placement Portal</span>
        <span class="navbar-welcome">Welcome, {{ store.state.name }}</span>
        <ul class="nav-links">
          <li><router-link to="/admin_dashboard/home"         class="nav-link">Dashboard</router-link></li>
          <li><router-link to="/admin_dashboard/companies"    class="nav-link">Companies</router-link></li>
          <li><router-link to="/admin_dashboard/students"     class="nav-link">Students</router-link></li>
          <li><router-link to="/admin_dashboard/drives"       class="nav-link">Drives</router-link></li>
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

<template>
  <div class="landing-page theme-gradient-bg">
    <div class="landing-hero">
      <div class="hero-content">
        <h1> Placement Portal</h1>
        <p>Connecting students with top companies for campus placement drives</p>
        <div class="landing-actions">
          <router-link to="/login"    class="landing-btn landing-btn-primary">Login</router-link>
          <router-link to="/register" class="landing-btn landing-btn-secondary">Register</router-link>
        </div>
      </div>
    </div>
    <footer class="site-footer">
      <p>&copy; {{ year }} Placement Portal. All rights reserved.</p>
    </footer>
  </div>
</template>

<script setup>
const year = new Date().getFullYear()
</script>

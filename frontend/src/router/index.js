import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store/userStore'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/pages/HomePage.vue'),
      meta: { title: 'Placement Portal' },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/pages/LoginPage.vue'),
      meta: { title: 'Login' },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/pages/RegisterPage.vue'),
      meta: { title: 'Register' },
    },

    // ── Admin ──────────────────────────────────────────────────
    {
      path: '/admin_dashboard',
      name: 'admin_dashboard',
      component: () => import('@/pages/admin/AdminDashboard.vue'),
      meta: { requiresAuth: true, roles: ['admin'] },
      redirect: '/admin_dashboard/home',
      children: [
        {
          path: 'home',
          name: 'admin_home',
          component: () => import('@/pages/admin/AdminHome.vue'),
          meta: { title: 'Admin Home', requiresAuth: true, roles: ['admin'] },
        },
        {
          path: 'companies',
          name: 'admin_companies',
          component: () => import('@/pages/admin/AdminCompanies.vue'),
          meta: { title: 'Manage Companies', requiresAuth: true, roles: ['admin'] },
        },
        {
          path: 'students',
          name: 'admin_students',
          component: () => import('@/pages/admin/AdminStudents.vue'),
          meta: { title: 'Manage Students', requiresAuth: true, roles: ['admin'] },
        },
        {
          path: 'drives',
          name: 'admin_drives',
          component: () => import('@/pages/admin/AdminDrives.vue'),
          meta: { title: 'Manage Drives', requiresAuth: true, roles: ['admin'] },
        },
      ],
    },

    // ── Company ────────────────────────────────────────────────
    {
      path: '/company_dashboard',
      name: 'company_dashboard',
      component: () => import('@/pages/company/CompanyDashboard.vue'),
      meta: { requiresAuth: true, roles: ['company'] },
      redirect: '/company_dashboard/home',
      children: [
        {
          path: 'home',
          name: 'company_home',
          component: () => import('@/pages/company/CompanyHome.vue'),
          meta: { title: 'Company Home', requiresAuth: true, roles: ['company'] },
        },
        {
          path: 'drives',
          name: 'company_drives',
          component: () => import('@/pages/company/CompanyDrives.vue'),
          meta: { title: 'My Drives', requiresAuth: true, roles: ['company'] },
        },
        {
          path: 'applications',
          name: 'company_applications',
          component: () => import('@/pages/company/CompanyApplications.vue'),
          meta: { title: 'Applications', requiresAuth: true, roles: ['company'] },
        },
        {
          path: 'profile',
          name: 'company_profile',
          component: () => import('@/pages/company/CompanyProfile.vue'),
          meta: { title: 'Company Profile', requiresAuth: true, roles: ['company'] },
        },
      ],
    },

    // ── Student ────────────────────────────────────────────────
    {
      path: '/student_dashboard',
      name: 'student_dashboard',
      component: () => import('@/pages/student/StudentDashboard.vue'),
      meta: { requiresAuth: true, roles: ['student'] },
      redirect: '/student_dashboard/home',
      children: [
        {
          path: 'home',
          name: 'student_home',
          component: () => import('@/pages/student/StudentHome.vue'),
          meta: { title: 'Student Home', requiresAuth: true, roles: ['student'] },
        },
        {
          path: 'drives',
          name: 'student_drives',
          component: () => import('@/pages/student/StudentDrives.vue'),
          meta: { title: 'Browse Drives', requiresAuth: true, roles: ['student'] },
        },
        {
          path: 'applications',
          name: 'student_applications',
          component: () => import('@/pages/student/StudentApplications.vue'),
          meta: { title: 'My Applications', requiresAuth: true, roles: ['student'] },
        },
        {
          path: 'profile',
          name: 'student_profile',
          component: () => import('@/pages/student/StudentProfile.vue'),
          meta: { title: 'My Profile', requiresAuth: true, roles: ['student'] },
        },
      ],
    },
  ],
})

router.beforeEach((to) => {
  if (to.meta?.title) document.title = `${to.meta.title} | Placement Portal`

  if (to.path === '/login') {
    store.dispatch('logout')
    sessionStorage.clear()
  }

  const isAuthenticated = !!store.state.token
  const role            = store.state.role
  const dashboardRoute  = store.getters.dashboardRoute

  if (to.meta?.requiresAuth && !isAuthenticated) return '/login'
  if (to.meta?.roles && !to.meta.roles.includes(role)) {
    return isAuthenticated ? (dashboardRoute || '/') : '/login'
  }
  return true
})

export default router

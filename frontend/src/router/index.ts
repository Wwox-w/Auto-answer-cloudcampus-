import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: () => import('@/views/Dashboard.vue') },
    { path: '/session', name: 'session', component: () => import('@/views/Session.vue') },
    { path: '/config', name: 'config', component: () => import('@/views/Config.vue') },
    { path: '/history', name: 'history', component: () => import('@/views/History.vue') },
  ],
})

export default router

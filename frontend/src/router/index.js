// 文件路径: D:\Code\MangroveProject\frontend\src\router\index.js
import { createRouter, createWebHashHistory } from 'vue-router'

// 路由懒加载
const Login = () => import('../views/Login.vue')
const Dashboard = () => import('../views/Dashboard.vue')
const AdminPanel = () => import('../views/AdminPanel.vue') 
const Tides = () => import('../views/Tides.vue')
const MangroveIntro = () => import('../views/MangroveIntro.vue')

const routes =[
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard },
  { path: '/tides', name: 'Tides', component: Tides },
  { path: '/intro', name: 'MangroveIntro', component: MangroveIntro },
  { 
    path: '/admin', 
    name: 'AdminPanel', 
    component: AdminPanel, 
    meta: { requiresAdmin: true } // 只有管理员能进
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 路由权限拦截守卫
router.beforeEach((to, from, next) => {
  const role = localStorage.getItem('role')
  
  if (to.path === '/login') {
    next()
  } else {
    if (!role) {
      next('/login') // 没登录，踢回登录页
    } else if (to.meta.requiresAdmin && role !== 'admin') {
      alert('权限不足！仅管理员可用。') // 游客想进后台，拦截
      next('/dashboard')
    } else {
      next() // 正常放行
    }
  }
})

export default router
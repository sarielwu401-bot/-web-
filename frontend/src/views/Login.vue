<!-- 文件路径: D:\Code\MangroveProject\frontend\src\views\Login.vue -->
<template>
  <div class="login-wrapper">
    
    <!-- 全局背景层 -->
    <div class="global-bg-gradient"></div>
    <div class="grid-bg"></div>
    
    <!-- 雷达扫描 -->
    <div class="radar-container">
      <div class="radar-circle"></div>
      <div class="radar-scan"></div>
      <div class="radar-dot dot1"></div>
      <div class="radar-dot dot2"></div>
      <div class="radar-dot dot3"></div>
    </div>

    <!-- 左侧：科技展示区 -->
    <div class="left-panel">
      <div class="intro-content">
        
        <h1 class="main-title">红树林生态环境</h1>
        <h2 class="sub-title">大数据智能监测平台</h2>
        <p class="en-title">MANGROVE ECOLOGICAL BIG DATA PLATFORM</p>
        
        <ul class="feature-list">
          <li>
            <el-icon class="f-icon"><Monitor /></el-icon>
            <span>多维环境全天候感知与孪生呈现</span>
          </li>
          <li>
            <el-icon class="f-icon"><Cpu /></el-icon>
            <span>高频设备心跳检测与智能预警</span>
          </li>
          <li>
            <el-icon class="f-icon"><DataAnalysis /></el-icon>
            <span>气象卫星对接与潮汐演变分析</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- 右侧：登录区 -->
    <div class="right-panel">
      <div class="login-box animate-fade-in">
        <div class="box-header">
          <div class="logo-box">
            <el-icon class="logo-icon"><Platform /></el-icon>
          </div>
          <h3>系统登录</h3>
          <p>请输入您的管理员凭证</p>
        </div>

        <el-form ref="loginFormRef" :model="form" :rules="rules" class="login-form" @keyup.enter="handleLogin">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="请输入管理员账号" :prefix-icon="User" size="large" class="custom-input" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="请输入管理员密码" :prefix-icon="Lock" size="large" show-password class="custom-input" />
          </el-form-item>

          <el-form-item style="margin-top: 35px; margin-bottom: 20px;">
            <el-button type="primary" class="login-btn" :loading="loading" @click="handleLogin">
              {{ loading ? '安全验证中...' : '进 入 系 统' }}
            </el-button>
          </el-form-item>

          <div class="guest-login-entry">
            <el-button link class="guest-btn" @click="quickLogin('guest')">
              我是游客，免密浏览数据大屏 <el-icon class="el-icon--right"><Right /></el-icon>
            </el-button>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue' // Vue 工具
import { useRouter } from 'vue-router'// 路由器，负责页面跳转
import { ElMessage } from 'element-plus'// 弹窗工具（提示密码错误等）
import { User, Lock, Monitor, Cpu, DataAnalysis, Platform, Right } from '@element-plus/icons-vue'
import axios from 'axios'// 弹窗工具（提示密码错误等）

const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)
const form = reactive({ username: '', password: '' })
// 2. 准备规则：门卫的初步检查，如果不填就不让发请求
const rules = {
  username:[{ required: true, message: '账号不能为空', trigger: 'blur' }],
  password:[{ required: true, message: '密码不能为空', trigger: 'blur' }]
}

// 2. 准备规则：门卫的初步检查，如果不填就不让发请求
const handleLogin = () => {
  if (!loginFormRef.value) return
  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
                // 【前后端联系的核心】：
        // 门卫(axios)带着 form(账号密码) 去敲后端 Python 的门 (/api/login)
        const res = await axios.post('http://localhost:5000/api/login', form)
             // 如果后端 Python 查了 MySQL 发现账号密码是对的，就会返回 code: 200
        if (res.data.code === 200) {
          // 【发通行证】：把用户名和角色身份（admin或guest）存在浏览器的本地小本本里 (localStorage)
          localStorage.setItem('username', res.data.data.username)
          localStorage.setItem('role', res.data.data.role)
         // 【发通行证】：把用户名和角色身份（admin或guest）存在浏览器的本地小本本里 (localStorage)
          router.push('/dashboard')
        } else { ElMessage.error(res.data.msg) }
      } catch (error) { ElMessage.error('无法连接服务器') } finally { loading.value = false }
    }
  })
}
// 4. 游客快捷登录（一键填充账号密码并直接敲门
const quickLogin = (role) => {
  form.username = 'guest'; form.password = 'guest123'; handleLogin()
}
</script>

<style scoped lang="scss">
.login-wrapper { display: flex; width: 100vw; height: 100vh; overflow: hidden; background-color: #010a0f; position: relative; }
.global-bg-gradient { position: absolute; inset: 0; background: radial-gradient(circle at 30% 50%, #022521 0%, #010a0f 80%); z-index: 0; }
.grid-bg { position: absolute; inset: 0; background-image: linear-gradient(rgba(0, 210, 255, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 210, 255, 0.05) 1px, transparent 1px); background-size: 30px 30px; z-index: 1; }

.radar-container { position: absolute; left: 45%; top: 50%; transform: translate(-50%, -50%); width: 600px; height: 600px; z-index: 2; opacity: 0.5; }
.radar-circle { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 1px dashed rgba(0, 255, 157, 0.3); }
.radar-scan { position: absolute; width: 50%; height: 50%; top: 0; right: 0; background: conic-gradient(from 90deg at 0 100%, transparent 0deg, rgba(0, 255, 157, 0.6) 90deg, transparent 90deg); border-radius: 0 100% 0 0; transform-origin: 0 100%; animation: radarSpin 4s linear infinite; }
@keyframes radarSpin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.radar-dot { position: absolute; width: 8px; height: 8px; background: #00d2ff; border-radius: 50%; box-shadow: 0 0 10px #00d2ff; animation: dotPulse 2s infinite alternate; }
.dot1 { top: 30%; left: 20%; } .dot2 { top: 60%; left: 70%; background: #00ff9d; animation-delay: 0.5s;} .dot3 { top: 75%; left: 40%; animation-delay: 1s;}
@keyframes dotPulse { 0% { transform: scale(1); opacity: 0.5; } 100% { transform: scale(2); opacity: 1; } }
/* 呼吸动画：从小变大，从半透明变不透明 */
/* 核心优化部分 */
.left-panel { flex: 6; position: relative; display: flex; align-items: center; z-index: 10; }
.intro-content {
  margin-left: 250px; /* 关键修改：向右靠拢 */
  .badge { display: inline-block; padding: 5px 12px; background: rgba(0, 255, 157, 0.1); border: 1px solid #00ff9d; color: #00ff9d; font-size: 14px; border-radius: 4px; margin-bottom: 20px; }
  .main-title { font-size: 60px; margin: 0; font-weight: bold; letter-spacing: 4px; color: #fff; }
  .sub-title { font-size: 60px; margin: 0 0 15px 0; font-weight: bold; letter-spacing: 4px; background: linear-gradient(90deg, #fff, #00ff9d); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .en-title { font-size: 16px; color: #6a8c9e; letter-spacing: 3px; margin-bottom: 40px; }
  .feature-list { list-style: none; padding: 0; margin: 0;
    li { display: flex; align-items: center; gap: 15px; margin-bottom: 25px; font-size: 18px; color: #d0e0e3; 
      .f-icon { font-size: 24px; color: #00d2ff; padding: 10px; background: rgba(0, 210, 255, 0.1); border-radius: 8px; border: 1px solid rgba(0, 210, 255, 0.3); }
    }
  }
}
//毛玻璃
.right-panel { flex: 4; display: flex; justify-content: center; align-items: center; z-index: 10; }
.login-box {
  width: 420px; padding: 50px 45px;
  background: rgba(4, 30, 40, 0.65); backdrop-filter: blur(15px);
  border: 1px solid rgba(0, 255, 157, 0.25); border-radius: 20px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
}
.box-header { text-align: center; margin-bottom: 40px; .logo-box { width: 60px; height: 60px; margin: 0 auto 15px; background: linear-gradient(135deg, rgba(0,255,157,0.2), rgba(0,210,255,0.2)); border-radius: 16px; border: 1px solid rgba(0,255,157,0.5); display: flex; justify-content: center; align-items: center; .logo-icon { font-size: 32px; color: #00ff9d; } } h3 { font-size: 24px; color: #fff; margin: 0 0 10px 0; } p { color: #5a7b8e; font-size: 14px; } }
.login-form { :deep(.el-input__wrapper) { background-color: rgba(0, 0, 0, 0.4); box-shadow: 0 0 0 1px #1a3c42 inset; border-radius: 8px; height: 48px; } :deep(.el-input__inner) { color: #fff; } }
.login-btn { width: 100%; height: 50px; font-size: 16px; font-weight: bold; border-radius: 8px; border: none; background: linear-gradient(90deg, #009688, #00ff9d); color: #01151a; }
.guest-login-entry { text-align: center; margin-top: 10px; .guest-btn { font-size: 14px; color: #00d2ff; } }
.animate-fade-in { animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
@keyframes fadeInUp { 0% { opacity: 0; transform: translateY(30px); } 100% { opacity: 1; transform: translateY(0); } }
</style>
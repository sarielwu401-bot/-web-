// 文件路径: D:\Code\MangroveProject\frontend\src\main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// 引入 Element Plus 及图标
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 引入 Leaflet 地图核心样式
import 'leaflet/dist/leaflet.css'

const app = createApp(App)

// 注册 Element Plus 的所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus)
app.use(router)

app.mount('#app')
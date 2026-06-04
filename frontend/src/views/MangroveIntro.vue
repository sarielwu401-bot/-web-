<!-- 文件路径: D:\Code\MangroveProject\frontend\src\views\MangroveIntro.vue -->
<template>
  <div class="intro-wrapper">
    <!-- 悬浮顶部导航 -->
    <header class="fixed-header">
      <div class="header-left">
        <el-button link icon="ArrowLeft" class="back-btn" @click="$router.push('/dashboard')">
          返回数据大屏
        </el-button>
      </div>
      <div class="header-right">
        <span class="logo-text">红树林生态展厅</span>
        <span class="pulse-dot"></span>
      </div>
    </header>

    <!-- 全屏沉浸式轮播 -->
       <!-- height="100vh" 意思是高度占满整个屏幕，interval="6000" 意思是6秒钟自动翻页 -->
    <el-carousel 
      height="100vh" 
      :interval="6000" 
      arrow="always" 
      indicator-position="outside"
      class="full-carousel"
    >
      <el-carousel-item v-for="(slide, index) in slideList" :key="index">
        <!-- 背景图片层 -->
        <div class="slide-bg" :style="{ backgroundImage: `url(${slide.image})` }">
          
          <!-- 暗色渐变遮罩 (确保文字清晰，增加深邃感) -->
          <div class="dark-overlay"></div>

          <!-- 玻璃拟态内容卡片 -->
          <div class="glass-card animate-fade-up">
            <div class="card-header">
              <span class="slide-num">0{{ index + 1 }}</span>
              <span class="slide-subtitle">{{ slide.subtitle }}</span>
            </div>
            <h1 class="slide-title">{{ slide.title }}</h1>
            <div class="tech-divider"></div>
            <p class="slide-desc">{{ slide.desc }}</p>
            
            <div class="tags-container">
              <span v-for="(tag, tIdx) in slide.tags" :key="tIdx" class="tech-tag">
                <i class="glow-point"></i> {{ tag }}
              </span>
            </div>
          </div>

        </div>
      </el-carousel-item>
    </el-carousel>
  </div>
</template>

<script setup>
import { ref } from 'vue'// Vue 的核心工具
import { useRouter } from 'vue-router'// 路由器，用来点击返回大屏
import { ArrowLeft } from '@element-plus/icons-vue'

const router = useRouter() // 拿到路由控制权

// ================= 幻灯片内容配置 =================

// 把下方的 image 值改为 '/bg1.jpg' 即可
const slideList = ref([
  {
    subtitle: 'COASTAL GUARDIAN',
    title: '海岸卫士：抵御风浪的绿色长城',
    desc: '红树林生长在热带、亚热带海岸潮间带，其盘根错节的发达根系深深扎入淤泥，能有效地滞留陆地来沙，减少近岸海域的含沙量。茂密高大的枝体宛如一道道绿色屏障，有效抵御台风和海啸的袭击，保护海岸线免受侵蚀。',
    tags:['消浪护岸', '净化海水', '促淤造陆'],
    image: '/bg4.png'
  },
  {
    subtitle: 'BLUE CARBON',
    title: '蓝碳宝库：高效的碳封存机器',
    desc: '作为三大蓝碳生态系统之一，红树林是地球上固碳效率最高的生态系统之一。虽然其面积仅占全球沿海面积的极少部分，但其碳埋藏率却占全球海洋沉积物碳埋藏总量的 10%-15%。保护红树林对于缓解全球气候变暖具有不可替代的作用。',
    tags:['碳中和', '气候变化', '底泥固碳'],
    image: '/bg2.jpg'
  },
  {
    subtitle: 'BIODIVERSITY',
    title: '生物天堂：极高的生物多样性',
    desc: '这里是无数海洋生物和鸟类的理想家园。底栖动物（如招潮蟹、弹涂鱼）在泥滩上通过生物扰动促进物质循环；每年数以万计的候鸟（如黑脸琵鹭）在此越冬觅食。发达的根系更是海洋鱼虾最天然的“育儿所”和避难所。',
    tags:['招潮蟹', '黑脸琵鹭', '生态繁育', '物质循环'],
    image: '/bg3.png'
  },
  
])
</script>

<style scoped lang="scss">
.intro-wrapper {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background-color: #000;
  position: relative;
}

/* ================= 悬浮顶部导航 ================= */
.fixed-header {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 80px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  z-index: 999;
  background: linear-gradient(180deg, rgba(0, 15, 20, 0.9) 0%, rgba(0, 0, 0, 0) 100%);
  
  .back-btn {
    font-size: 16px;
    color: #00d2ff;
    font-weight: bold;
    text-shadow: 0 0 10px rgba(0, 210, 255, 0.5);
    transition: 0.3s;
    &:hover { color: #00ff9d; transform: translateX(-5px); }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 15px;
    
    .logo-text {
      font-size: 18px;
      color: #fff;
      letter-spacing: 2px;
      font-weight: bold;
    }

    .pulse-dot {
      width: 10px; height: 10px;
      background-color: #00ff9d;
      border-radius: 50%;
      box-shadow: 0 0 10px #00ff9d;
      animation: pulse 1.5s infinite;
    }
  }
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.5); opacity: 0.5; }
  100% { transform: scale(1); opacity: 1; }
}

/* ================= 全屏轮播与遮罩 ================= */
.full-carousel {
  width: 100%; height: 100%;
}

.slide-bg {
  width: 100%; height: 100%;
  background-size: cover;
  background-position: center;
  position: relative;
  display: flex;
  align-items: center;
  padding-left: 10vw; /* 让卡片偏左显示，留出右侧的风景视觉空间 */
}


/* ================= 玻璃拟态数据卡片 ================= */
.glass-card {
  position: relative;
  z-index: 2;
  width: 650px;
  padding: 50px;
  background: rgba(4, 30, 45, 0.3); 
  backdrop-filter: blur(15px);      /* 毛玻璃核心代码 */
  -webkit-backdrop-filter: blur(15px);
  border: 1px solid rgba(0, 210, 255, 0.2);
  border-left: 4px solid #00ff9d;   
  border-radius: 4px 20px 20px 4px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  color: #fff;
}

/* 卡片排版 */
.card-header {
  display: flex; align-items: baseline; gap: 15px; margin-bottom: 10px;
  
  .slide-num {
    font-size: 32px; font-weight: bold; color: #00d2ff;
    font-family: 'Arial Black', sans-serif;
  }
  .slide-subtitle {
    font-size: 14px; color: #8fa3ad; letter-spacing: 3px; font-weight: bold;
  }
}

.slide-title {
  font-size: 36px;
  font-weight: bold;
  margin: 0 0 20px 0;
  color: #fff;
  text-shadow: 0 2px 10px rgba(0,0,0,0.8);
}

.tech-divider {
  width: 60px; height: 4px; background: #00ff9d; margin-bottom: 30px;
  box-shadow: 0 0 10px #00ff9d;
}

.slide-desc {
  font-size: 16px; line-height: 2; color: #d0e0e3;
  text-align: justify; margin-bottom: 40px;
  text-shadow: 0 1px 3px rgba(0,0,0,0.8);
}

/* 底部发光标签 */
.tags-container {
  display: flex; gap: 15px; flex-wrap: wrap;
  
  .tech-tag {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 16px;
    background: rgba(0, 210, 255, 0.1);
    border: 1px solid rgba(0, 210, 255, 0.3);
    border-radius: 20px;
    color: #e0f7fa; font-size: 13px; font-weight: bold;
    
    .glow-point {
      width: 6px; height: 6px; border-radius: 50%;
      background: #00ff9d; box-shadow: 0 0 5px #00ff9d;
    }
  }
}

/* ================= 动画特效 ================= */
.animate-fade-up {
  animation: fadeUp 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fadeUp {
  0% { opacity: 0; transform: translateY(50px); }
  100% { opacity: 1; transform: translateY(0); }
}

/* ================= 覆盖 ElementUI 轮播组件样式 ================= */
:deep(.el-carousel__arrow) {
  background-color: rgba(0, 210, 255, 0.1);
  border: 1px solid rgba(0, 210, 255, 0.3);
  font-size: 24px; width: 60px; height: 60px;
  transition: 0.3s;
  &:hover { background-color: rgba(0, 255, 157, 0.2); color: #00ff9d; border-color: #00ff9d; }
}

:deep(.el-carousel__indicators--outside) {
  position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%);
}

:deep(.el-carousel__indicator .el-carousel__button) {
  width: 30px; height: 4px; background-color: rgba(255,255,255,0.3); border-radius: 2px;
}
:deep(.el-carousel__indicator.is-active .el-carousel__button) {
  background-color: #00ff9d; width: 50px; box-shadow: 0 0 10px #00ff9d;
}
</style>
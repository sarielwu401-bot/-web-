<!-- 文件路径: D:\Code\MangroveProject\frontend\src\views\Tides.vue -->
<template>
  <div class="screen-container">
    
    <!-- ================= 1. 驾驶舱式炫酷顶部导航 ================= -->
    <header class="cockpit-header">
      <div class="header-flank left-flank">
        <el-button link icon="ArrowLeft" class="back-btn" @click="$router.push('/dashboard')">
          返回数据大屏
        </el-button>
      </div>
      
      <div class="header-center">
        <div class="center-bg">
          <h1 class="main-title">潮汐预报与赶海分析系统</h1>
        </div>
      </div>
      
      <div class="header-flank right-flank">
        <!-- 地点选择 -->
        <el-select 
          v-model="currentLocation" 
          class="custom-select" 
          popper-class="custom-dark-select"
          style="width: 150px; margin-right: 15px;" 
          @change="fetchData"
        >
          <el-option 
            v-for="loc in locationList" 
            :key="loc.location_id" 
            :label="loc.name" 
            :value="loc.location_id" 
          />
        </el-select>
        
        <!-- 日期选择 -->
        <el-date-picker
          v-model="displayDate"
          type="date"
          class="custom-select"
          popper-class="custom-dark-select"
          style="width: 140px;"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          :disabled-date="disabledDate"
          :clearable="false"
          @change="fetchData"
        />
        
        <el-button type="primary" icon="Refresh" circle class="refresh-btn" style="margin-left: 20px; margin-right: 25px;" @click="fetchData" :loading="loading" />
        
        <!-- ================= 【新增】右上角用户控制下拉菜单 ================= -->
        <el-dropdown @command="handleCommand" trigger="hover" placement="bottom-end">
          <span class="user-box el-dropdown-link">
            <img src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" class="avatar" />
            <span class="username">{{ username }}</span>
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu class="dark-dropdown">
              <el-dropdown-item v-if="isAdmin" command="admin" class="admin-item">
                <el-icon><Setting /></el-icon>管理面板
              </el-dropdown-item>
              <el-dropdown-item command="logout" class="logout-item" divided>
                <el-icon><SwitchButton /></el-icon>安全注销
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- ================= 2. 主体大屏布局 ================= -->
    <main class="screen-main" v-loading="loading" element-loading-background="rgba(1, 11, 18, 0.9)" element-loading-text="正在通过专线网关连接气象卫星...">
      
      <!-- 顶部：潮汐曲线图 -->
      <section class="panel-top">
        <div class="tech-box">
          <div class="flow-lines"><span class="line top"></span><span class="line right"></span><span class="line bottom"></span><span class="line left"></span></div>
          <div class="box-title">
            <span>{{ displayDate }} 全天 24 小时潮汐演变曲线</span>
            <div class="legend">
              <span class="dot blue"></span> 潮汐高度 (cm)
              <span class="dot yellow"></span> 推荐赶海时段
            </div>
          </div>
          <div id="tide-chart" class="chart-content"></div>
          <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
        </div>
      </section>

      <!-- 底部：极值表与智能建议 -->
      <section class="panel-bottom">
        <!-- 左侧：潮汐极值表 -->
        <div class="tech-box bottom-box">
          <div class="flow-lines"><span class="line top"></span><span class="line right"></span><span class="line bottom"></span><span class="line left"></span></div>
          <div class="box-title">潮汐极值时刻表</div>
          <el-table :data="tideTable" class="custom-table" height="100%">
            <el-table-column label="潮况" width="120">
              <template #default="scope">
                <el-tag :type="scope.row.type === '满潮' ? 'danger' : 'success'" effect="dark" class="tide-tag">
                  {{ scope.row.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="time" label="预报时间 (HH:MM)" />
            <el-table-column prop="height" label="预报潮高 (cm)" />
          </el-table>
          <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
        </div>

        <!-- 右侧：AI 赶海建议 -->
        <div class="tech-box bottom-box recommend-box">
          <div class="flow-lines"><span class="line top"></span><span class="line right"></span><span class="line bottom"></span><span class="line left"></span></div>
          <div class="box-title" style="color: #ffeb3b; border-left-color: #ffeb3b;">
            最佳赶海时间
          </div>
          <div class="recommend-content scroll-bar">
            <template v-if="bestTimes && bestTimes.length > 0">
              <div class="time-block" v-for="(time, index) in bestTimes" :key="index">
              
                <div class="text">
                  <div class="range">{{ time.start }} - {{ time.end }}</div>
                  <div class="desc">依据退潮规律测算：干潮最低点前 2 小时为极佳赶海时机！</div>
                </div>
              </div>
            </template>
            <template v-else>
              <div class="empty-block">
                <el-icon :size="40" color="#8fa3ad"><Warning /></el-icon>
                <p>今日全天潮水偏高或该地暂无有效数据，请注意人身安全。</p>
              </div>
            </template>
            <div class="tips">
              <p>严格禁令：推荐时段结束后即开始涨潮，请务必立即撤离至岸上安全地带！</p>
              <p>数据节点：由和风天气海洋气象企业商业专线 API 提供数据支撑</p>
            </div>
          </div>
          <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
        </div>
      </section>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Refresh, ArrowLeft, Warning, ArrowDown, Setting, SwitchButton } from '@element-plus/icons-vue'

// 【新增】：获取路由及本地用户信息状态
const router = useRouter()
const username = localStorage.getItem('username') || 'Guest'
const isAdmin = localStorage.getItem('role') === 'admin'

const lowTideThreshold = 130; 
const currentLocation = ref('') 
const locationList = ref([]) 

const getTodayStr = () => {
  const d = new Date()
  return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`
}

const displayDate = ref(getTodayStr())
const loading = ref(false)
const tideTable = ref([]) 
const bestTimes = ref([])
let chartInstance = null

const disabledDate = (time) => {
  return time.getTime() < new Date(new Date().setHours(0, 0, 0, 0)).getTime()
}

// 【新增】：用户下拉菜单的操作流转
const handleCommand = (command) => {
  if (command === 'admin') router.push('/admin')
  else if (command === 'logout') { localStorage.clear(); router.push('/login') }
}
// 1. 获取赶海地点下拉框字典
const fetchLocations = async () => {
  try {
      // 向自己的后端要地点列表（深圳湾、大梅沙等），这些数据存在 MySQL 的 tb_tide_location 表里
    const res = await axios.get('http://localhost:5000/api/tide_locations')
    if (res.data.code === 200 && res.data.data.length > 0) {
      locationList.value = res.data.data// 存到下拉框里
      currentLocation.value = locationList.value[0].location_id 
      fetchData() 
    } else {
      ElMessage.error('数据库中尚未配置任何赶海地点')
    }
  } catch(e) {
    ElMessage.error('获取赶海地点列表失败，请检查数据库连接')
  }
}

const fetchData = async () => {
  if (!currentLocation.value) return; 
  
  loading.value = true
  try {
    const dateApi = displayDate.value.replace(/-/g, '')
      // 【核心】：前端不去求和风天气，而是去求自己的 Python 后端（/api/proxy/tide）
    const url = `http://localhost:5000/api/proxy/tide?location=${currentLocation.value}&date=${dateApi}`
    
    const res = await axios.get(url)
    
     // 从返回的 JSON 数据中，把“每小时潮水数据”和“满潮干潮极值数据”剥离出来
    const hourlyData = res.data.tideHourly || res.data.tide ||[]
    const officialTableData = res.data.tideTable ||[]
  // 交给处理函数去画图
    if (res.data.code === '200' && hourlyData.length > 0) {
      processAndRender(hourlyData, officialTableData)
      ElMessage.success('卫星潮汐气象数据拉取成功')
    } else {
      ElMessage.warning(`该位置暂无潮汐观测数据，请尝试切换其他主流港口`)
      clearData()
    }
  } catch (error) {
    console.error("前端请求报错:", error)
    ElMessage.error('无法连接到本地 Python 代理服务器，请检查后端是否启动')
    clearData()
  } finally {
    loading.value = false
  }
}

const clearData = () => {
  tideTable.value = []
  bestTimes.value =[]
  if (chartInstance) {
    chartInstance.clear() 
  }
}

const processAndRender = (hourlyData, officialTableData) => {
  if (!hourlyData || hourlyData.length === 0) {
    clearData()
    return
  }
// 1. 数据洗洗干净，转成厘米
// 遍历24小时数据，把时间(比如14:00)抽出来做X轴，把高度乘100变成厘米做Y轴
  const xData = hourlyData.map(item => item.fxTime.substring(11, 16))
  const yData = hourlyData.map(item => Math.round(parseFloat(item.height) * 100))

  if (officialTableData && officialTableData.length > 0) {
    tideTable.value = officialTableData.map(item => ({
      type: item.type === 'H' ? '满潮' : '干潮',
      time: item.fxTime.substring(11, 16),
      height: Math.round(parseFloat(item.height) * 100)
    }))
  } else {
    const peaks =[]
    for (let i = 1; i < yData.length - 1; i++) {
      if (yData[i] >= yData[i-1] && yData[i] >= yData[i+1]) {
        if (peaks.length === 0 || peaks[peaks.length-1].type !== '满潮') {
          peaks.push({ type: '满潮', time: xData[i], height: yData[i] })
        }
      }
      if (yData[i] <= yData[i-1] && yData[i] <= yData[i+1]) {
        if (peaks.length === 0 || peaks[peaks.length-1].type !== '干潮') {
          peaks.push({ type: '干潮', time: xData[i], height: yData[i] })
        }
      }
    }
    tideTable.value = peaks
  }

  // 2. 核心算法：找最安全的干潮点
// 设定安全线 lowTideThreshold = 130 (130厘米)
// 从极值表里，把所有类型是“干潮”，且高度低于 130cm 的点过滤出来
  bestTimes.value =[]
  let start = null
  const safeLowTides = tideTable.value.filter(item => item.type === '干潮' && item.height <= lowTideThreshold)
// 3. 核心算法：逆向推算赶海时间窗
  safeLowTides.forEach(lt => {
    
    let closestIdx = -1;
    let minDiff = 99999;
    
    const[ltH, ltM] = lt.time.split(':').map(Number);
    const ltMinutes = ltH * 60 + ltM;

    xData.forEach((timeStr, idx) => {
      const[h, m] = timeStr.split(':').map(Number);
      const tMinutes = h * 60 + m;
      const diff = Math.abs(tMinutes - ltMinutes);
      if (diff < minDiff) {
        minDiff = diff;
        closestIdx = idx;
      }
    });

    if (closestIdx !== -1) {
      // 找到这个干潮点在 X轴 数组里是第几个（假设是第 16 个索引）
      let endIdx = closestIdx;
      // 保留你的改动：往前推算 2 个小时
      let startIdx = Math.max(0, endIdx - 2);
    // 把推算好的开始时间和结束时间，存进 bestTimes 数组里
      if (startIdx < endIdx) {
        bestTimes.value.push({
          start: xData[startIdx],
          end: xData[endIdx]
        });
      }
    }
  });

  renderChart(xData, yData)
}

const renderChart = (xData, yData) => {
  nextTick(() => {
    const chartDom = document.getElementById('tide-chart')
    if (!chartDom || chartDom.clientWidth === 0) return
    
    if (!chartInstance) {
      chartInstance = echarts.init(chartDom)
    }
    // 1. 画背景高亮块（MarkArea）
// 刚才算出的 bestTimes 数组，转换成 ECharts 认识的色块格式
    const markAreaData = bestTimes.value.map(t => {
      return[
        { xAxis: t.start, itemStyle: { color: 'rgba(255, 235, 59, 0.15)' } },
        { xAxis: t.end }
      ]
    })

    const option = {
      grid: { left: '4%', right: '4%', bottom: '8%', top: '15%', containLabel: true },
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(0,15,25,0.9)',
        borderColor: '#00d2ff',
        textStyle: { color: '#fff' },
        formatter: (params) => {
          const h = params[0].value
          let tip = `<b style="color:#00d2ff">${params[0].name}</b><br/>潮汐高度: <b style="font-size:16px">${h}</b> cm<br/>`
          if (h <= lowTideThreshold) tip += `<span style="color:#ffeb3b; margin-top:5px; display:inline-block;">极佳赶海时机</span>`
          return tip
        }
      },
      xAxis: {
        type: 'category', boundaryGap: false, data: xData,
        axisLine: { lineStyle: { color: '#1a3c5a' } },
        axisLabel: { color: '#8fa3ad', interval: 2 } 
      },
      yAxis: {
        type: 'value', name: '潮高 (cm)', nameTextStyle: { color: '#8fa3ad', padding:[0, 0, 0, 20] },
        splitLine: { lineStyle: { color: 'rgba(0, 210, 255, 0.1)', type: 'dashed' } },
        axisLabel: { color: '#8fa3ad' }
      },
      series:[
        {
          name: '潮汐高度', type: 'line', smooth: true, symbol: 'circle', symbolSize: 4, showSymbol: false,
          lineStyle: { width: 3, color: '#00d2ff', shadowColor: '#00d2ff', shadowBlur: 10 },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1,[
              { offset: 0, color: 'rgba(0, 210, 255, 0.5)' },
              { offset: 1, color: 'rgba(0, 210, 255, 0.0)' }
            ])
          },
          data: yData,
          markArea: { data: markAreaData, label: { show: true, position: 'insideTop', color: '#ffeb3b', formatter: '推荐\n赶海', distance: 10 } },
          markPoint: {
            symbol: 'pin', symbolSize: 40, label: { color: '#fff', fontSize: 10 },
            data:[
              { type: 'max', name: '最高水位', itemStyle: { color: '#ff5252' } },
              { type: 'min', name: '最低水位', itemStyle: { color: '#00ff9d' } }
            ]
          }
        }
      ]
    }
    chartInstance.setOption(option, true) 
  })
}

onMounted(() => {
  fetchLocations()
  window.addEventListener('resize', () => chartInstance?.resize())
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped lang="scss">
.screen-container {
  width: 100vw; height: 100vh; overflow: hidden; background-color: #020d14; 
  background-image: radial-gradient(circle at 50% 50%, rgba(0, 210, 255, 0.05) 0%, transparent 60%), linear-gradient(0deg, rgba(0,0,0,0.8) 0%, transparent 100%);
  color: #fff; display: flex; flex-direction: column;
}

.cockpit-header {
  height: 80px; display: flex; justify-content: space-between; align-items: flex-start;
  position: relative; z-index: 100;
  background: url('data:image/svg+xml;utf8,<svg width="100%" height="80" xmlns="http://www.w3.org/2000/svg"><line x1="0" y1="35" x2="30%" y2="35" stroke="%2300d2ff" stroke-width="2"/><line x1="30%" y1="35" x2="33%" y2="75" stroke="%2300d2ff" stroke-width="2"/><line x1="33%" y1="75" x2="67%" y2="75" stroke="%2300d2ff" stroke-width="2"/><line x1="67%" y1="75" x2="70%" y2="35" stroke="%2300d2ff" stroke-width="2"/><line x1="70%" y1="35" x2="100%" y2="35" stroke="%2300d2ff" stroke-width="2"/></svg>') no-repeat top center;
  
  .header-flank { width: 32%; height: 35px; display: flex; align-items: center; padding: 0 30px; background: rgba(0, 30, 50, 0.4); }
  .left-flank { justify-content: flex-start; .back-btn { font-size: 16px; color: #00d2ff; font-weight: bold; transition: 0.3s; &:hover { color: #00ff9d; text-shadow: 0 0 8px #00ff9d; } } }
  
  .header-center {
    width: 36%; height: 75px; display: flex; justify-content: center; align-items: center;
    background: radial-gradient(ellipse at bottom, rgba(0, 210, 255, 0.3) 0%, transparent 70%);
    .main-title { font-size: 30px; font-weight: bold; margin: 0; padding-bottom: 10px; color: #fff; text-shadow: 0 0 10px #00d2ff, 0 0 20px #00ff9d; letter-spacing: 5px; }
  }

  .right-flank { 
    display: flex; align-items: center; justify-content: flex-end; 
    
    /* 【新增】用户区域样式 */
    .el-dropdown-link { 
      display: flex; align-items: center; gap: 10px; cursor: pointer; color: #fff; margin-left: 10px;
      .avatar { width: 28px; height: 28px; border-radius: 50%; border: 1px solid #00ff9d; } 
      .username { font-size: 15px; color: #e0f7fa;} 
    }
  }
}

.screen-main { flex: 1; display: flex; flex-direction: column; padding: 15px; gap: 15px; }
.panel-top { flex: 1.5; display: flex; }
.panel-bottom { flex: 1; display: flex; gap: 15px; }

.tech-box {
  flex: 1; background: rgba(0, 30, 45, 0.6); border: 1px solid rgba(0, 210, 255, 0.2);
  position: relative; padding: 15px; display: flex; flex-direction: column;
  box-shadow: inset 0 0 20px rgba(0, 210, 255, 0.05);

  .box-title {
    font-size: 16px; font-weight: bold; color: #00ff9d; padding-left: 10px; border-left: 4px solid #00d2ff;
    margin-bottom: 15px; text-shadow: 0 0 5px rgba(0, 255, 157, 0.5);
    display: flex; justify-content: space-between; align-items: center;
    
    .legend {
      font-size: 12px; color: #8fa3ad; font-weight: normal; text-shadow: none;
      .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin: 0 5px 0 15px; }
      .blue { background: #00d2ff; box-shadow: 0 0 5px #00d2ff; }
      .yellow { background: #ffeb3b; box-shadow: 0 0 5px #ffeb3b; }
    }
  }

  .chart-content { flex: 1; width: 100%; min-height: 250px; }
  
  .corner { position: absolute; width: 15px; height: 15px; border: 2px solid #00d2ff; }
  .tl { top: -1px; left: -1px; border-right: none; border-bottom: none; }
  .tr { top: -1px; right: -1px; border-left: none; border-bottom: none; }
  .bl { bottom: -1px; left: -1px; border-right: none; border-top: none; }
  .br { bottom: -1px; right: -1px; border-left: none; border-top: none; }
  
  .flow-lines { position: absolute; inset: 0; overflow: hidden; border-radius: inherit; pointer-events: none; z-index: 1; }
  .line { position: absolute; background: linear-gradient(90deg, transparent, #00d2ff); }
  .top { top: 0; left: -100%; width: 100%; height: 2px; animation: flowTop 3s linear infinite; }
  .right { top: -100%; right: 0; width: 2px; height: 100%; background: linear-gradient(180deg, transparent, #00d2ff); animation: flowRight 3s linear infinite; animation-delay: 0.75s; }
  .bottom { bottom: 0; right: -100%; width: 100%; height: 2px; background: linear-gradient(270deg, transparent, #00d2ff); animation: flowBottom 3s linear infinite; animation-delay: 1.5s; }
  .left { bottom: -100%; left: 0; width: 2px; height: 100%; background: linear-gradient(360deg, transparent, #00d2ff); animation: flowLeft 3s linear infinite; animation-delay: 2.25s; }
}

@keyframes flowTop { 50%, 100% { left: 100%; } } @keyframes flowRight { 50%, 100% { top: 100%; } } @keyframes flowBottom { 50%, 100% { right: 100%; } } @keyframes flowLeft { 50%, 100% { bottom: 100%; } }

.bottom-box { flex: 1; min-width: 0; overflow: hidden; }

:deep(.custom-table) {
  background-color: transparent !important;
  --el-table-border-color: rgba(0, 210, 255, 0.1); --el-table-header-bg-color: rgba(0, 210, 255, 0.1);
  --el-table-header-text-color: #00d2ff; --el-table-tr-bg-color: transparent; --el-table-row-hover-bg-color: rgba(0, 255, 157, 0.1);
  color: #fff; border: 1px solid rgba(0, 210, 255, 0.2); border-radius: 4px;
}
:deep(.el-table th.el-table__cell) { background-color: rgba(0, 210, 255, 0.05) !important; }
:deep(.el-table tr) { background-color: transparent !important; }
:deep(.el-table td.el-table__cell) { border-bottom: 1px solid rgba(0, 210, 255, 0.1); }
:deep(.el-table::before) { display: none; }
.tide-tag { font-weight: bold; width: 70px; text-align: center; }

.recommend-content {
  flex: 1; overflow-y: auto; padding-right: 10px; position: relative; z-index: 2; margin-top: 15px; padding-left: 15px;
  
  .time-block {
    display: flex; align-items: center; background: rgba(255, 235, 59, 0.05);
    padding: 15px; border-radius: 4px; margin-bottom: 12px; border-left: 4px solid #ffeb3b; transition: 0.3s;
    &:hover { background: rgba(255, 235, 59, 0.15); transform: translateX(5px); }
    .icon { font-size: 28px; margin-right: 15px; }
    .text { .range { font-size: 18px; font-weight: bold; color: #ffeb3b; letter-spacing: 1px; } .desc { font-size: 13px; color: #8fa3ad; margin-top: 5px; } }
  }

  .empty-block { text-align: center; padding: 30px 10px; color: #8fa3ad; p { margin-top: 10px; font-size: 14px; } }
  .tips { margin-top: 15px; padding-top: 15px; border-top: 1px dashed rgba(255,255,255,0.1); font-size: 12px; color: #666; line-height: 1.8; margin-right: 10px; }
}

:deep(.custom-select .el-input__wrapper), :deep(.custom-date .el-input__wrapper) {
  background-color: rgba(0, 30, 45, 0.8) !important; box-shadow: 0 0 0 1px #00d2ff inset !important;
}
:deep(.custom-select .el-input__inner), :deep(.custom-date .el-input__inner) { color: #00ff9d !important; font-weight: bold; }

.scroll-bar::-webkit-scrollbar { width: 6px; }
.scroll-bar::-webkit-scrollbar-thumb { background: rgba(0, 210, 255, 0.5); border-radius: 3px; }
.scroll-bar::-webkit-scrollbar-track { background: rgba(0, 0, 0, 0.2); }
</style>

<!-- 注入全局暗黑下拉菜单样式 -->
<style>
.dark-dropdown { background-color: #021a24 !important; border: 1px solid #00d2ff !important; }
.dark-dropdown .el-dropdown-menu__item { color: #fff !important; font-size: 14px !important; padding: 12px 20px !important; }
.dark-dropdown .el-dropdown-menu__item:hover { background-color: rgba(0, 210, 255, 0.2) !important; color: #00d2ff !important; }
.dark-dropdown .admin-item { color: #00ff9d !important; } .dark-dropdown .logout-item { color: #ff5252 !important; }

.custom-dark-select { background-color: #02121d !important; border: 1px solid #00d2ff !important; }
.custom-dark-select .el-select-dropdown__item { color: #8fa3ad !important; font-weight: bold; }
.custom-dark-select .el-select-dropdown__item.hover, .custom-dark-select .el-select-dropdown__item:hover { background-color: rgba(0, 210, 255, 0.2) !important; color: #00ff9d !important; }
.custom-dark-select .el-select-dropdown__item.selected { color: #00ff9d !important; background-color: rgba(0, 255, 157, 0.1) !important; }
.custom-dark-select .el-popper__arrow::before { background-color: #02121d !important; border-color: #00d2ff !important; }
</style>
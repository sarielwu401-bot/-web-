<!-- 文件路径: D:\Code\MangroveProject\frontend\src\views\Dashboard.vue -->
<template>
  <div class="screen-container">
    
    <!-- ================= 1. 驾驶舱式炫酷顶部导航 ================= -->
    <header class="cockpit-header">
      <div class="header-flank left-flank">
        <div class="time-box">{{ currentTime }}</div>
      </div>
      
      <div class="header-center">
        <div class="center-bg">
          <h1 class="main-title">红树林生态环境大数据监测平台</h1>
        </div>
      </div>
      
      <div class="header-flank right-flank">
        <div class="nav-menu">
          <span class="active">数据概览</span>
          <span @click="$router.push('/intro')">生态科普</span>
          <span @click="$router.push('/tides')">赶海助手</span>
        </div>
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
    <main class="screen-main">
      
      <!-- ================= 左侧面板 ================= -->
      <section class="panel left-panel">
        <div class="tech-box gauge-row">
          <!-- 这里有四个 span，其实就是框框四周跑来跑去的蓝色流水线 -->
          <div class="flow-lines"><span class="line top"></span><span class="line right"></span><span class="line bottom"></span><span class="line left"></span></div>
          <div class="box-title">空间气象感知 (光照/气压)</div>
          <div class="gauge-container">
            <div id="chart-light" class="gauge-item"></div> <!-- 留给 ECharts 画光照图的空盒子 -->
            <div id="chart-press" class="gauge-item"></div>
          </div>
          <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
        </div>

        <div class="tech-box gauge-row">
          <div class="flow-lines"><span class="line top"></span><span class="line right"></span><span class="line bottom"></span><span class="line left"></span></div>
          <div class="box-title">核心水文指标 (PH/水温)</div>
          <div class="gauge-container">
            <div id="chart-ph" class="gauge-item"></div>
            <div id="chart-wtemp" class="gauge-item"></div>
          </div>
          <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
        </div>
      </section>

      <!-- ================= 中间面板 ================= -->
      <section class="panel center-panel">
        
        <div class="tech-box ctrl-box">
          <div class="flow-lines"><span class="line top"></span><span class="line right"></span><span class="line bottom"></span><span class="line left"></span></div>
          <div class="ctrl-content">
            <span class="label">监控节点调度：</span>
            <el-select v-model="currentStation" @change="handleStationChange" class="custom-select" popper-class="custom-dark-select" style="width: 260px">
              <el-option 
                v-for="st in stationList" 
                :key="st.id" 
                :label="`${st.id}号: ${st.name} ${st.is_real ? '(实体节点)' : '(规划中)'}`" 
                :value="st.id" 
              />
            </el-select>

            <div class="status-indicator">
              <span class="dot" :class="isOnline ? 'pulse online' : 'offline'"></span>
              <span :style="{ color: isOnline ? '#00ff9d' : '#ff5252', fontWeight: 'bold', fontSize: '15px' }">
                {{ isOnline ? '设备通信正常 ' : '设备失去联系 (Offline)' }}
              </span>
            </div>
          </div>
          <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
        </div>

        <div class="tech-box map-box">
          <div class="flow-lines"><span class="line top"></span><span class="line right"></span><span class="line bottom"></span><span class="line left"></span></div>
          <div id="map-container"></div>
          
          <div class="massive-offline-overlay" v-if="!isOnline">
            <div class="alert-center-box">
              <el-icon class="warning-icon"><Warning /></el-icon>
              <h2 class="glitch-text">系统失去通信连接</h2>
              <p class="alert-desc">CRITICAL ERROR: OFFLINE</p>
              <div class="alert-detail">已中断超过 30 秒</div>
            </div>
          </div>
          <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
        </div>
      </section>

      <!-- ================= 右侧面板 ================= -->
      <section class="panel right-panel">
        <div class="tech-box gauge-row">
          <div class="flow-lines"><span class="line top"></span><span class="line right"></span><span class="line bottom"></span><span class="line left"></span></div>
          <div class="box-title">微气候分析 (气温/湿度)</div>
          <div class="gauge-container">
            <div id="chart-atemp" class="gauge-item"></div>
            <div id="chart-hum" class="gauge-item"></div>
          </div>
          <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
        </div>

        <div class="tech-box trend-box">
          <div class="flow-lines"><span class="line top"></span><span class="line right"></span><span class="line bottom"></span><span class="line left"></span></div>
          <div class="box-title">实时温湿度波动关联曲线</div>
          <div id="chart-trend" class="chart-content"></div>
          <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
        </div>

        <div class="tech-box alarm-box">
          <div class="flow-lines"><span class="line top"></span><span class="line right"></span><span class="line bottom"></span><span class="line left"></span></div>
          <div class="box-title" style="color: #ff5252; border-left-color: #ff5252;">全局异常告警监控卷轴</div>
          <div class="alarm-header">今日触发告警总计: <span class="danger-text">{{ alarmCount }}</span> 次</div>
          <div class="alarm-list scroll-bar">
            <el-empty v-if="alarmList.length === 0" description="系统运行稳定，无告警记录" :image-size="60"></el-empty>
            <div v-else class="alarm-item" v-for="(item, index) in alarmList" :key="index">
              <div class="time">[{{ formatTime(item.alarm_time) }}]</div>
              <div class="msg">{{ item.msg }}</div>
            </div>
          </div>
          <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
        </div>
      </section>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'// 专门负责给后端打电话要数据的邮递员
import { useRouter } from 'vue-router'
import { Warning, ArrowDown, Setting, SwitchButton } from '@element-plus/icons-vue'
import * as echarts from 'echarts'// 图表工具
import 'echarts-liquidfill'// 这是专门画湿度“水波浪”球的插件
import L from 'leaflet'// 著名的 WebGIS 地图工具
import axios from 'axios'// 专门负责给后端打电话要数据的邮递员
// 定义一堆响应式变量（数据一变，界面就跟着变）
const router = useRouter()
const username = localStorage.getItem('username') || 'Guest'
const isAdmin = localStorage.getItem('role') === 'admin'

const currentTime = ref('')
const currentStation = ref(1) 
const currentData = ref({})
const isOnline = ref(true) 
const alarmCount = ref(0)
const alarmList = ref([])// 存告警日志的数组

const stationList = ref([])

let timer = null// 这是一个定时器，用来每5秒发一次请求
let clockTimer = null
let map = null
const charts = {}// 用来装 ECharts 图表对象的容器
const mapMarkers = {} 

const formatTime = (timeStr) => {
  if(!timeStr) return ''
  const d = new Date(timeStr)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`
}

const updateClock = () => {
  const d = new Date()
  const days =['日', '一', '二', '三', '四', '五', '六']
  currentTime.value = `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')} 星期${days[d.getDay()]} ${formatTime(d)}`
}

const handleCommand = (command) => {
  if (command === 'admin') router.push('/admin')
  else if (command === 'logout') { localStorage.clear(); router.push('/login') }
}

const fetchStations = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/stations')
    if (res.data.code === 200 && res.data.data.length > 0) {
      stationList.value = res.data.data
      stationList.value.forEach(st => { st.color = st.is_real ? '#00ff9d' : '#555' })
      if (!stationList.value.find(s => s.id === currentStation.value)) {
         currentStation.value = stationList.value[0].id
      }
      initMap()
      initCharts()
      handleStationChange() 
      timer = setInterval(fetchRealtimeData, 5000)
    }
  } catch(e) {}
}

const initMap = () => {// 把地图塞进 HTML 里的 map-container 盒子里
  map = L.map('map-container', { zoomControl: false, attributionControl: false })
  
  L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', { 
    subdomains:['1', '2', '3', '4'], maxZoom: 19 
  }).addTo(map)

  const createPulseIcon = (color) => {
    return L.divIcon({
      className: 'custom-div-icon',
      html: `<div class="pulse-marker" style="background-color: ${color}; box-shadow: 0 0 20px ${color}"></div>`,
      iconSize:[24, 24], iconAnchor:[12, 12]
    })
  }

  const bounds =[];
  // 遍历所有站点，在地图上画出发光的呼吸点 (pulse-marker)
  stationList.value.forEach(st => {
    const marker = L.marker([st.lat, st.lng], { icon: createPulseIcon(st.color) }).addTo(map)
    marker.bindPopup(`<b style="color:#000; font-size:14px;">${st.id}号: ${st.name}</b>`)
    marker.on('click', () => { currentStation.value = st.id; handleStationChange(); })
    mapMarkers[st.id] = marker
    bounds.push([st.lat, st.lng]);
  })

  if (bounds.length > 0) map.fitBounds(bounds, { padding: [50, 50], maxZoom: 10 });
  setTimeout(() => {
    if (map) {
      map.invalidateSize(true);
      if (bounds.length > 0) map.fitBounds(bounds, { padding: [50, 50], maxZoom: 10 });
    }
  }, 600);
}


const createCyberGauge = (value, name, min, max, colorStr, unit) => {
  const isValid = value !== undefined && value !== null && value !== '';
  const displayVal = isValid ? Number(value).toFixed(1) : '--';
  
  // 【核心修改点 1】：强行把传给 ECharts 的数值保留 1 位小数，切断长尾巴！
  const gaugeVal = isValid ? Number(Number(value).toFixed(1)) : min; 
  
  return {
    series:[
      {
        type: 'gauge', startAngle: 210, endAngle: -30, min: min, max: max, radius: '90%',
        axisLine: { lineStyle: { width: 15, color: [[1, 'rgba(0, 210, 255, 0.1)']] } },
        splitLine: { show: true, length: 15, distance: -15, lineStyle: { color: '#010f1a', width: 2 } },
        axisTick: { show: false }, axisLabel: { show: false }, pointer: { show: false },
        progress: { show: true, width: 15, itemStyle: { color: isValid ? colorStr : '#333', shadowBlur: 15, shadowColor: isValid ? colorStr : 'transparent' } },
        title: { show: true, fontSize: 13, color: '#8fa3ad', offsetCenter:[0, '70%'] },
        detail: {
          valueAnimation: isValid, fontSize: 26, color: isValid ? '#fff' : '#555', fontWeight: 'bold', offsetCenter:[0, '0%'],
          formatter: displayVal === '--' ? `--\n{unit|${unit}}` : `{value}\n{unit|${unit}}`, 
          rich: { unit: { fontSize: 12, color: isValid ? colorStr : '#555', paddingTop: 10 } }
        },
        data:[{ value: gaugeVal, name: name }]
      }
    ]
  }
}

const initCharts = () => {
  charts.light = echarts.init(document.getElementById('chart-light'))
  charts.press = echarts.init(document.getElementById('chart-press'))
  charts.ph = echarts.init(document.getElementById('chart-ph'))
  charts.wtemp = echarts.init(document.getElementById('chart-wtemp'))
  charts.atemp = echarts.init(document.getElementById('chart-atemp'))
  charts.hum = echarts.init(document.getElementById('chart-hum'))
  charts.trend = echarts.init(document.getElementById('chart-trend'))
  
  window.addEventListener('resize', () => { 
    Object.values(charts).forEach(c => c?.resize());
    if (map) map.invalidateSize(true);
  })
}

const renderGauges = (data) => {
  if(!charts.light) return;
  charts.light.setOption(createCyberGauge(data.lux, '光照强度', 0, 80000, '#f1c40f', 'Lx'))
  charts.press.setOption(createCyberGauge(data.press, '大气气压', 900, 1100, '#9b59b6', 'hPa'))
  
  const isValidPh = data.ph !== undefined && data.ph !== null && data.ph !== '';
  // 专门给特殊渐变的 PH 仪表盘也强行截断 1 位小数
  const phVal = isValidPh ? Number(Number(data.ph).toFixed(1)) : 0;
  const displayPh = isValidPh ? phVal.toFixed(1) : '--';
  
  charts.ph.setOption({
    series:[{
      type: 'gauge', radius: '90%', min: 0, max: 14,
      axisLine: { lineStyle: { width: 12, color: isValidPh ? [[0.4, '#ff5252'],[0.6, '#00ff9d'],[1, '#e91e63']] : [[1, 'rgba(0, 210, 255, 0.1)']] } },
      pointer: { width: 4, itemStyle: { color: isValidPh ? 'auto' : '#555' } }, 
      axisTick: { show: false }, splitLine: { length: 12, distance: -12, lineStyle: { color: '#010f1a', width: 3} },
      axisLabel: { distance: 15, fontSize: 10, color: '#8fa3ad' },
      detail: { formatter: displayPh === '--' ? '--' : '{value}', fontSize: 26, color: isValidPh ? '#fff' : '#555', fontWeight: 'bold', offsetCenter:[0, '60%'] },
      title: { offsetCenter:[0, '95%'], color: '#8fa3ad', fontSize: 13 },
      data:[{ value: phVal, name: '水质 PH' }]
    }]
  })

  charts.wtemp.setOption(createCyberGauge(data.w_temp, '水域温度', 0, 50, '#00d2ff', '℃'))
  charts.atemp.setOption(createCyberGauge(data.a_temp, '空气温度', -10, 50, '#e67e22', '℃'))
  
  const isValidHum = data.hum !== undefined && data.hum !== null && data.hum !== '';
  const humVal = isValidHum ? data.hum / 100 : 0;
  const displayHum = isValidHum ? (humVal * 100).toFixed(0) : '--';
  
  charts.hum.setOption({
    series:[{
      type: 'liquidFill', radius: '80%', center:['50%', '45%'],
      data: isValidHum ?[humVal, humVal - 0.05] :[], 
      color:['#00ff9d', 'rgba(0, 255, 157, 0.3)'], 
      backgroundStyle: { color: 'rgba(0, 30, 45, 0.5)' },
      outline: { borderDistance: 3, itemStyle: { borderWidth: 3, borderColor: isValidHum ? '#00ff9d' : '#555', shadowBlur: 15, shadowColor: isValidHum ? '#00ff9d' : 'transparent' } },
      label: { formatter: displayHum + '%', fontSize: 28, color: isValidHum ? '#fff' : '#555', fontWeight: 'bold' },
      name: '空气湿度'
    }],
    graphic:[{ type: 'text', left: 'center', bottom: '5%', style: { text: '空气湿度', fill: '#8fa3ad', font: '13px sans-serif' } }]
  })
}
// ==================== 到此结束，下面就是 loadChartData 函数了，不用动 ====================
const loadChartData = async () => {
  try {
    const today = new Date().toISOString().split('T')[0]
    const res = await axios.get(`http://localhost:5000/api/history?station_id=${currentStation.value}&date=${today}`)
    
    if (res.data.code === 200) {
      let rawList = res.data.data.reverse()
      const validList = rawList.filter(item => item.w_temp > 0 && item.hum > 0)

      const xData =[]
      const parsedData = { a_temp: [], hum:[] }

      for (let i = 0; i < validList.length; i++) {
        const current = validList[i];
        const d = new Date(current.create_time);
        xData.push(`${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`);
        
        parsedData.a_temp.push(current.a_temp);
        parsedData.hum.push(current.hum);

        if (i < validList.length - 1) {
          const next = validList[i + 1];
          const t1 = new Date(current.create_time).getTime();
          const t2 = new Date(next.create_time).getTime();
          
          if (t2 - t1 > 90000) { 
            xData.push(''); 
            parsedData.a_temp.push(null); 
            parsedData.hum.push(null);
          }
        }
      }
      
      charts.trend.setOption({
        tooltip: { trigger: 'axis', backgroundColor: 'rgba(0,15,25,0.9)', borderColor: '#00d2ff', textStyle: { color: '#fff' } },
        grid: { top: '25%', bottom: '15%', left: '10%', right: '10%' },
        legend: { textStyle: { color: '#e0f7fa' }, top: 0, icon: 'rect' },
        xAxis: { type: 'category', data: xData, axisLine: { lineStyle: { color: '#1a3c5a' } }, axisLabel: { color: '#6a8ca3' } },
        yAxis:[
          { type: 'value', name: '℃', nameTextStyle: { color: '#6a8ca3'}, splitLine: { lineStyle: { color: '#0a1e2f', type: 'dashed' } }, axisLabel: { color: '#6a8ca3' } },
          { type: 'value', name: '%', nameTextStyle: { color: '#6a8ca3'}, splitLine: { show: false }, axisLabel: { color: '#6a8ca3' } }
        ],
        series:[
          { name: '气温', type: 'line', smooth: true, itemStyle: { color: '#ffeb3b' }, lineStyle: { width: 3, shadowBlur: 5, shadowColor: '#ffeb3b' },
            connectNulls: false, 
            areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(255,235,59,0.3)'},{offset:1,color:'transparent'}]) },
            data: parsedData.a_temp },
          { name: '湿度', type: 'line', yAxisIndex: 1, smooth: true, itemStyle: { color: '#00ff9d' }, lineStyle: { width: 3, shadowBlur: 5, shadowColor: '#00ff9d' }, 
            connectNulls: false, 
            data: parsedData.hum }
        ]
      })
    }
  } catch(e) {}
}

const fetchRealtimeData = async () => {
  try {
    const res = await axios.get(`http://localhost:5000/api/realtime?station_id=${currentStation.value}`)
    if (res.data.code === 200) {
      currentData.value = res.data.data || {}
      isOnline.value = res.data.is_online
      alarmCount.value = res.data.alarm_today
      
      // ================= 前端告警队列截断防泄漏】 =================
      // 设定大屏日志卷轴最大展示容量，防止长期挂机导致的 DOM 堆积与浏览器崩溃
      const MAX_LOG_SIZE = 50; 
      let incomingAlarms = res.data.alarm_list ||[];
      if (incomingAlarms.length > MAX_LOG_SIZE) {
        // 使用 slice 进行截断，强制丢弃超过 50 条的老旧数据节点
        incomingAlarms = incomingAlarms.slice(0, MAX_LOG_SIZE);
      }
      alarmList.value = incomingAlarms;
      // =========================================================================
        // 如果设备在线，就把拿到的 currentData 传给仪表盘去画图，如果掉线了，就传个空壳去画
      renderGauges(isOnline.value ? currentData.value : {})
      // 同时去拉取今天一整天的数据，画中间的折线图
      loadChartData()
    }
  } catch(e) {}
}

const handleStationChange = () => { 
  fetchRealtimeData(); 
  if (map && mapMarkers[currentStation.value]) {
    const targetMarker = mapMarkers[currentStation.value];
    map.panTo(targetMarker.getLatLng(), { animate: true, duration: 1.0 });
    setTimeout(() => { targetMarker.openPopup(); }, 500);
  }
}

onMounted(() => {
  updateClock(); clockTimer = setInterval(updateClock, 1000)
  nextTick(() => {
    fetchStations()
  })
})

onUnmounted(() => {
  clearInterval(timer); clearInterval(clockTimer)
  Object.values(charts).forEach(c => c?.dispose())
})
</script>

<style scoped lang="scss">
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');

.screen-container { 
  width: 100vw; height: 100vh; overflow: hidden; background-color: #010b12; color: #fff; display: flex; flex-direction: column; 
}

.cockpit-header {
  height: 80px; display: flex; justify-content: space-between; align-items: flex-start;
  position: relative; z-index: 100;
  background: url('data:image/svg+xml;utf8,<svg width="100%" height="80" xmlns="http://www.w3.org/2000/svg"><line x1="0" y1="35" x2="30%" y2="35" stroke="%2300d2ff" stroke-width="2"/><line x1="30%" y1="35" x2="33%" y2="75" stroke="%2300d2ff" stroke-width="2"/><line x1="33%" y1="75" x2="67%" y2="75" stroke="%2300d2ff" stroke-width="2"/><line x1="67%" y1="75" x2="70%" y2="35" stroke="%2300d2ff" stroke-width="2"/><line x1="70%" y1="35" x2="100%" y2="35" stroke="%2300d2ff" stroke-width="2"/></svg>') no-repeat top center;
  
  .header-flank { width: 32%; height: 35px; display: flex; align-items: center; padding: 0 30px; background: rgba(0, 30, 50, 0.4); }
  .left-flank { justify-content: flex-start; .time-box { font-family: 'Orbitron', sans-serif; color: #00d2ff; font-size: 15px; letter-spacing: 2px; } }
  
  .header-center {
    width: 36%; height: 75px; display: flex; justify-content: center; align-items: center;
    background: radial-gradient(ellipse at bottom, rgba(0, 210, 255, 0.3) 0%, transparent 70%);
    .main-title { font-size: 32px; font-weight: bold; margin: 0; padding-bottom: 10px; color: #fff; text-shadow: 0 0 10px #00d2ff, 0 0 20px #00ff9d; letter-spacing: 5px; }
  }

  .right-flank {
    justify-content: flex-end; gap: 30px;
    .nav-menu { display: flex; gap: 20px; font-size: 15px; font-weight: bold; span { cursor: pointer; color: #8fa3ad; transition: 0.3s; &:hover { color: #00ff9d; } &.active { color: #00d2ff; } } }
    .el-dropdown-link { display: flex; align-items: center; gap: 10px; cursor: pointer; color: #fff; .avatar { width: 24px; height: 24px; border-radius: 50%; border: 1px solid #00ff9d; } }
  }
}

.screen-main { flex: 1; display: flex; padding: 10px 20px 20px; gap: 20px; height: calc(100vh - 80px); }
.panel { display: flex; flex-direction: column; gap: 20px; }
.left-panel { width: 28%; } .right-panel { width: 28%; } .center-panel { width: 44%; }

.tech-box {
  background: #02121d; border: 1px solid #0a2e4c; box-shadow: 0 5px 20px rgba(0,0,0,0.6), inset 0 0 30px rgba(0, 210, 255, 0.02);
  position: relative; display: flex; flex-direction: column; transition: all 0.8s ease; 
  
  .flow-lines { position: absolute; inset: 0; overflow: hidden; border-radius: inherit; pointer-events: none; z-index: 1; }
  .line { position: absolute; background: linear-gradient(90deg, transparent, #00d2ff); }
  .top { top: 0; left: -100%; width: 100%; height: 2px; animation: flowTop 3s linear infinite; }
  .right { top: -100%; right: 0; width: 2px; height: 100%; background: linear-gradient(180deg, transparent, #00d2ff); animation: flowRight 3s linear infinite; animation-delay: 0.75s; }
  .bottom { bottom: 0; right: -100%; width: 100%; height: 2px; background: linear-gradient(270deg, transparent, #00d2ff); animation: flowBottom 3s linear infinite; animation-delay: 1.5s; }
  .left { bottom: -100%; left: 0; width: 2px; height: 100%; background: linear-gradient(360deg, transparent, #00d2ff); animation: flowLeft 3s linear infinite; animation-delay: 2.25s; }
  
  .box-title { 
    position: relative; z-index: 2; font-size: 15px; font-weight: bold; color: #00d2ff; padding: 15px 20px 0; letter-spacing: 1px; display: flex; align-items: center; text-shadow: 0 0 5px rgba(0,210,255,0.5); transition: 0.5s;
    &::before { content: ''; display: inline-block; width: 4px; height: 16px; background: #00ff9d; margin-right: 10px; border-radius: 2px; box-shadow: 0 0 5px #00ff9d; }
  }
  
  .corner { position: absolute; width: 12px; height: 12px; border: 2px solid #00d2ff; opacity: 0.8; z-index: 2; transition: 0.5s; }
  .tl { top: -1px; left: -1px; border-right: none; border-bottom: none; } .tr { top: -1px; right: -1px; border-left: none; border-bottom: none; }
  .bl { bottom: -1px; left: -1px; border-right: none; border-top: none; } .br { bottom: -1px; right: -1px; border-left: none; border-top: none; }
}
/* 定义动画：让线条从左边（-100%）跑到右边（100%），永远循环（infinite） */
@keyframes flowTop { 50%, 100% { left: 100%; } } @keyframes flowRight { 50%, 100% { top: 100%; } } @keyframes flowBottom { 50%, 100% { right: 100%; } } @keyframes flowLeft { 50%, 100% { bottom: 100%; } }

/* 1. 把所有仪表盘变成灰色，变暗，去掉发光特效！模拟断电效果 */
.is-offline { 
  filter: grayscale(100%) brightness(0.3); box-shadow: none !important; border-color: #222 !important;
  .flow-lines { display: none; } .box-title { color: #555 !important; text-shadow: none !important; &::before { background: #555; box-shadow: none;} } .corner { border-color: #444 !important; }
}

.massive-offline-overlay {
  position: absolute; inset: 0; z-index: 999; background: rgba(20, 0, 0, 0.7); backdrop-filter: blur(5px); display: flex; justify-content: center; align-items: center; animation: bgFlash 2s infinite alternate;
  .alert-center-box {
    border: 2px solid #ff5252; background: rgba(30, 0, 0, 0.95); box-shadow: 0 0 50px rgba(255, 0, 0, 0.4), inset 0 0 30px rgba(255, 0, 0, 0.2); padding: 60px 80px; border-radius: 12px; text-align: center; transform: scale(0.8); opacity: 0; animation: popScale 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    .warning-icon { font-size: 80px; color: #ff5252; margin-bottom: 15px; animation: iconPulse 1s infinite; text-shadow: 0 0 20px #ff5252;}
    .glitch-text { color: #ff5252; font-size: 42px; margin: 0 0 10px; letter-spacing: 5px; font-weight: 900; text-shadow: 0 0 15px #ff5252; }
    .alert-desc { color: #ff8a80; font-size: 20px; margin: 0 0 25px; letter-spacing: 3px; font-family: 'Orbitron', sans-serif;}
    .alert-detail { color: #a0a0a0; font-size: 14px; line-height: 1.8; border-top: 1px dashed rgba(255,82,82,0.5); padding-top: 20px;}
  }
}
@keyframes popScale { to { transform: scale(1); opacity: 1; } } @keyframes iconPulse { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.1); opacity: 0.7; } } @keyframes bgFlash { from { background: rgba(20, 0, 0, 0.7); } to { background: rgba(40, 0, 0, 0.85); } }

/* ================= 具体组件布局 ================= */
.gauge-row { flex: 1; .gauge-container { position: relative; z-index: 2; display: flex; flex: 1; padding: 10px; } .gauge-item { flex: 1; height: 100%; } }
.trend-box { flex: 1.2; .chart-content { position: relative; z-index: 2; flex: 1; width: 100%; } }

.alarm-box {
  flex: 1.8; 
  .alarm-header { position: relative; z-index: 2; font-size: 13px; color: #8fa3ad; padding: 10px 20px; border-bottom: 1px solid #0a2e4c; }
  .danger-text { color: #ff5252; font-size: 18px; font-weight: bold; font-family: 'Orbitron', sans-serif; }
  .alarm-list {
    position: relative; z-index: 2; flex: 1; overflow-y: auto; padding: 15px 20px;
    .alarm-item { 
      padding: 10px 15px; background: rgba(255, 82, 82, 0.05); 
      border-left: 3px solid #ff5252; margin-bottom: 12px; border-radius: 0 4px 4px 0; 
    }
    .time { color: #ff8a80; font-size: 12px; margin-bottom: 5px; font-family: monospace;} 
    .msg { color: #d0e0e3; font-size: 14px; }
  }
}

.ctrl-box {
  padding: 15px 20px; border-radius: 4px;
  .ctrl-content { position: relative; z-index: 2; display: flex; align-items: center; justify-content: space-between; }
  .label { color: #8fa3ad; font-size: 15px; font-weight: bold; }
  .status-indicator { display: flex; align-items: center; gap: 12px; }
  .dot { width: 12px; height: 12px; border-radius: 50%; }
  .online { background: #00ff9d; box-shadow: 0 0 15px #00ff9d; animation: pulse 1s infinite; }
  .offline { background: #ff5252; box-shadow: 0 0 15px #ff5252; }
}
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }

.map-box { flex: 1; position: relative; padding: 0; border: 1px solid #0a2e4c; #map-container { width: 100%; height: 100%; background: #010a0f; } }

:deep(.pulse-marker) { width: 24px; height: 24px; border-radius: 50%; animation: markerPulse 1.5s infinite alternate; border: 2px solid #fff;}
@keyframes markerPulse { 0% { transform: scale(1); opacity: 1; } 100% { transform: scale(1.5); opacity: 0.3; } }
:deep(.custom-select .el-input__wrapper) { background-color: #031829 !important; box-shadow: 0 0 0 1px #00d2ff inset !important; }
:deep(.custom-select .el-input__inner) { color: #00ff9d !important; font-weight: bold; font-size: 15px;}
.scroll-bar::-webkit-scrollbar { width: 6px; } .scroll-bar::-webkit-scrollbar-thumb { background: #0a2e4c; border-radius: 3px; }
</style>

<style>
.dark-dropdown { background-color: #021a24 !important; border: 1px solid #00d2ff !important; }
.dark-dropdown .el-dropdown-menu__item { color: #fff !important; font-size: 14px !important; padding: 12px 20px !important; }
.dark-dropdown .el-dropdown-menu__item:hover { background-color: rgba(0, 210, 255, 0.2) !important; color: #00d2ff !important; }
.dark-dropdown .admin-item { color: #00ff9d !important; } .dark-dropdown .logout-item { color: #ff5252 !important; }
.el-popper.is-light { border: none !important; } .el-popper[data-popper-placement^=bottom] .el-popper__arrow::before { background-color: #021a24 !important; border-color: #00d2ff !important; }
.custom-dark-select { background-color: #02121d !important; border: 1px solid #00d2ff !important; }
.custom-dark-select .el-select-dropdown__item { color: #8fa3ad !important; font-weight: bold; }
.custom-dark-select .el-select-dropdown__item.hover, .custom-dark-select .el-select-dropdown__item:hover { background-color: rgba(0, 210, 255, 0.2) !important; color: #00ff9d !important; }
.custom-dark-select .el-select-dropdown__item.selected { color: #00ff9d !important; background-color: rgba(0, 255, 157, 0.1) !important; }
.custom-dark-select .el-popper__arrow::before { background-color: #02121d !important; border-color: #00d2ff !important; }
</style>
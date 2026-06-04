<!-- 文件路径: D:\Code\MangroveProject\frontend\src\views\AdminPanel.vue -->
<template>
  <div class="admin-layout">
    <!-- ================= 左侧导航栏 ================= 
     利用了 Vue 的 :class 动态绑定。点哪个按钮，activeMenu 就等于几，界面就知道该显示哪个功能了。-->
    <aside class="sidebar">
      <div class="logo-box">
        <img src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" class="logo" />
        <h2>管理员控制台</h2>
      </div>
      <ul class="nav-menu">
        <li :class="{ active: activeMenu === 'threshold' }" @click="switchMenu('threshold')">
          <el-icon><Setting /></el-icon> 报警阈值设置
        </li>
        <li :class="{ active: activeMenu === 'alarm' }" @click="switchMenu('alarm')">
          <el-icon><Warning /></el-icon> 全局异常告警
        </li>
        <li :class="{ active: activeMenu === 'history' }" @click="switchMenu('history')">
          <el-icon><TrendCharts /></el-icon> 历史数据查看
        </li>
      </ul>

      <div class="bottom-action">
        <el-button type="info" plain icon="Back" class="back-btn" @click="$router.push('/dashboard')">
          返回数据大屏
        </el-button>
      </div>
    </aside>

    <!-- ================= 右侧内容区 ================= -->
    <main class="main-content">
      <header class="top-header">
        <div class="page-title">
          {{ activeMenu === 'threshold' ? '传感器报警阈值管理' : (activeMenu === 'alarm' ? '全局异常告警日志追溯' : '历史时序数据可视化查看') }}
        </div>
        
        <div class="user-info">
          <span>欢迎您，超级管理员 (Admin)</span>
          <el-button type="danger" size="small" link @click="logout">安全退出</el-button>
        </div>
      </header>

      <div class="content-body">
        
        <!-- ================= 视窗 1：阈值设置 ================= 
         利用 v-if 指令，实现点击左侧菜单，右侧无缝切换，页面完全不需要刷新-->
        <div v-if="activeMenu === 'threshold'" class="view-panel">
          <div class="tip-bar">
            <span>提示：修改数值后，系统将立即按照新标准对实时上传的数据进行报警拦截。</span>
            <el-button type="success" icon="Check" @click="saveThresholds">保存生效</el-button>
          </div>
          
          <el-table :data="thresholdList" border stripe class="custom-table">
            <el-table-column prop="sensor_name" label="监测参数" width="150" />
            <el-table-column prop="sensor_key" label="系统标识" width="120" />
            <el-table-column label="安全下限 (Min)">
              <template #default="scope">
                <el-input-number v-model="scope.row.min_val" :precision="1" :step="0.5" />
              </template>
            </el-table-column>
            <el-table-column label="安全上限 (Max)">
              <template #default="scope">
                <el-input-number v-model="scope.row.max_val" :precision="1" :step="0.5" />
              </template>
            </el-table-column>
            <el-table-column prop="unit" label="单位" width="100" />
          </el-table>
        </div>

        <!-- ================= 视窗 2：历史数据查看 ================= -->
        <div v-if="activeMenu === 'history'" class="view-panel history-panel">
          <!-- 智能分析控制台 -->
          <div class="advanced-toolbar">
            <div class="toolbar-row">
              <div class="filter-group">
                <span class="label">监测节点：</span>
                <el-select v-model="queryStation" style="width: 280px;">
                  <el-option 
                    v-for="st in stationList" 
                    :key="st.id" 
                    :label="`${st.id}号: ${st.name} ${st.is_real ? '(实体节点)' : '(规划中)'}`" 
                    :value="st.id" 
                  />
                </el-select>
                
                <span class="label" style="margin-left: 20px;">选择日期：</span>
                <el-date-picker
                  v-model="queryDate"
                  type="date"
                  placeholder="选择查询日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  :disabled-date="disabledDate"
                  :clearable="false"
                />
                
                <el-button type="primary" icon="Search" @click="fetchHistory" style="margin-left: 15px;">提取数据</el-button>
              </div>
              <div class="action-group">
                <el-button type="warning" icon="Download" @click="exportExcel">导出 Excel 报表</el-button>
              </div>
            </div>

            <div class="toolbar-row controls-row" v-if="historyList.length > 0">
              <div class="left-controls">
                <span class="label">分析模式：</span>
                <el-radio-group v-model="displayMode" @change="renderCharts">
                  <el-radio-button label="multi">多维融合展示</el-radio-button>
                  <el-radio-button label="single">单项指标聚焦</el-radio-button>
                </el-radio-group>

                <transition name="el-fade-in">
                  <div style="display: inline-block; margin-left: 20px;" v-show="displayMode === 'multi'">
                    <span class="label">融合指标：</span>
                    <el-select 
                      v-model="selectedMultiSensors" 
                      multiple 
                      collapse-tags
                      collapse-tags-tooltip
                      placeholder="请勾选需要对比的指标"
                      style="width: 240px"
                      @change="renderCharts"
                    >
                      <el-option label="水温 (℃)" value="w_temp" />
                      <el-option label="气温 (℃)" value="a_temp" />
                      <el-option label="空气湿度 (%)" value="hum" />
                      <el-option label="水质 PH" value="ph" />
                      <el-option label="光照强度 (Lx)" value="lux" />
                      <el-option label="大气压 (hPa)" value="press" />
                    </el-select>
                  </div>
                </transition>

                <transition name="el-fade-in">
                  <div style="display: inline-block; margin-left: 20px;" v-show="displayMode === 'single'">
                    <span class="label">聚焦指标：</span>
                    <el-select v-model="singleSensor" @change="renderCharts" style="width: 150px">
                      <el-option label="水温 (℃)" value="w_temp" />
                      <el-option label="气温 (℃)" value="a_temp" />
                      <el-option label="空气湿度 (%)" value="hum" />
                      <el-option label="水质 PH" value="ph" />
                      <el-option label="光照强度 (Lx)" value="lux" />
                      <el-option label="大气压 (hPa)" value="press" />
                    </el-select>
                  </div>
                </transition>
              </div>

              <div class="right-controls">
                <transition name="el-fade-in">
                  <div style="display: inline-block; margin-right: 30px;" v-show="viewMode === 'chart'">
                    <span class="label">图表形态：</span>
                    <el-radio-group v-model="chartType" @change="renderCharts">
                      <el-radio-button label="line">折线图</el-radio-button>
                      <el-radio-button label="bar">柱状图</el-radio-button>
                    </el-radio-group>
                  </div>
                </transition>

                <span class="label">呈现视图：</span>
                <el-radio-group v-model="viewMode" @change="renderCharts">
                  <el-radio-button label="chart">可视化图表</el-radio-button>
                  <el-radio-button label="table">原始数据表</el-radio-button>
                </el-radio-group>
              </div>
            </div>
          </div>

          <div class="display-area" v-loading="loading">
            <el-empty v-if="historyList.length === 0" description="该节点当日无数据记录，请确认设备是否在线或尝试切换日期"></el-empty>
             <!-- 下方展示区：图表和表格的切换 -->
            <template v-else>
              <div v-show="viewMode === 'chart'" class="charts-container">
                <div id="chart-main" class="chart-box single-chart"></div>
              </div>
              
              <div v-show="viewMode === 'table'" class="table-container">
                <el-table :data="historyList" height="100%" border stripe>
                  <el-table-column label="采集时间" width="150">
                    <template #default="scope">{{ formatTime(scope.row.create_time) }}</template>
                  </el-table-column>
                  <el-table-column prop="w_temp" label="水温(℃)" />
                  <el-table-column prop="a_temp" label="气温(℃)" />
                  <el-table-column prop="hum" label="湿度(%)" />
                  <el-table-column prop="ph" label="PH值" />
                  <el-table-column prop="lux" label="光照(Lx)" />
                  <el-table-column prop="press" label="气压(hPa)" />
                </el-table>
              </div>
            </template>
          </div>
        </div>

        <!-- ================= 视窗 3：全局异常告警 ================= -->
        <div v-if="activeMenu === 'alarm'" class="view-panel alarm-panel">
          <div class="advanced-toolbar">
            <div class="toolbar-row">
              <div class="filter-group">
                <span class="label">告警归属节点：</span>
                <el-select v-model="queryAlarmStation" style="width: 280px;">
                  <el-option label="所有节点 (全局联动追踪)" value="0" />
                  <el-option 
                    v-for="st in stationList" 
                    :key="st.id" 
                    :label="`${st.id}号: ${st.name} ${st.is_real ? '(实体节点)' : '(规划中)'}`" 
                    :value="st.id.toString()" 
                  />
                </el-select>
                
                <span class="label" style="margin-left: 20px;">选择告警日期：</span>
                <el-date-picker
                  v-model="queryAlarmDate"
                  type="date"
                  placeholder="选择查询日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  :disabled-date="disabledDate"
                  :clearable="false"
                />
                
                <el-button type="danger" icon="Search" @click="fetchAlarmHistory" style="margin-left: 15px;">追溯异常记录</el-button>
              </div>
            </div>
          </div>

          <div class="display-area" v-loading="loadingAlarms">
            <el-empty v-if="alarmHistoryList.length === 0" description="恭喜，该条件下无任何异常越界告警记录！"></el-empty>
            
            <div v-else class="table-container">
              <el-table :data="alarmHistoryList" height="100%" border stripe style="width: 100%">
                <el-table-column label="告警发生时间" width="180">
                  <template #default="scope">
                    <span style="font-weight:bold; color:#e91e63">{{ formatTime(scope.row.alarm_time) }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="告警节点" width="150">
                  <template #default="scope">
                    <el-tag type="info" effect="dark">{{ scope.row.station_id }}号监测站</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="sensor_key" label="传感器标识" width="120" />
                <el-table-column label="越界数值" width="120">
                  <template #default="scope">
                    <span style="color:#ff5252; font-weight:bold; font-size:16px;">{{ scope.row.val }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="threshold_range" label="设定安全区间" width="150" />
                <el-table-column prop="msg" label="系统告警详情信息" min-width="200" />
              </el-table>
            </div>
          </div>
        </div>

      </div>
    </main>
  </div>
</template>


<script setup>
import { ref, onMounted, onUnmounted, nextTick, shallowRef } from 'vue' //Vue核心工具
import axios from 'axios'// 用来给后端 Flask 发送网络请求的“邮递员”
import { ElMessage, ElMessageBox } from 'element-plus'// 弹窗提示工具
import { useRouter } from 'vue-router'
import { Setting, TrendCharts, Back, Download, Search, Check, Warning } from '@element-plus/icons-vue'// 弹窗提示工具
import * as echarts from 'echarts'//画图神器

const router = useRouter()
const activeMenu = ref('history') 
const loading = ref(false)

const thresholdList = ref([]) // 存放阈值的数组（响应式，数据变了界面自动变）
// 【获取当前阈值】
const fetchThresholds = async () => {
  // 【获取当前阈值】
  try {
    const res = await axios.get('http://localhost:5000/api/threshold')
    if(res.data.code === 200) thresholdList.value = res.data.data// 把要来的数据存到数组里
  } catch(e) {}
}
// 【保存修改后的阈值下发给后端】
const saveThresholds = async () => {
  try {
    const dataToSubmit = thresholdList.value.map(item => ({
        // 把表格里修改过的数据，重新打包
      sensor_key: item.sensor_key, min_val: item.min_val, max_val: item.max_val
    }))
      // 邮递员 axios 带着打包好的数据，用 POST 方式送给后端
    const res = await axios.post('http://localhost:5000/api/threshold', dataToSubmit)
    if(res.data.code === 200) ElMessage.success('阈值设置已成功保存并实时下发！')
  } catch(e) { ElMessage.error('保存失败') }
}

const stationList = ref([])

const fetchStations = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/stations')
    if(res.data.code === 200 && res.data.data.length > 0) {
      stationList.value = res.data.data
      if (!stationList.value.find(s => s.id === queryStation.value)) {
        queryStation.value = stationList.value[0].id
      }
      fetchHistory()
    }
  } catch(e) {
    ElMessage.error('获取监测节点字典失败，请检查数据库服务')
  }
}

const queryDate = ref(new Date().toISOString().split('T')[0]) 
const queryStation = ref(1) 
const historyList = ref([])

const viewMode = ref('chart')         
const displayMode = ref('multi')      
const chartType = ref('line')         
const singleSensor = ref('w_temp')    
const selectedMultiSensors = ref(['w_temp', 'a_temp', 'hum']) 

const sensorMeta = {
  w_temp: { key: 'w_temp', name: '水温', unit: '℃', color: '#00d2ff', min: 0, max: 40 },
  a_temp: { key: 'a_temp', name: '气温', unit: '℃', color: '#ff9800', min: -10, max: 50 },
  hum:    { key: 'hum', name: '空气湿度', unit: '%', color: '#00ff9d', min: 0, max: 100 },
  ph:     { key: 'ph', name: '水质 PH值', unit: '', color: '#e91e63', min: 0, max: 14 },
  lux:    { key: 'lux', name: '光照强度', unit: 'Lx', color: '#ffeb3b', min: 0, max: null },
  press:  { key: 'press', name: '大气气压', unit: 'hPa', color: '#9c27b0', min: 900, max: 1100 }
}

const chartMain = shallowRef(null)
const disabledDate = (time) => time.getTime() > Date.now()

const queryAlarmDate = ref(new Date().toISOString().split('T')[0])
const queryAlarmStation = ref('0') 
const alarmHistoryList = ref([])
const loadingAlarms = ref(false)

const fetchAlarmHistory = async () => {
  loadingAlarms.value = true
  try {
    const res = await axios.get(`http://localhost:5000/api/alarms?station_id=${queryAlarmStation.value}&date=${queryAlarmDate.value}`)
    if(res.data.code === 200) {
      alarmHistoryList.value = res.data.data
      if(alarmHistoryList.value.length === 0) {
        ElMessage.success('当日系统运行平稳，无异常越界记录！')
      }
    }
  } catch(e) {
    ElMessage.error('告警记录追溯失败')
  } finally {
    loadingAlarms.value = false
  }
}

const switchMenu = (menu) => {
  activeMenu.value = menu
  if(menu === 'history') {
    nextTick(() => { if(historyList.value.length > 0) renderCharts() })
  } else if (menu === 'alarm') {
    nextTick(() => { fetchAlarmHistory() }) 
  }
}

const fetchHistory = async () => {
  if (stationList.value.length === 0) return 
  loading.value = true
  try {
      // ... 请求后端获取一天的数据 ...
    const res = await axios.get(`http://localhost:5000/api/history?station_id=${queryStation.value}&date=${queryDate.value}`)
    if(res.data.code === 200) {
      let rawList = res.data.data.reverse() // 把数据按时间正序排列
       // 只要水温或湿度 <= 0，认为是硬件掉电产生的毛刺，统统不要
      historyList.value = rawList.filter(item => item.w_temp > 0 && item.hum > 0)

      if(historyList.value.length === 0) {
        ElMessage.info('该节点在此日期暂无有效数据记录')
        if (chartMain.value) chartMain.value.dispose()
      } else {
        renderCharts() // 过滤干净后，开始画图
      }
    }
  } catch(e) {
    ElMessage.error('查询历史数据失败')
  } finally {
    loading.value = false
  }
}

const renderCharts = () => {
  if (viewMode.value !== 'chart' || historyList.value.length === 0) return

  nextTick(() => {
    const xData = []
    const parsedData = { w_temp:[], a_temp: [], hum: [], ph: [], lux: [], press:[] }

    // 统一保留1位小数的辅助函数，过滤微小噪点，让曲线从物理级别变得丝滑
    const toFix1 = (val) => val !== null && val !== undefined ? Number(Number(val).toFixed(1)) : null;

    for (let i = 0; i < historyList.value.length; i++) {
      const current = historyList.value[i];
      const d = new Date(current.create_time);
      xData.push(`${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`);
      
      // 使用 toFix1 对入栈数据进行降维修剪
      parsedData.w_temp.push(toFix1(current.w_temp));
      parsedData.a_temp.push(toFix1(current.a_temp));
      parsedData.hum.push(toFix1(current.hum));
      parsedData.ph.push(toFix1(current.ph));
      parsedData.lux.push(toFix1(current.lux));
      parsedData.press.push(toFix1(current.press));

      if (i < historyList.value.length - 1) {
        const next = historyList.value[i + 1];
        const t1 = new Date(current.create_time).getTime();
        const t2 = new Date(next.create_time).getTime();
        
        if (t2 - t1 > 90000) { 
          xData.push(''); 
          parsedData.w_temp.push(null);
          parsedData.a_temp.push(null);
          parsedData.hum.push(null);
          parsedData.ph.push(null);
          parsedData.lux.push(null);
          parsedData.press.push(null);
        }
      }
    }

    if (chartMain.value) { chartMain.value.dispose() }
    chartMain.value = echarts.init(document.getElementById('chart-main'))

    let yAxesConfig = []
    let seriesData =[]
    let titleText = ''
    let gridLeft = 60
    let gridRight = 60

    if (displayMode.value === 'single') {
      const meta = sensorMeta[singleSensor.value]
      titleText = `${queryDate.value} 全天【${meta.name}】演变趋势`
      
      yAxesConfig.push({
        type: 'value', name: `单位 (${meta.unit})`, min: meta.min, max: meta.max,
        splitLine: { lineStyle: { type: 'dashed', color: '#eee' } },
        axisLine: { show: true, lineStyle: { color: meta.color, width: 2 } }
      })

      const areaStyleObj = chartType.value === 'line' ? {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1,[
          { offset: 0, color: meta.color + '88' }, { offset: 1, color: 'transparent' }
        ])
      } : null;

      seriesData.push({
        name: meta.name, type: chartType.value, smooth: chartType.value === 'line', barMaxWidth: 40,
        data: parsedData[meta.key],
        connectNulls: false, 
        itemStyle: { color: meta.color, borderRadius: chartType.value === 'bar' ?[4,4,0,0] : 0 },
        lineStyle: { width: 3, shadowBlur: 10, shadowColor: meta.color },
        areaStyle: areaStyleObj
      })

    } else {
      titleText = `${queryDate.value} 多维度环境生态数据融合对比分析`
      
      if (selectedMultiSensors.value.length === 0) {
        chartMain.value.setOption({ title: { text: '请至少勾选一个融合指标', left: 'center' } })
        return
      }
//Y轴避让
      selectedMultiSensors.value.forEach((key, index) => {
        // 奇数放左边，偶数放右边
        const meta = sensorMeta[key]
        const position = index % 2 === 0 ? 'left' : 'right'
        // 向外推移 60 像素，防止重叠
        const offsetVal = Math.floor(index / 2) * 60

        yAxesConfig.push({
          type: 'value',
          name: meta.name + (meta.unit ? ` (${meta.unit})` : ''),
          position: position, offset: offsetVal, min: meta.min, max: meta.max,
          axisLine: { show: true, lineStyle: { color: meta.color, width: 2 } },
          axisLabel: { color: meta.color, fontWeight: 'bold' },
          splitLine: { show: index === 0, lineStyle: { type: 'dashed', color: '#eee' } } 
        })

        seriesData.push({
          name: meta.name, type: chartType.value, smooth: chartType.value === 'line',
          yAxisIndex: index, barMaxWidth: 30,
          //修改1
          //showSymbol: false,
          data: parsedData[meta.key],
          connectNulls: false,
          //itemStyle: { color: meta.color, borderRadius: chartType.value === 'bar' ?[4,4,0,0] : 0 },
          //lineStyle: { width: 3 }
          itemStyle: { color: meta.color, borderRadius: chartType.value === 'bar' ?[4,4,0,0] : 0 },
          lineStyle: { width: 3, shadowBlur: 8, shadowColor: 'rgba(0, 0, 0, 0.2)', shadowOffsetY: 4 }  
          //v--- 第2处修改：增加高级投影，让线条产生 3D 立体悬浮感，交叉也不会乱 
        })
      })

      const leftCount = Math.ceil(selectedMultiSensors.value.length / 2)
      const rightCount = Math.floor(selectedMultiSensors.value.length / 2)
      gridLeft = 20 + leftCount * 60
      gridRight = 20 + rightCount * 60
    }

    chartMain.value.setOption({
      title: { text: titleText, left: 'center', textStyle: { color: '#333', fontSize: 18, fontWeight: 'bold' }, top: 10 },
      tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
      legend: { top: 40, itemWidth: 20, icon: 'roundRect' }, 
      grid: { left: gridLeft, right: gridRight, bottom: 80, top: 90, containLabel: false },
      xAxis: { type: 'category', data: xData, boundaryGap: chartType.value === 'bar' },
      yAxis: yAxesConfig,
      dataZoom:[ 
        { type: 'inside', start: 0, end: 100 }, 
        { start: 0, end: 100, bottom: 20, textStyle: { color: '#888' } } 
      ],
      series: seriesData
    })
  })
}

const exportExcel = () => {
  if(!queryDate.value) return ElMessage.warning('请先选择日期')
  ElMessageBox.confirm(`确定要导出 ${queryStation.value}号站 ${queryDate.value} 的全天数据为 Excel 吗？`, '导出确认', { type: 'info' })
    .then(() => {
      window.open(`http://localhost:5000/api/history?station_id=${queryStation.value}&date=${queryDate.value}&type=export`)
    })
}

const formatTime = (isoString) => {
  if(!isoString) return ''
  const d = new Date(isoString)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`
}

const logout = () => {
  localStorage.clear()
  router.push('/login')
}

window.addEventListener('resize', () => {
  if (chartMain.value) chartMain.value.resize()
})

onMounted(() => {
  fetchThresholds()
  fetchStations() 
})

onUnmounted(() => {
  if (chartMain.value) chartMain.value.dispose()
})
</script>

<style scoped lang="scss">
.admin-layout {
  display: flex; width: 100vw; height: 100vh; overflow: hidden; background-color: #f4f7f6;
}

/* ================= 左侧侧边栏 ================= */
.sidebar {
  width: 240px; background-color: #021b18; color: #fff; display: flex; flex-direction: column;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.2); z-index: 10; position: relative;
  
  .logo-box {
    height: 70px; display: flex; align-items: center; justify-content: center; gap: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1); background-color: #011311;
    .logo { width: 32px; height: 32px; border-radius: 4px; }
    h2 { font-size: 18px; margin: 0; color: #00ff9d; font-weight: bold; letter-spacing: 1px; }
  }
  
  .nav-menu {
    list-style: none; padding: 20px 0; margin: 0; flex: 1;
    li {
      padding: 15px 25px; font-size: 15px; cursor: pointer; display: flex; align-items: center; gap: 12px;
      color: #8fa3ad; border-left: 4px solid transparent; transition: all 0.3s ease;
      &:hover { background-color: rgba(0, 255, 157, 0.05); color: #fff; }
      &.active { background-color: rgba(0, 255, 157, 0.1); color: #00ff9d; border-left-color: #00ff9d; font-weight: bold; }
    }
  }

  .bottom-action { 
    padding: 20px; 
    border-top: 1px solid rgba(255, 255, 255, 0.1); 
    background-color: #011311; 
    .back-btn { width: 100%; border-color: rgba(255,255,255,0.2); color: #fff; background: transparent; transition: 0.3s; }
    .back-btn:hover { background: rgba(0, 210, 255, 0.2); border-color: #00d2ff; color: #00d2ff; }
  }
}

/* ================= 右侧内容区 ================= */
.main-content {
  flex: 1; display: flex; flex-direction: column; overflow: hidden;
  
  .top-header {
    height: 70px; background-color: #fff; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    display: flex; justify-content: space-between; align-items: center; padding: 0 30px; z-index: 5;
    .page-title { font-size: 18px; font-weight: bold; color: #333; border-left: 4px solid #009688; padding-left: 10px; }
    
    .user-info { 
      display: flex; align-items: center; gap: 15px; font-size: 14px; color: #666; 
      .divider { color: #e4e7ed; font-size: 16px;} 
    }
  }
  
  .content-body {
    flex: 1; padding: 20px; overflow-y: auto;
    .view-panel { background-color: #fff; border-radius: 8px; padding: 25px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03); min-height: calc(100vh - 120px); }
  }
}

/* ================= 阈值设置模块 ================= */
.tip-bar {
  background-color: #e6f7ff; border: 1px solid #91d5ff; padding: 12px 20px; border-radius: 6px;
  display: flex; justify-content: space-between; align-items: center; color: #1890ff; margin-bottom: 25px;
}
.custom-table { border-radius: 6px; overflow: hidden; }

/* ================= 历史查询与告警高级控制台 ================= */
.history-panel, .alarm-panel {
  display: flex; flex-direction: column;
  
  .advanced-toolbar {
    display: flex; flex-direction: column; gap: 15px; margin-bottom: 20px;
    
    .toolbar-row {
      display: flex; justify-content: space-between; align-items: center; 
      background-color: #f8fafc; padding: 15px 20px; border-radius: 6px; border: 1px solid #ebeef5;
    }
    
    .controls-row {
      background-color: #f0f4f8; 
      border: 1px dashed #dcdfe6;
      padding: 10px 20px;
    }

    .filter-group, .left-controls, .right-controls { display: flex; align-items: center; }
    .label { font-size: 14px; color: #606266; font-weight: bold; margin-right: 12px; }
  }

  .display-area {
    flex: 1; min-height: 500px; display: flex; flex-direction: column;
    
    .charts-container {
      flex: 1; display: flex; flex-direction: column;
      .single-chart { flex: 1; min-height: 600px; border: 1px solid #ebeef5; border-radius: 6px; padding: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
    }
    
    .table-container { flex: 1; height: 600px; }
  }
}

:deep(.el-table th.el-table__cell) { background-color: #f5f7fa !important; color: #333; font-weight: bold; }
</style>
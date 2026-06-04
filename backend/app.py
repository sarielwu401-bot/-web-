# 文件路径: D:\Code\MangroveProject\backend\app.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from db_utils import get_db_connection
import datetime
import requests
import xlwt
import io

app = Flask(__name__)
CORS(app)   #装备库与系统初始化

# ================= 核心：设备状态监控与高频缓存机制 =================
LATEST_DATA = {}   #五秒数据 高频缓存
LAST_SAVE_TIME = datetime.datetime.now() - datetime.timedelta(minutes=1)  #低频落盘

# 告警防抖状态机 (Alert Debounce Cache)
# 格式: {"1_w_temp": datetime, "1_ph": datetime} 记录每个站点每个指标上次报警的时间
LAST_ALARM_TIME = {} 
# ====================================================================

# --- 1. 用户登录接口 ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM sys_users WHERE username=%s AND password=%s", 
                           (data.get('username'), data.get('password')))
            user = cursor.fetchone()
            if user:
                return jsonify({'code': 200, 'msg': '登录成功', 'data': {'username': user['username'], 'role': user['role']}})
            return jsonify({'code': 401, 'msg': '账号或密码错误'})
    finally:
        conn.close()

# 监测节点
@app.route('/api/stations', methods=['GET'])
def get_stations():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tb_station ORDER BY id ASC")
            rows = list(cursor.fetchall())
            return jsonify({'code': 200, 'data': rows})
    except Exception as e:
        print(f"获取地点失败: {str(e)}")
        return jsonify({'code': 500, 'msg': str(e)})
    finally:
        conn.close()

# --- 2. 硬件真实上传接口 (包含告警防抖机制) ---
@app.route('/api/upload', methods=['POST'])
def upload_data():
    global LAST_SAVE_TIME, LATEST_DATA, LAST_ALARM_TIME
    raw_data = request.json
    station_id = raw_data.get('station_id', 1)
    now = datetime.datetime.now()

    
    
    data = {}
    data['station_id'] = station_id
    # 温度、湿度保留 1 位小数 (DHT11/DS18B20 物理极限精度)
    data['w_temp'] = round(float(raw_data.get('w_temp', 0)), 1)
    data['a_temp'] = round(float(raw_data.get('a_temp', 0)), 1)
    data['hum'] = round(float(raw_data.get('hum', 0)), 1)
    # pH 值和气压保留 2 位小数
    data['ph'] = round(float(raw_data.get('ph', 0)), 2)
    data['press'] = round(float(raw_data.get('press', 0)), 2)
    # 光照强度 BH1750 输出的必须是整数 Lux，强制转为 int
    data['lux'] = int(float(raw_data.get('lux', 0)))
    # ========================================================================

    w_temp = data.get('w_temp', 0)
    hum = data.get('hum', 0)
    if w_temp <= 0 or hum <= 0:
        print(f"[{now.strftime('%H:%M:%S')}] 拦截到断开/重启产生的 0 值异常数据，安全丢弃！")
        return jsonify({'code': 200, 'msg': 'Garbage Data Ignored'})

    LATEST_DATA[station_id] = {
        'data': data,
        'last_time': now
    }

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tb_threshold")
            thresholds = {row['sensor_key']: row for row in cursor.fetchall()}
            
            for key in['w_temp', 'ph', 'a_temp', 'hum', 'lux', 'press']:
                val = data.get(key)
                setting = thresholds.get(key)
                if val is not None and setting:
                    # 判断是否越界
                    if val < setting['min_val'] or val > setting['max_val']:
                        # 告警防抖 (Debounce) 机制】
                        # 构建唯一的告警键名，例如 "1_w_temp" 代表 1号站的水温
                        alarm_cache_key = f"{station_id}_{key}"
                        last_alarm = LAST_ALARM_TIME.get(alarm_cache_key)
                        
                        # 逻辑：如果之前没报过警，或者距离上次报警已经超过了 60 秒，才允许写入数据库！
                        if not last_alarm or (now - last_alarm).total_seconds() >= 60:
                            msg = f"站点{station_id} {setting['sensor_name']}数值异常: {val}{setting['unit']}"
                            cursor.execute(
                                "INSERT INTO alarm_log (station_id, sensor_key, val, threshold_range, msg) VALUES (%s, %s, %s, %s, %s)",
                                (station_id, key, val, f"{setting['min_val']}~{setting['max_val']}", msg)
                            )
                            # 记录这次报警的精确时间，开启下一次 60 秒的冷却CD
                            LAST_ALARM_TIME[alarm_cache_key] = now
                            print(f"[{now.strftime('%H:%M:%S')}] 触发告警落盘: {msg}")

            # 正常数据的 60 秒定时落盘
            if (now - LAST_SAVE_TIME).total_seconds() >= 60:
                print(f"[{now.strftime('%H:%M:%S')}] 触发 1分钟 定时持久化，写入真实数据...")
                sql = """INSERT INTO env_data (station_id, w_temp, ph, a_temp, hum, lux, press) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (
                    station_id, data.get('w_temp', 0), data.get('ph', 0), 
                    data.get('a_temp', 0), data.get('hum', 0), data.get('lux', 0), data.get('press', 0)
                ))
                LAST_SAVE_TIME = now 

        conn.commit()
        return jsonify({'code': 200, 'msg': 'Data Processed'})
    except Exception as e:
        print(f"上传错误: {e}")
        return jsonify({'code': 500, 'msg': str(e)})
    finally:
        conn.close()

# --- 3. 大屏实时获取接口 ---
@app.route('/api/realtime', methods=['GET'])
def get_realtime():
    station_id = int(request.args.get('station_id', 1))
    now = datetime.datetime.now()
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM alarm_log WHERE DATE(alarm_time) = CURDATE()")
            alarm_count = cursor.fetchone()['count']
            cursor.execute("SELECT * FROM alarm_log ORDER BY id DESC LIMIT 15")
            alarm_list = list(cursor.fetchall())
            
            for a in alarm_list:
                if 'alarm_time' in a and isinstance(a['alarm_time'], datetime.datetime):
                    a['alarm_time'] = a['alarm_time'].strftime('%Y-%m-%dT%H:%M:%S')
            
            res_data = None
            is_online = False
            
            station_info = LATEST_DATA.get(station_id)
            if station_info:
                last_time = station_info['last_time']
                if (now - last_time).total_seconds() <= 30:
                    is_online = True
                    res_data = dict(station_info['data'])
            
            if not res_data:
                cursor.execute("SELECT * FROM env_data WHERE station_id=%s ORDER BY id DESC LIMIT 1", (station_id,))
                res_data = cursor.fetchone()
                if res_data and 'create_time' in res_data and isinstance(res_data['create_time'], datetime.datetime):
                    res_data['create_time'] = res_data['create_time'].strftime('%Y-%m-%dT%H:%M:%S')

            return jsonify({
                'code': 200, 
                'data': res_data, 
                'is_online': is_online, 
                'alarm_today': alarm_count, 
                'alarm_list': alarm_list
            })
    finally:
        conn.close()

# --- 4. 阈值管理 ---
@app.route('/api/threshold', methods=['GET', 'POST'])
def handle_threshold():
    conn = get_db_connection()
    try:
        if request.method == 'GET':
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM tb_threshold")
                return jsonify({'code': 200, 'data': cursor.fetchall()})
        elif request.method == 'POST':
            data = request.json
            with conn.cursor() as cursor:
                for item in data:
                    cursor.execute("UPDATE tb_threshold SET min_val=%s, max_val=%s WHERE sensor_key=%s", 
                                   (item['min_val'], item['max_val'], item['sensor_key']))
            conn.commit()
            return jsonify({'code': 200, 'msg': 'Updated'})
    finally:
        conn.close()

# --- 5. 历史数据与 Excel 导出 ---
@app.route('/api/history', methods=['GET'])
def get_history():
    query_date = request.args.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
    station_id = request.args.get('station_id', 1)
    action_type = request.args.get('type', 'query')
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM env_data WHERE DATE(create_time) = %s AND station_id = %s ORDER BY create_time DESC"
            cursor.execute(sql, (query_date, station_id))
            rows = list(cursor.fetchall())
            
            if action_type == 'export':
                return export_excel(rows, query_date, station_id)
            
            for r in rows:
                if 'create_time' in r and isinstance(r['create_time'], datetime.datetime):
                    r['create_time'] = r['create_time'].strftime('%Y-%m-%dT%H:%M:%S')
                    
            return jsonify({'code': 200, 'data': rows})
    finally:
        conn.close()

def export_excel(rows, date_str, station_id):
    wb = xlwt.Workbook()
    ws = wb.add_sheet(f'站点{station_id}真实数据')
    headers =['时间', '水温(℃)', 'PH值', '气温(℃)', '湿度(%)', '光照(Lx)', '气压(hPa)']
    for col, h in enumerate(headers):
        ws.write(0, col, h)
    for i, row in enumerate(rows):
        ws.write(i+1, 0, row['create_time'].strftime('%H:%M:%S'))
        ws.write(i+1, 1, row['w_temp'])
        ws.write(i+1, 2, row['ph'])
        ws.write(i+1, 3, row['a_temp'])
        ws.write(i+1, 4, row['hum'])
        ws.write(i+1, 5, row['lux'])
        ws.write(i+1, 6, row['press'])
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(output, mimetype='application/vnd.ms-excel', as_attachment=True, download_name=f'RealData_St{station_id}_{date_str}.xls')

# --- 6. 历史报警日志查询接口 ---
@app.route('/api/alarms', methods=['GET'])
def get_alarms():
    query_date = request.args.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
    station_id = request.args.get('station_id', '0') 
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if station_id != '0':
                sql = "SELECT * FROM alarm_log WHERE DATE(alarm_time) = %s AND station_id = %s ORDER BY alarm_time DESC"
                cursor.execute(sql, (query_date, station_id))
            else:
                sql = "SELECT * FROM alarm_log WHERE DATE(alarm_time) = %s ORDER BY alarm_time DESC"
                cursor.execute(sql, (query_date,))
            
            rows = list(cursor.fetchall())
            for r in rows:
                if 'alarm_time' in r and isinstance(r['alarm_time'], datetime.datetime):
                    r['alarm_time'] = r['alarm_time'].strftime('%Y-%m-%dT%H:%M:%S')
            return jsonify({'code': 200, 'data': rows})
    finally:
        conn.close()

# --- 7. 赶海数据和风天气专属 API 代理 ---
@app.route('/api/proxy/tide', methods=['GET'])
def proxy_tide():
    loc = request.args.get('location')
    date = request.args.get('date')
    
    key = 'f053547d0d854d4f979157f079993536'
    api_host = 'ku487ta8ng.re.qweatherapi.com'
    url = f"https://{api_host}/v7/ocean/tide?location={loc}&date={date}&key={key}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'code': '500', 'msg': str(e)})

# --- 8. 动态获取赶海地点配置接口 ---
@app.route('/api/tide_locations', methods=['GET'])
def get_tide_locations():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, location_id FROM tb_tide_location ORDER BY id ASC")
            rows = list(cursor.fetchall())
            return jsonify({'code': 200, 'data': rows})
    except Exception as e:
        print(f"获取地点失败: {str(e)}")
        return jsonify({'code': 500, 'msg': str(e)})
    finally:
        conn.close()

if __name__ == '__main__':
    print("==================================================")
    print(" 后端服务启动成功！")
    print(" 1. 设备心跳检测开启 (30秒)")
    print(" 2. 0值脏数据物理拦截防御墙已上线！")
    
    print("==================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
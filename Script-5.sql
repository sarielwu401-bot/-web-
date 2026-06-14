USE mangrove_db;
-- 2. 创建用户表
CREATE TABLE sys_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(50) NOT NULL,
    role VARCHAR(20) DEFAULT 'guest'
);
INSERT INTO sys_users (username, password, role) VALUES ('admin', 'admin123', 'admin');
INSERT INTO sys_users (username, password, role) VALUES ('guest', 'guest123', 'guest');

-- 3. 创建监测站点表
CREATE TABLE tb_station (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    lat DOUBLE,
    lng DOUBLE,
    is_real BOOLEAN DEFAULT FALSE,
    description VARCHAR(255)
);
INSERT INTO tb_station VALUES 
(1, '深圳湾核心保护区', 22.5431, 114.0579, TRUE, '真实硬件节点'),
(2, '福田红树林边缘区', 22.5450, 114.0600, FALSE, '虚拟节点A'),
(3, '内伶仃岛浅滩区', 22.5400, 114.0550, FALSE, '虚拟节点B');

-- 4. 阈值表
CREATE TABLE tb_threshold (
    sensor_key VARCHAR(20) PRIMARY KEY,
    sensor_name VARCHAR(50),
    min_val FLOAT,
    max_val FLOAT,
    unit VARCHAR(20)
);
INSERT INTO tb_threshold VALUES 
('w_temp', '水温', 15.0, 35.0, '℃'),
('ph', '水质PH值', 6.0, 8.5, ''),
('a_temp', '气温', 10.0, 38.0, '℃'),
('hum', '空气湿度', 30.0, 95.0, '%'),
('lux', '光照强度', 0.0, 80000.0, 'Lx'),
('press', '大气压', 900.0, 1100.0, 'hPa');

-- 5. 环境数据表
CREATE TABLE env_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    station_id INT,
    w_temp FLOAT,
    ph FLOAT,
    a_temp FLOAT,
    hum FLOAT,
    lux FLOAT,
    press FLOAT,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_time (create_time),
    INDEX idx_station (station_id)
);

-- 6. 报警表
CREATE TABLE alarm_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    station_id INT,
    sensor_key VARCHAR(20),
    val FLOAT,
    threshold_range VARCHAR(50),
    msg VARCHAR(255),
    alarm_time DATETIME DEFAULT CURRENT_TIMESTAMP
);




USE mangrove_db;

-- 创建赶海地点配置表
CREATE TABLE tb_tide_location (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '下拉框显示的名称',
    location_id VARCHAR(50) NOT NULL COMMENT '和风天气的 LocationID'
);

-- 插入你想要的赶海地点数据
INSERT INTO tb_tide_location (name, location_id) VALUES 
('深圳湾 (赤湾港)', 'P2951'),
('大梅沙 (盐田港)', 'P2952'),
('珠海 (珠海港)', 'P2954'),
('惠州 (惠州港)', 'P2944'),
('厦门 (厦门港)', 'P2910'),
('北海 (北海港)', 'P3002');
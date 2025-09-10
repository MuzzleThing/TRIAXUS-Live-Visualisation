-- 启用必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";  -- 用于地理空间数据
CREATE EXTENSION IF NOT EXISTS "timescaledb";  -- 用于时序数据优化

-- 1. 航次信息表
CREATE TABLE cruises (
    cruise_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cruise_name VARCHAR(100) NOT NULL,
    vessel_name VARCHAR(100),
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    chief_scientist VARCHAR(100),
    description TEXT,
    metadata JSONB,  -- 存储额外的航次配置信息
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. 文件管理表
CREATE TABLE data_files (
    file_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cruise_id UUID REFERENCES cruises(cruise_id),
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_type VARCHAR(20) CHECK (file_type IN ('CNV', 'HEX', 'HDR', 'XMLCON', 'NC')),
    file_size BIGINT,
    file_hash VARCHAR(64),  -- SHA256 hash确保数据完整性
    upload_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(20) DEFAULT 'pending',
    header_info JSONB,  -- 存储SeaBird header信息
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(file_name, file_hash)
);

-- 3. 传感器配置表
CREATE TABLE sensor_configurations (
    config_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cruise_id UUID REFERENCES cruises(cruise_id),
    sensor_type VARCHAR(50) NOT NULL,
    sensor_name VARCHAR(100),
    serial_number VARCHAR(50),
    calibration_date DATE,
    calibration_coefficients JSONB,
    channel_mapping JSONB,  -- 通道到变量的映射
    valid_from TIMESTAMP WITH TIME ZONE,
    valid_to TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Cast（上下运动周期）表
CREATE TABLE casts (
    cast_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cruise_id UUID REFERENCES cruises(cruise_id),
    file_id UUID REFERENCES data_files(file_id),
    cast_number INTEGER NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    start_location GEOGRAPHY(POINT, 4326),  -- PostGIS地理点
    end_location GEOGRAPHY(POINT, 4326),
    max_depth REAL,
    min_depth REAL,
    direction VARCHAR(10) CHECK (direction IN ('down', 'up', 'both')),
    quality_flag INTEGER DEFAULT 0,  -- 0=good, 1=questionable, 2=bad
    operator_notes TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cast_time (cruise_id, start_time)
);

-- 5. 原始传感器数据表（分区表，按时间分区）
CREATE TABLE sensor_data (
    data_id BIGSERIAL,
    file_id UUID REFERENCES data_files(file_id),
    cast_id UUID REFERENCES casts(cast_id),
    scan_number BIGINT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,

    -- 核心CTD数据
    pressure REAL,
    temperature REAL,
    conductivity REAL,
    salinity REAL,
    depth REAL,

    -- 其他传感器数据
    oxygen REAL,
    fluorescence REAL,
    turbidity REAL,
    par REAL,  -- 光合有效辐射

    -- 位置数据
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,

    -- 质量控制标记
    qc_flags JSONB,  -- 每个变量的QC标记

    -- 扩展数据
    additional_channels JSONB,  -- 存储其他传感器通道数据

    PRIMARY KEY (timestamp, scan_number)
) PARTITION BY RANGE (timestamp);

-- 创建时序超表（使用TimescaleDB）
SELECT create_hypertable('sensor_data', 'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE);

-- 6. GPS轨迹表
CREATE TABLE gps_tracks (
    track_id BIGSERIAL PRIMARY KEY,
    cruise_id UUID REFERENCES cruises(cruise_id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    device_type VARCHAR(20) CHECK (device_type IN ('TRIAXUS', 'VESSEL')),
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    heading REAL,
    speed REAL,
    status VARCHAR(20) DEFAULT 'active',  -- active, inactive, error
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建GPS数据的时序超表
SELECT create_hypertable('gps_tracks', 'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE);

-- 7. 处理后的数据产品表（用于可视化）
CREATE TABLE processed_data (
    processed_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cast_id UUID REFERENCES casts(cast_id),
    processing_type VARCHAR(50),  -- 'gridded', 'binned', 'smoothed'
    depth_bins REAL[],
    time_bins TIMESTAMP WITH TIME ZONE[],
    variable_name VARCHAR(50),
    data_array JSONB,  -- 存储处理后的多维数组
    processing_params JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_processed_cast (cast_id, variable_name)
);

-- 8. 质量控制日志表
CREATE TABLE qc_logs (
    qc_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID REFERENCES data_files(file_id),
    cast_id UUID REFERENCES casts(cast_id),
    qc_type VARCHAR(50),  -- 'range_check', 'spike_test', 'gradient_test'
    variable_name VARCHAR(50),
    test_params JSONB,
    flagged_count INTEGER,
    flagged_indices INTEGER[],
    qc_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    operator VARCHAR(100),
    notes TEXT
);

-- 9. 操作日志表
CREATE TABLE operation_logs (
    log_id BIGSERIAL PRIMARY KEY,
    cruise_id UUID REFERENCES cruises(cruise_id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    log_type VARCHAR(20) CHECK (log_type IN ('info', 'warning', 'error', 'user_action')),
    component VARCHAR(50),  -- 'data_ingestion', 'visualization', 'qc', 'export'
    message TEXT NOT NULL,
    details JSONB,
    user_id VARCHAR(100)
);

-- 10. 实时数据缓冲表（用于高频实时数据暂存）
CREATE TABLE realtime_buffer (
    buffer_id BIGSERIAL PRIMARY KEY,
    file_id UUID REFERENCES data_files(file_id),
    raw_line TEXT NOT NULL,  -- 原始CNV数据行
    line_number BIGINT,
    parsed_data JSONB,
    processing_status VARCHAR(20) DEFAULT 'pending',
    received_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- 创建关键索引
CREATE INDEX idx_sensor_data_cast ON sensor_data(cast_id);
CREATE INDEX idx_sensor_data_file ON sensor_data(file_id);
CREATE INDEX idx_sensor_data_depth ON sensor_data(depth);
CREATE INDEX idx_gps_tracks_cruise ON gps_tracks(cruise_id);
CREATE INDEX idx_gps_location ON gps_tracks USING GIST(location);
CREATE INDEX idx_casts_location ON casts USING GIST(start_location);
CREATE INDEX idx_operation_logs_time ON operation_logs(timestamp DESC);

-- 创建触发器：自动更新updated_at字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_cruises_updated_at BEFORE UPDATE ON cruises
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建视图：最新传感器数据
CREATE MATERIALIZED VIEW latest_sensor_readings AS
SELECT DISTINCT ON (file_id)
    file_id,
    timestamp,
    pressure,
    temperature,
    conductivity,
    salinity,
    depth,
    latitude,
    longitude
FROM sensor_data
ORDER BY file_id, timestamp DESC;

-- 定期刷新物化视图
CREATE INDEX idx_latest_readings_file ON latest_sensor_readings(file_id);

-- 数据完整性约束
ALTER TABLE sensor_data ADD CONSTRAINT check_depth_range
    CHECK (depth >= -10 AND depth <= 400);
ALTER TABLE sensor_data ADD CONSTRAINT check_temperature_range
    CHECK (temperature >= -5 AND temperature <= 40);
ALTER TABLE sensor_data ADD CONSTRAINT check_coordinates
    CHECK (latitude >= -90 AND latitude <= 90 AND longitude >= -180 AND longitude <= 180);
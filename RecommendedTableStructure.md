## TRIAXUS项目数据库表设计文档

### 1. 航次信息表 (cruises)
**主键：** cruise_id (UUID类型)  
**外键：** 无  
**列定义：**
- cruise_id：UUID类型，主键，航次唯一标识符，自动生成
- cruise_name：VARCHAR(100)，非空，航次名称
- vessel_name：VARCHAR(100)，可空，调查船名称
- start_date：TIMESTAMP WITH TIME ZONE，可空，航次开始时间
- end_date：TIMESTAMP WITH TIME ZONE，可空，航次结束时间
- chief_scientist：VARCHAR(100)，可空，首席科学家姓名
- description：TEXT，可空，航次描述信息
- metadata：JSONB，可空，额外的航次配置信息
- created_at：TIMESTAMP WITH TIME ZONE，非空，记录创建时间，默认当前时间
- updated_at：TIMESTAMP WITH TIME ZONE，非空，记录更新时间，默认当前时间

### 2. 文件管理表 (data_files)
**主键：** file_id (UUID类型)  
**外键：** cruise_id 关联 cruises表的cruise_id  
**列定义：**
- file_id：UUID类型，主键，文件唯一标识符，自动生成
- cruise_id：UUID类型，外键，关联的航次ID
- file_name：VARCHAR(255)，非空，文件名称
- file_path：VARCHAR(500)，可空，文件存储路径
- file_type：VARCHAR(20)，可空，文件类型，限定值为CNV、HEX、HDR、XMLCON、NC
- file_size：BIGINT，可空，文件大小（字节）
- file_hash：VARCHAR(64)，可空，文件SHA256哈希值
- upload_time：TIMESTAMP WITH TIME ZONE，非空，文件上传时间，默认当前时间
- processing_status：VARCHAR(20)，非空，处理状态，默认值pending
- header_info：JSONB，可空，SeaBird设备头部信息
- created_at：TIMESTAMP WITH TIME ZONE，非空，记录创建时间，默认当前时间

### 3. 传感器配置表 (sensor_configurations)
**主键：** config_id (UUID类型)  
**外键：** cruise_id 关联 cruises表的cruise_id  
**列定义：**
- config_id：UUID类型，主键，配置唯一标识符，自动生成
- cruise_id：UUID类型，外键，关联的航次ID
- sensor_type：VARCHAR(50)，非空，传感器类型
- sensor_name：VARCHAR(100)，可空，传感器名称
- serial_number：VARCHAR(50)，可空，传感器序列号
- calibration_date：DATE，可空，标定日期
- calibration_coefficients：JSONB，可空，标定系数
- channel_mapping：JSONB，可空，通道到变量的映射关系
- valid_from：TIMESTAMP WITH TIME ZONE，可空，配置生效开始时间
- valid_to：TIMESTAMP WITH TIME ZONE，可空，配置生效结束时间
- created_at：TIMESTAMP WITH TIME ZONE，非空，记录创建时间，默认当前时间

### 4. Cast表 (casts)
**主键：** cast_id (UUID类型)  
**外键：** cruise_id 关联 cruises表的cruise_id，file_id 关联 data_files表的file_id  
**列定义：**
- cast_id：UUID类型，主键，Cast唯一标识符，自动生成
- cruise_id：UUID类型，外键，关联的航次ID
- file_id：UUID类型，外键，关联的文件ID
- cast_number：INTEGER，非空，Cast编号
- start_time：TIMESTAMP WITH TIME ZONE，非空，开始时间
- end_time：TIMESTAMP WITH TIME ZONE，可空，结束时间
- start_location：GEOGRAPHY(POINT, 4326)，可空，开始位置的地理坐标点
- end_location：GEOGRAPHY(POINT, 4326)，可空，结束位置的地理坐标点
- max_depth：REAL，可空，最大深度（米）
- min_depth：REAL，可空，最小深度（米）
- direction：VARCHAR(10)，可空，运动方向，限定值为down、up、both
- quality_flag：INTEGER，非空，质量标记，默认值0（0=良好，1=可疑，2=错误）
- operator_notes：TEXT，可空，操作员备注
- metadata：JSONB，可空，其他元数据
- created_at：TIMESTAMP WITH TIME ZONE，非空，记录创建时间，默认当前时间

### 5. 原始传感器数据表 (sensor_data)
**主键：** 复合主键 (timestamp, scan_number)  
**外键：** file_id 关联 data_files表的file_id，cast_id 关联 casts表的cast_id  
**列定义：**
- data_id：BIGSERIAL，非空，自增ID
- file_id：UUID类型，外键，关联的文件ID
- cast_id：UUID类型，外键，关联的Cast ID
- scan_number：BIGINT，非空，扫描编号
- timestamp：TIMESTAMP WITH TIME ZONE，非空，数据时间戳
- pressure：REAL，可空，压力（分巴）
- temperature：REAL，可空，温度（摄氏度）
- conductivity：REAL，可空，电导率（S/m）
- salinity：REAL，可空，盐度（PSU）
- depth：REAL，可空，深度（米）
- oxygen：REAL，可空，溶解氧（mg/L）
- fluorescence：REAL，可空，荧光强度
- turbidity：REAL，可空，浊度（NTU）
- par：REAL，可空，光合有效辐射
- latitude：DOUBLE PRECISION，可空，纬度
- longitude：DOUBLE PRECISION，可空，经度
- qc_flags：JSONB，可空，各变量的质量控制标记
- additional_channels：JSONB，可空，其他传感器通道数据

### 6. GPS轨迹表 (gps_tracks)
**主键：** track_id (BIGSERIAL类型)  
**外键：** cruise_id 关联 cruises表的cruise_id  
**列定义：**
- track_id：BIGSERIAL，主键，自增ID
- cruise_id：UUID类型，外键，关联的航次ID
- timestamp：TIMESTAMP WITH TIME ZONE，非空，时间戳
- device_type：VARCHAR(20)，可空，设备类型，限定值为TRIAXUS、VESSEL
- location：GEOGRAPHY(POINT, 4326)，非空，地理位置点
- heading：REAL，可空，航向（度）
- speed：REAL，可空，速度（节）
- status：VARCHAR(20)，非空，状态，默认值active（active、inactive、error）
- metadata：JSONB，可空，其他元数据
- created_at：TIMESTAMP WITH TIME ZONE，非空，记录创建时间，默认当前时间

### 7. 处理后数据产品表 (processed_data)
**主键：** processed_id (UUID类型)  
**外键：** cast_id 关联 casts表的cast_id  
**列定义：**
- processed_id：UUID类型，主键，处理数据唯一标识符，自动生成
- cast_id：UUID类型，外键，关联的Cast ID
- processing_type：VARCHAR(50)，可空，处理类型（gridded、binned、smoothed）
- depth_bins：REAL数组，可空，深度分层
- time_bins：TIMESTAMP WITH TIME ZONE数组，可空，时间分段
- variable_name：VARCHAR(50)，可空，变量名称
- data_array：JSONB，可空，处理后的多维数组数据
- processing_params：JSONB，可空，处理参数
- created_at：TIMESTAMP WITH TIME ZONE，非空，记录创建时间，默认当前时间

### 8. 质量控制日志表 (qc_logs)
**主键：** qc_id (UUID类型)  
**外键：** file_id 关联 data_files表的file_id，cast_id 关联 casts表的cast_id  
**列定义：**
- qc_id：UUID类型，主键，质控记录唯一标识符，自动生成
- file_id：UUID类型，外键，关联的文件ID
- cast_id：UUID类型，外键，关联的Cast ID
- qc_type：VARCHAR(50)，可空，质控类型（range_check、spike_test、gradient_test）
- variable_name：VARCHAR(50)，可空，变量名称
- test_params：JSONB，可空，测试参数
- flagged_count：INTEGER，可空，标记的数据点数量
- flagged_indices：INTEGER数组，可空，被标记的数据索引
- qc_timestamp：TIMESTAMP WITH TIME ZONE，非空，质控时间，默认当前时间
- operator：VARCHAR(100)，可空，操作员
- notes：TEXT，可空，备注

### 9. 操作日志表 (operation_logs)
**主键：** log_id (BIGSERIAL类型)  
**外键：** cruise_id 关联 cruises表的cruise_id  
**列定义：**
- log_id：BIGSERIAL，主键，自增ID
- cruise_id：UUID类型，外键，关联的航次ID
- timestamp：TIMESTAMP WITH TIME ZONE，非空，时间戳，默认当前时间
- log_type：VARCHAR(20)，可空，日志类型，限定值为info、warning、error、user_action
- component：VARCHAR(50)，可空，组件名称（data_ingestion、visualization、qc、export）
- message：TEXT，非空，日志消息
- details：JSONB，可空，详细信息
- user_id：VARCHAR(100)，可空，用户ID

### 10. 实时数据缓冲表 (realtime_buffer)
**主键：** buffer_id (BIGSERIAL类型)  
**外键：** file_id 关联 data_files表的file_id  
**列定义：**
- buffer_id：BIGSERIAL，主键，自增ID
- file_id：UUID类型，外键，关联的文件ID
- raw_line：TEXT，非空，原始CNV数据行
- line_number：BIGINT，可空，行号
- parsed_data：JSONB，可空，解析后的数据
- processing_status：VARCHAR(20)，非空，处理状态，默认值pending
- received_at：TIMESTAMP WITH TIME ZONE，非空，接收时间，默认当前时间
- processed_at：TIMESTAMP WITH TIME ZONE，可空，处理完成时间

## 特殊说明

1. **时序数据优化**：sensor_data和gps_tracks表将使用TimescaleDB扩展转换为超表，自动按时间分区
2. **地理空间数据**：使用PostGIS扩展处理所有地理位置数据，支持空间查询和距离计算
3. **数据完整性**：通过file_hash确保原始数据不被篡改，所有表都有created_at时间戳追踪
4. **灵活扩展**：大量使用JSONB字段存储可变结构数据，适应不同传感器配置和元数据需求
5. **性能优化**：在关键查询字段建立索引，包括时间、深度、位置等维度

# File structure
triaxus_backend/
├── alembic/                          # 数据库迁移管理
│   ├── versions/                     # 迁移版本文件
│   ├── alembic.ini                   # Alembic配置
│   ├── env.py                        # 迁移环境配置
│   └── script.py.mako                # 迁移脚本模板
│
├── config/                           # 配置管理
│   ├── __init__.py
│   ├── settings.py                   # 基础配置
│   ├── database.py                   # 数据库连接配置
│   ├── logging_config.py             # 日志配置
│   └── environments/                 # 环境特定配置
│       ├── development.py
│       ├── production.py
│       └── testing.py
│
├── database/                         # 数据库核心
│   ├── __init__.py
│   ├── base.py                       # SQLAlchemy基类和元数据
│   ├── session.py                    # 会话管理和连接池
│   ├── mixins.py                     # 可复用的模型混入类
│   └── extensions.py                 # 数据库扩展初始化（PostGIS、TimescaleDB）
│
├── models/                           # 数据模型定义
│   ├── __init__.py                   # 导出所有模型
│   ├── base_model.py                 # 基础模型类（含通用字段）
│   ├── cruise.py                     # 航次相关模型
│   ├── file.py                       # 文件管理模型
│   ├── sensor.py                     # 传感器配置和数据模型
│   ├── cast.py                       # Cast相关模型
│   ├── gps.py                        # GPS轨迹模型
│   ├── qc.py                         # 质量控制模型
│   └── processed.py                  # 处理后数据模型
│
├── repositories/                     # 数据访问层（DAO模式）
│   ├── __init__.py
│   ├── base_repository.py            # 基础仓库类
│   ├── cruise_repository.py          # 航次数据访问
│   ├── sensor_data_repository.py     # 传感器数据访问
│   ├── cast_repository.py            # Cast数据访问
│   ├── file_repository.py            # 文件数据访问
│   ├── gps_repository.py             # GPS数据访问
│   └── realtime_repository.py        # 实时数据缓冲访问
│
├── services/                         # 业务逻辑层
│   ├── __init__.py
│   ├── data_ingestion_service.py     # 数据摄入服务
│   ├── cast_detection_service.py     # Cast自动检测服务
│   ├── qc_service.py                  # 质量控制服务
│   ├── file_processing_service.py    # 文件处理服务
│   ├── realtime_service.py           # 实时数据处理服务
│   ├── export_service.py             # 数据导出服务
│   └── aggregation_service.py        # 数据聚合服务
│
├── schemas/                          # Pydantic模型（数据验证）
│   ├── __init__.py
│   ├── cruise_schema.py              # 航次数据模式
│   ├── sensor_schema.py              # 传感器数据模式
│   ├── cast_schema.py                # Cast数据模式
│   ├── request_schema.py             # API请求模式
│   └── response_schema.py            # API响应模式
│
├── utils/                            # 工具函数
│   ├── __init__.py
│   ├── cnv_parser.py                 # CNV文件解析器
│   ├── time_utils.py                 # 时间处理工具
│   ├── geo_utils.py                  # 地理空间计算工具
│   ├── hash_utils.py                 # 文件哈希工具
│   ├── validators.py                 # 数据验证器
│   └── decorators.py                 # 装饰器（事务、重试等）
│
├── tasks/                            # 异步任务和定时任务
│   ├── __init__.py
│   ├── celery_app.py                 # Celery配置
│   ├── data_processing_tasks.py      # 数据处理任务
│   ├── maintenance_tasks.py          # 维护任务（清理、归档）
│   └── scheduled_tasks.py            # 定时任务
│
├── scripts/                          # 运维脚本
│   ├── __init__.py
│   ├── init_db.py                    # 初始化数据库
│   ├── seed_data.py                  # 填充测试数据
│   ├── create_partitions.py          # 创建时序表分区
│   ├── backup_db.py                  # 数据库备份
│   └── migrate_legacy_data.py        # 历史数据迁移
│
├── tests/                            # 测试
│   ├── __init__.py
│   ├── conftest.py                   # pytest配置和fixtures
│   ├── unit/                         # 单元测试
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── services/
│   │   └── utils/
│   ├── integration/                  # 集成测试
│   │   ├── test_data_pipeline.py
│   │   ├── test_realtime_ingestion.py
│   │   └── test_cast_detection.py
│   └── fixtures/                     # 测试数据
│       ├── sample_cnv_files/
│       └── mock_data.py
│
├── logs/                             # 日志文件
│   └── .gitkeep
│
├── .env.example                      # 环境变量示例
├── .gitignore                        # Git忽略文件
├── requirements.txt                  # Python依赖
├── requirements-dev.txt              # 开发依赖
├── docker-compose.yml                # Docker编排（含PostgreSQL、TimescaleDB、Redis）
├── Dockerfile                        # Docker镜像定义
├── Makefile                         # 常用命令
├── README.md                        # 项目文档
└── pyproject.toml                   # Python项目配置
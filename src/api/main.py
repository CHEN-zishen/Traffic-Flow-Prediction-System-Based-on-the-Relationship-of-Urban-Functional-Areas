"""FastAPI主应用"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys
import json

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.prediction.predictor import create_predictor
from src.api.routes.auth import router as auth_router
from src.api.routes.profile import router as profile_router
from src.api.routes.message import router as message_router
from src.utils.db_utils import DatabaseManager, get_db_manager
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="智能交通流预测系统 API",
    description="基于深度学习的交通流量预测服务",
    version="1.0.0"
)

# 挂载静态文件目录（用于提供头像等静态资源）
static_dir = project_root / "static"
static_dir.mkdir(exist_ok=True)  # 确保目录存在
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 配置CORS（跨域资源共享）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # 本地开发环境
        "http://127.0.0.1:5000",
        "http://localhost:5000",
        "http://127.0.0.1:8501",  # Streamlit
        "http://localhost:8501",
        # Sealos 生产环境
        "https://lybkgczezkpi.sealoshzh.site",  # 前端域名
        "https://yjwkusxabeto.sealoshzh.site",  # 后端域名
        # Sealos 测试环境
        "https://ukkmpvxeanxd.sealoshzh.site",  # 前端测试地址
        "https://hrhpdkpuwpxz.sealoshzh.site",  # 后端测试地址
        "*"  # 允许所有来源（开发环境）
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册路由
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(message_router)

# 全局预测器（启动时加载）
predictor = None


class PredictionRequest(BaseModel):
    """预测请求"""
    sensor_id: str
    sequence_data: List[List[float]]  # shape: (seq_len, features)
    model_type: str = "lstm"


class PredictionResponse(BaseModel):
    """预测响应"""
    sensor_id: str
    flow_prediction: float
    density_prediction: float
    congestion_status: int
    congestion_level: str
    confidence: float
    prediction_time: str
    model_type: str


# ===================== 城市级预测（全国主要城市） =====================
class CityPredictionRequest(BaseModel):
    city: str
    date: str
    time_range: str
    weather: str
    district: str | None = None
    other: str | None = None
    token: str | None = None  # 添加token字段，用于识别用户
    model_type: str | None = None  # 模型类型（从用户配置获取）


@app.post("/city/predict")
async def city_predict(req: CityPredictionRequest):
    """
    面向全国主要城市的交通流量预测（演示版）

    说明：
    - 该接口结合时间段、天气、功能区等要素生成稳定可复现的演示预测结果
    - 后续可接入真实城市级数据与模型
    """
    import hashlib
    import random
    import asyncio
    
    # 模拟模型预测延迟（3~6秒随机），增强真实感
    delay = random.uniform(3.0, 6.0)
    await asyncio.sleep(delay)

    # 生成确定性随机种子（基于输入）
    seed_src = f"{req.city}|{req.date}|{req.time_range}|{req.weather}|{req.district}|{req.other}"
    seed_int = int(hashlib.sha256(seed_src.encode('utf-8')).hexdigest(), 16) % (2**32 - 1)
    rng = random.Random(seed_int)

    # 基础流量（不同城市规模不同的基数）
    city_scale = {
        '北京': 9800, '上海': 9600, '广州': 8800, '深圳': 8600, '杭州': 8200,
        '南京': 7600, '苏州': 7400, '天津': 7200, '武汉': 8000, '成都': 7900,
        '重庆': 7800, '西安': 7000, '郑州': 6900, '青岛': 6800, '厦门': 6400,
        '宁波': 6600, '合肥': 6300, '佛山': 6200, '东莞': 6100
    }
    base = city_scale.get(req.city, 6000)

    # 时间段影响系数
    tr = req.time_range
    if '早高峰' in tr:
        time_k = 1.15
    elif '晚高峰' in tr:
        time_k = 1.2
    elif '夜间' in tr:
        time_k = 0.7
    else:
        time_k = 0.95

    # 天气影响系数
    weather_k = {
        '晴': 1.0, '多云': 0.98, '小雨': 0.92, '大雨': 0.85, '暴雪': 0.75, '雾霾': 0.9, '沙尘暴': 0.8
    }.get(req.weather, 0.95)

    # 功能区影响
    district_k = {
        '主城区': 1.1, '商务区': 1.12, '高校区': 0.95, '景区': 1.05, '住宅区': 0.9, '工业区': 1.0, '其他': 1.0
    }.get((req.district or '其他'), 1.0)

    # 随机扰动（±6%）
    noise = 1.0 + (rng.random() - 0.5) * 0.12

    flow_per_hour = int(base * time_k * weather_k * district_k * noise)
    flow_per_hour = max(500, min(flow_per_hour, 15000))

    # 置信度与拥堵等级
    confidence = round(0.82 + (rng.random() * 0.1), 2)
    severity = '严重' if flow_per_hour > 11000 else ('拥堵' if flow_per_hour > 8500 else ('一般' if flow_per_hour > 6000 else '畅通'))

    base_speed = 68 - (flow_per_hour / 15000) * 35 + rng.uniform(-4, 4)
    avg_speed = round(max(18.0, min(70.0, base_speed)), 1)

    severity_index_map = {
        '严重': 0.88,
        '拥堵': 0.68,
        '一般': 0.48,
        '畅通': 0.22,
    }
    congestion_index = severity_index_map.get(severity, 0.45) + (rng.random() - 0.5) * 0.08
    congestion_index = round(max(0.05, min(congestion_index, 0.95)), 2)

    # 全国省份交通流热力数据（遵循东多西少原则）
    # 使用ECharts标准的省份全称
    province_base_flows = {
        # 东部沿海发达地区（高流量：10000-13000）
        '北京市': 12500, '上海市': 12200, '天津市': 9500,
        '广东省': 11800, '江苏省': 10500, '浙江省': 10200,
        '福建省': 8500, '山东省': 9800,
        
        # 中部地区（中高流量：7000-9000）
        '河南省': 8800, '湖北省': 8500, '湖南省': 8200,
        '河北省': 8000, '安徽省': 7500, '江西省': 7200,
        '山西省': 6500,
        
        # 东北地区（中等流量：5000-7000）
        '辽宁省': 7200, '吉林省': 5500, '黑龙江省': 5800,
        
        # 西南地区（中等流量：5000-8000）
        '重庆市': 8200, '四川省': 8800, '云南省': 6200,
        '贵州省': 5500, '广西壮族自治区': 6800,
        
        # 西北地区（低流量：2000-5000）
        '陕西省': 7000, '甘肃省': 4200, '宁夏回族自治区': 3200,
        '青海省': 2500, '新疆维吾尔自治区': 4000,
        '内蒙古自治区': 4500,
        
        # 特别行政区和其他
        '西藏自治区': 1800, '海南省': 4800,
        '台湾省': 7500, '香港特别行政区': 10500, '澳门特别行政区': 5200
    }
    
    province_flows = []
    
    # 城市到省份的映射（使用完整省份名称）
    city_province_map = {
        '北京': '北京市', '天津': '天津市', '上海': '上海市', '重庆': '重庆市',
        '杭州': '浙江省', '宁波': '浙江省', '南京': '江苏省', '苏州': '江苏省',
        '广州': '广东省', '深圳': '广东省', '佛山': '广东省', '东莞': '广东省',
        '武汉': '湖北省', '成都': '四川省', '西安': '陕西省', '郑州': '河南省',
        '青岛': '山东省', '厦门': '福建省', '合肥': '安徽省'
    }
    
    for province, base in province_base_flows.items():
        # 根据当前城市所在省份和时间段调整流量
        province_flow = base
        
        # 如果是预测城市所在省份，流量更接近预测值
        if city_province_map.get(req.city) == province:
            province_flow = int(flow_per_hour * rng.uniform(0.95, 1.15))
        else:
            # 其他省份根据时间段调整，保持东多西少的梯度
            province_flow = int(base * time_k * weather_k * rng.uniform(0.85, 1.15))
        
        province_flows.append({
            'name': province,
            'value': max(800, min(15000, province_flow))
        })

    # 各城市真实交通监控点（扩展到24-32个路口）
    city_monitors = {
        '北京': [
            '长安街天安门路口', '三环国贸桥', '二环东直门桥', '四环望京桥', '西二环复兴门桥', '东三环国贸立交', 
            '机场高速三元桥', '京通快速双桥', '五环五棵松桥', '六环沙河桥', '西三环紫竹桥', '东四环四惠桥',
            '北三环安贞桥', '南三环木樨园桥', '京承高速望京', '京开高速玉泉营', '京藏高速清河', '京港澳高速西道口',
            '阜石路首钢', '广渠路双井桥', '朝阳路大望路', '平安大街地安门', '德胜门桥', '积水潭桥'
        ],
        '上海': [
            '南京路人民广场', '延安高架成都路段', '中环漕溪路立交', '外环沪闵高架', '浦东世纪大道', '虹桥枢纽',
            '内环高架徐家汇', '北横通道', '南北高架共和新路', '卢浦大桥浦西', '杨浦大桥', '外滩中山东一路',
            '淮海路陕西南路', '四川北路虹口', '张杨路浦东南路', '龙阳路磁悬浮站', '南京西路静安寺', '中山公园',
            '五角场商圈', '徐家汇商圈', '打浦桥', '鲁班路', '大柏树', '曲阳路'
        ],
        '广州': [
            '天河路体育中心', '环市路淘金立交', '广州大道客村立交', '黄埔大道科韵路口', '内环路动物园南门', '珠江新城花城大道',
            '番禺大道南', '白云大道', '新港路琶洲', '江南大道南', '东风路', '中山路',
            '北京路步行街', '上下九步行街', '五羊新城', '赤岗立交', '洛溪大桥', '海珠桥',
            '人民桥', '解放桥', '华南快速干线', '广园快速', '机场高速三元里', '环城高速'
        ],
        '深圳': [
            '深南大道车公庙', '滨河大道香蜜湖', '北环大道梅林关', '南山大道后海', '福田中心区', '宝安大道新安',
            '龙岗大道布吉', '盐田港进港路', '深南大道世界之窗', '深南东路老街', '沙河西路', '侨城东路',
            '科苑路', '白石路', '布心路', '翠竹路', '红岭路', '华强北',
            '皇岗路', '新洲路', '前海路', '蛇口工业区', '龙华大道', '民治大道'
        ],
        '杭州': [
            '西溪路高峰路口', '延安路武林广场', '中河高架凤起路段', '秋涛路复兴大桥', '滨江滨盛路口', '钱塘新区大道',
            '城西银泰路口', '之江大桥北侧', '西湖隧道', '紫金港路', '文一西路', '天目山路',
            '庆春路', '解放路', '湖滨商圈', '吴山广场', '钱江新城', '奥体中心',
            '萧山机场高速', '钱塘江大桥', '复兴大桥', '西兴大桥', '下沙高教园', '余杭高铁站'
        ],
        '南京': [
            '新街口洪武路', '中山东路总统府', '中央路鼓楼广场', '应天大街软件大道', '江东路扬子江隧道', '汉中门大街',
            '玄武大道', '建邺路河西CBD', '夫子庙秦淮河', '中华门城堡', '水西门大街', '龙蟠路',
            '北京东路', '太平北路', '湖南路狮子桥', '珠江路', '仙林大道', '江宁大学城',
            '南京南站', '禄口机场高速', '长江大桥', '长江三桥', '扬子江大道', '河西万达'
        ],
        '苏州': [
            '观前街人民路口', '干将路莫邪路口', '东环路星海广场', '金鸡湖大道', '工业园区星港街', '狮山路新区',
            '吴中大道', '相城大道', '平江路历史街区', '石路商圈', '国际博览中心', '圆融广场',
            '独墅湖大道', '现代大道', '苏虹路', '苏州北站', '高铁新城', '太湖大道',
            '木渎古镇', '虎丘山门', '留园路', '拙政园', '护城河', '平门'
        ],
        '天津': [
            '和平路滨江道', '南京路世纪钟', '黑牛城道', '卫国道天塔', '解放南路', '海河东路',
            '河东大桥', '津滨大道', '五大道', '古文化街', '意式风情区', '滨江道',
            '西康路', '南开大学', '天津大学', '水上公园', '奥体中心', '梅江会展中心',
            '天津站', '天津西站', '滨海新区', '塘沽外滩', '开发区', '空港经济区'
        ],
        '武汉': [
            '中山大道江汉路', '解放大道循礼门', '珞喻路街道口', '武昌和平大道', '长江大桥武昌桥头', '二七长江大桥',
            '鹦鹉大道', '光谷广场', '武汉天地', '楚河汉街', '户部巷', '江汉路步行街',
            '汉口江滩', '武昌江滩', '黄鹤楼', '东湖绿道', '武汉站', '汉口站',
            '光谷广场转盘', '关山大道', '珞喻路鲁巷', '雄楚大道', '白沙洲大桥', '天兴洲大桥'
        ],
        '成都': [
            '天府广场人民南路', '一环路跳伞塔', '二环建设路', '锦江大道合江亭', '天府大道世纪城', '剑南大道孵化园',
            '红星路二段', '春熙路总府路口', '太古里', '宽窄巷子', '武侯祠', '锦里古街',
            '人民公园', '杜甫草堂', '青羊宫', '金沙遗址', '三环路娇子立交', '四环路',
            '双流机场高速', '成温邛高速', '成灌高速', '成绵高速', '天府新区', '高新区'
        ],
        '重庆': [
            '解放碑邹容路', '观音桥商圈', '南坪万达广场', '沙坪坝三峡广场', '朝天门长江大桥', '渝中区大坪',
            '江北嘴中央商务区', '杨家坪', '两路口', '菜园坝', '石桥铺', '杨家坪',
            '渝北龙溪', '南岸弹子石', '九龙坡直港大道', '渝北机场', '北碚缙云山', '江津几江',
            '千厮门大桥', '东水门大桥', '鹅公岩大桥', '黄花园大桥', '李家沱大桥', '马家岩'
        ],
        '西安': [
            '钟楼南大街', '小寨十字', '高新路科技路', '北大街安远门', '长安路雁塔路口', '未央路凤城五路',
            '曲江新区芙蓉路', '西三环丰镐路', '大雁塔', '钟楼', '鼓楼', '回民街',
            '大唐不夜城', '大明宫', '西安站', '西安北站', '经九路', '太华路',
            '凤城一路', '高新四路', '科技路', '丈八路', '电子城', '纬二街'
        ],
        '郑州': [
            '二七广场', '花园路农业路', '中原路桐柏路', '金水路未来路', '郑东新区CBD', '北三环文化路',
            '航海路', '紫荆山路', '东风路', '建设路', '嵩山路', '大学路',
            '经三路', '未来路', '黄河路', '北环路', '南三环', '西三环',
            '郑州东站', '郑州站', '新郑机场高速', '郑开大道', '郑民高速', 'CBD如意湖'
        ],
        '青岛': [
            '五四广场香港路', '台东商圈', '市南区中山路', '李沧万达', '崂山区秦岭路', '黄岛区长江路',
            '即墨蓝谷', '城阳区正阳路', '栈桥', '八大关', '奥帆中心', '石老人海水浴场',
            '香港中路', '闽江路', '延吉路', '辽阳西路', '海尔路', '深圳路',
            '宁夏路', '劲松路', '福州路', '南京路', '青岛站', '青岛北站'
        ],
        '厦门': [
            '思明中山路', '湖滨南路', '仙岳路湖里', '集美大道', '环岛路会展中心', '海沧大桥',
            '翔安隧道', '同安环城路', '鼓浪屿码头', '曾厝垵', '白城沙滩', '椰风寨',
            'SM广场', '文灶', '莲坂', '吕厝', '软件园二期', '观音山',
            '五缘湾', '集美学村', '杏林湾', '马銮湾', '翔安新城', '海沧新城'
        ],
        '宁波': [
            '天一广场', '鼓楼沿江东路', '江北万达', '鄞州中兴路', '东部新城', '宁波大学周边',
            '北仑港区', '镇海招宝山大桥', '月湖公园', '城隍庙', '老外滩', '三江口',
            '环城南路', '中山东路', '解放路', '灵桥路', '百丈路', '江东北路',
            '鄞州大道', '福明路', '首南路', '宁南路', '杭甬高速', '甬台温高速'
        ],
        '合肥': [
            '淮河路步行街', '金寨路黄山路口', '长江路蜀山', '包河大道', '政务区天鹅湖', '瑶海区明光路',
            '新站高新区', '滨湖新区', '逍遥津', '包公园', '三孝口', '四牌楼',
            '芜湖路', '宿州路', '阜阳路', '蒙城路', '长江中路', '马鞍山路',
            '望江路', '徽州大道', '合肥南站', '合肥站', '新桥机场高速', '金寨南路高架'
        ],
        '佛山': [
            '祖庙路', '季华路', '魁奇路', '南海大道', '桂城千灯湖', '顺德大良',
            '三水广场', '高明荷城', '岭南大道', '佛山大道', '汾江路', '普君路',
            '同济路', '文华路', '禅城东方广场', '南庄', '张槎', '石湾',
            '大沥', '狮山', '西樵山', '陈村', '勒流', '容桂'
        ],
        '东莞': [
            '南城鸿福路', '东城花园路', '莞太路', '虎门太平', '长安振安路', '塘厦环市路',
            '厚街大道', '松山湖大道', '虎门大桥', '常平', '樟木头', '大朗',
            '黄江', '清溪', '凤岗', '石龙', '石排', '企石',
            '茶山', '横沥', '东坑', '桥头', '谢岗', '望牛墩'
        ]
    }
    
    # 获取对应城市的所有监控点，如果没有则使用默认
    all_monitor_names = city_monitors.get(req.city, [
        '主干道一号路口', '核心区二号路段', '环线三号立交', '新区四号大道', 
        '机场五号高架', '开发区六号路', '商圈七号路口', '景区八号大桥',
        'CBD九号广场', '高新区十号大道', '火车站广场', '汽车站路口',
        '体育中心', '会展中心', '政务区', '大学城', '工业园区', '物流园',
        '科技园', '经济开发区', '保税区', '自贸区', '新城区', '老城区'
    ])
    
    # 打乱顺序并选择前8个（使用确定性随机）
    monitor_sample = rng.sample(all_monitor_names, min(8, len(all_monitor_names)))
    
    monitors = [{
        'name': f"{req.city}·{label}", 
        'status': rng.choice(['良好','拥堵','缓行'])
    } for label in monitor_sample]
    
    # 同时返回所有监控点，用于前端刷新
    all_monitors = [{
        'name': f"{req.city}·{label}", 
        'status': rng.choice(['良好','拥堵','缓行'])
    } for label in all_monitor_names]

    generated_at = datetime.now()
    index_score = round(flow_per_hour / 15000 * 100, 2)

    # 保存到数据库
    try:
        prediction_date = datetime.strptime(req.date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式应为YYYY-MM-DD")

    # 从token中获取user_id
    user_id = None
    user_model_type = req.model_type or 'lstm'  # 默认使用lstm
    if req.token:
        try:
            from src.utils.auth import decode_access_token
            payload = decode_access_token(req.token)
            if payload:
                user_id = payload.get("user_id")
                # 如果请求中没有指定模型类型，从用户配置中获取
                if not req.model_type and user_id:
                    try:
                        from src.utils.db_utils import get_session
                        from src.models_db.user import User
                        session = get_session()
                        user = session.query(User).filter(User.id == user_id).first()
                        if user and user.model_type:
                            user_model_type = user.model_type
                        session.close()
                    except Exception as user_error:
                        print(f"[WARN] 获取用户模型配置失败: {user_error}")
        except Exception as token_error:
            print(f"[WARN] 解析token失败: {token_error}")

    try:
        db = get_db_manager()
        db.create_city_prediction({
            "user_id": user_id,  # 添加user_id
            "model_type": user_model_type,  # 添加model_type
            "city": req.city,
            "prediction_date": prediction_date,
            "time_range": req.time_range,
            "weather": req.weather,
            "district": req.district,
            "other": req.other,
            "flow_per_hour": flow_per_hour,
            "avg_speed": avg_speed,
            "congestion_index": congestion_index,
            "severity": severity,
            "confidence": confidence,
            "index_score": index_score,
            "extra_payload": json.dumps(req.dict(), ensure_ascii=False),
            "created_at": generated_at,
        })
        
        # 如果有用户ID，更新用户的预测次数
        if user_id:
            try:
                from src.utils.db_utils import get_session
                from src.models_db.user import User
                session = get_session()
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    user.prediction_count = (user.prediction_count or 0) + 1
                    session.commit()
                session.close()
            except Exception as update_error:
                print(f"[WARN] 更新用户预测次数失败: {update_error}")
    except Exception as db_error:
        print(f"[WARN] 保存城市预测记录失败: {db_error}")

    return {
        'city': req.city,
        'flow_per_hour': flow_per_hour,
        'confidence': confidence,
        'severity': severity,
        'avg_speed': avg_speed,
        'congestion_index': congestion_index,
        'index_score': index_score,
        'province_flows': province_flows,
        'monitors': monitors,
        'all_monitors': all_monitors,  # 所有监控点，用于前端刷新
        'generated_at': generated_at.strftime('%Y-%m-%d %H:%M:%S')
    }


@app.get("/city/history/summary")
async def city_history_summary(token: str, range_days: int = 0, city: str | None = None):
    """历史预测汇总统计（仅返回当前用户的数据）"""
    from src.utils.auth import decode_access_token
    
    # 验证token并获取用户ID
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="令牌数据无效")
    
    try:
        # 只返回当前用户的统计数据
        stats = get_db_manager().get_city_prediction_stats(
            user_id=user_id,  # 添加用户ID过滤
            range_days=range_days, 
            city=city
        )
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


@app.get("/city/history/records")
async def city_history_records(token: str, limit: int = 100, range_days: int = 0, city: str | None = None):
    """历史预测记录列表（仅返回当前用户的数据）"""
    from src.utils.auth import decode_access_token
    
    # 验证token并获取用户ID
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="令牌数据无效")
    
    try:
        # 只返回当前用户的预测记录
        records = get_db_manager().get_city_predictions(
            user_id=user_id,  # 添加用户ID过滤
            limit=limit,
            range_days=range_days,
            city=city,
        )
        return {
            "count": len(records),
            "records": records,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")


@app.get("/city/history/detail/{record_id}")
async def city_history_detail(record_id: int, token: str):
    """获取单条历史预测记录的详细信息（需要验证是当前用户的记录）"""
    from src.utils.auth import decode_access_token
    
    # 验证token并获取用户ID
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="令牌数据无效")
    
    try:
        db = get_db_manager()
        record = db.get_city_prediction_by_id(record_id)
        
        if not record:
            raise HTTPException(status_code=404, detail="记录不存在")
        
        # 验证记录是否属于当前用户（重要：防止越权访问）
        if record.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="无权访问此记录")
        
        # 解析 extra_payload 获取完整的预测信息
        import json
        try:
            payload = json.loads(record.get('extra_payload', '{}'))
        except:
            payload = {}
        
        # 重新生成省份流量和监控点数据（基于原始输入）
        import hashlib
        import random
        
        city = record['city']
        date_str = str(record['prediction_date'])
        time_range = record['time_range']
        weather = payload.get('weather', '晴')
        district = record.get('district', '其他')
        
        # 使用相同的种子确保数据一致性
        seed_src = f"{city}|{date_str}|{time_range}|{weather}|{district}"
        seed_int = int(hashlib.sha256(seed_src.encode('utf-8')).hexdigest(), 16) % (2**32 - 1)
        rng = random.Random(seed_int)
        
        # 生成监控点数据（随机4个）
        city_monitors = {
            '北京': ['长安街天安门路口', '三环国贸桥', '二环东直门桥', '四环望京桥', '西二环复兴门桥', '东三环国贸立交', '机场高速三元桥', '京通快速双桥'],
            '上海': ['南京路人民广场', '延安高架成都路段', '中环漕溪路立交', '外环沪闵高架', '浦东世纪大道', '虹桥枢纽', '内环高架徐家汇', '北横通道'],
            '广州': ['天河路体育中心', '环市路淘金立交', '广州大道客村立交', '黄埔大道科韵路口', '内环路动物园南门', '珠江新城花城大道', '番禺大道南', '白云大道'],
            '深圳': ['深南大道车公庙', '滨河大道香蜜湖', '北环大道梅林关', '南山大道后海', '福田中心区', '宝安大道新安', '龙岗大道布吉', '盐田港进港路'],
            '杭州': ['西溪路高峰路口', '延安路武林广场', '中河高架凤起路段', '秋涛路复兴大桥', '滨江滨盛路口', '钱塘新区大道', '城西银泰路口', '之江大桥北侧'],
            '南京': ['新街口洪武路', '中山东路总统府', '中央路鼓楼广场', '应天大街软件大道', '江东路扬子江隧道', '汉中门大街', '玄武大道', '建邺路河西CBD'],
            '武汉': ['中山大道江汉路', '解放大道循礼门', '珞喻路街道口', '武昌和平大道', '长江大桥武昌桥头', '二七长江大桥', '鹦鹉大道', '光谷广场'],
            '成都': ['天府广场人民南路', '一环路跳伞塔', '二环建设路', '锦江大道合江亭', '天府大道世纪城', '剑南大道孵化园', '红星路二段', '春熙路总府路口'],
        }
        
        monitor_names = city_monitors.get(city, ['主干道路口', '核心区路段', '环线立交', '新区大道', '机场高架', '开发区路', '商圈路口', '景区大桥'])
        # 随机选择4个监控点
        selected_names = rng.sample(monitor_names, min(4, len(monitor_names)))
        monitors = [{
            'name': f"{city}·{name}",
            'status': rng.choice(['良好', '拥堵', '缓行'])
        } for name in selected_names]
        
        return {
            'id': record['id'],
            'city': city,
            'prediction_date': date_str,
            'time_range': time_range,
            'weather': weather,
            'district': district,
            'flow_per_hour': record['flow_per_hour'],
            'avg_speed': float(record['avg_speed']),
            'congestion_index': float(record['congestion_index']),
            'severity': record['severity'],
            'confidence': float(record['confidence']),
            'index_score': float(record['index_score']),
            'monitors': monitors,
            'created_at': str(record['created_at']),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取详情失败: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """启动时初始化数据库和加载模型"""
    # 初始化数据库连接
    try:
        print("🔄 正在初始化数据库连接...")
        db_manager = DatabaseManager()
        print("✅ 数据库连接初始化成功")
    except Exception as e:
        print(f"⚠️  数据库连接初始化失败: {e}")
        print("   请检查MySQL服务是否运行")
    
    # 加载预测模型
    global predictor
    try:
        print("🔄 正在加载预测模型...")
        predictor = create_predictor('lstm')
        print("✅ 模型加载成功")
    except Exception as e:
        print(f"⚠️  模型加载失败: {e}")
        print("   请先训练模型：python src/scripts/train_model.py")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "智能交通流预测系统 API",
        "version": "1.0.0",
        "status": "running" if predictor else "model_not_loaded",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "model_loaded": predictor is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/predict/demo")
async def predict_demo(sensor_id: str = None, model_type: str = "lstm"):
    """
    演示预测 - 使用真实数据进行预测
    
    参数：
    - sensor_id: 传感器ID（可选，格式如 "sensor_001"），不指定则随机选择
    - model_type: 模型类型 lstm/gru（默认lstm）
    """
    from src.utils.data_sampler import get_real_data_sampler
    import random
    
    # 检查模型是否加载
    global predictor
    if predictor is None:
        try:
            predictor = create_predictor(model_type)
        except Exception as e:
            raise HTTPException(
                status_code=503, 
                detail=f"模型未加载或不存在。请先训练模型：python src/scripts/train_model.py。错误: {str(e)}"
            )
    
    try:
        # 获取真实数据采样器
        sampler = get_real_data_sampler()
        
        # 解析传感器ID - 如果没有指定，随机选择一个
        sensor_idx = None
        if sensor_id and sensor_id.startswith("sensor_"):
            try:
                sensor_idx = int(sensor_id.split("_")[1])
            except:
                pass
        
        # 如果没有指定传感器，从多个传感器中随机选择
        if sensor_idx is None:
            # 从307个传感器中随机选择一个
            sensor_idx = random.randint(0, 306)
        
        # 从真实数据中采样
        sequence_data, actual_sensor_idx, time_idx = sampler.sample_sequence(
            lookback=12,
            sensor_id=sensor_idx
        )
        
        # 转换为列表（用于JSON返回）
        sequence_list = sequence_data.tolist()
        
        # 生成传感器ID字符串
        sensor_id_str = f"sensor_{actual_sensor_idx:03d}"
        
        # 进行预测（使用save_to_db=True让predictor自动保存）
        result = predictor.predict(
            input_data=sequence_data,
            sensor_id=sensor_id_str,
            save_to_db=True,
            target_time=datetime.now() + timedelta(hours=1)
        )
        
        # 获取传感器统计信息
        stats = sampler.get_sensor_statistics(actual_sensor_idx)
        
        # 返回结果
        return {
            "sensor_id": sensor_id_str,
            "sensor_index": actual_sensor_idx,
            "time_index": int(time_idx),
            "flow_prediction": result['flow'],
            "density_prediction": result['density'],
            "congestion_status": result['congestion_status'],
            "congestion_level": result['congestion_level'],
            "confidence": result.get('confidence', 0.85),
            "prediction_time": datetime.now().isoformat(),
            "model_type": model_type,
            "input_data": sequence_list,  # 返回真实的输入数据
            "data_source": "PeMS04_Real_Data",  # 标识使用真实数据
            "sensor_stats": stats  # 传感器统计信息
        }
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"数据集未找到。请先下载数据集：python src/scripts/download_data.py。错误: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    交通流预测接口
    
    请求示例：
    {
        "sensor_id": "sensor_001",
        "sequence_data": [[100.5, 60.2, 0.5], [102.3, 61.0, 0.52], ...],
        "model_type": "lstm"
    }
    """
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="模型未加载，请先训练模型"
        )
    
    try:
        # 转换输入数据
        input_data = np.array(request.sequence_data)
        
        # 预测
        result = predictor.predict(input_data)
        
        # 构造响应
        response = PredictionResponse(
            sensor_id=request.sensor_id,
            flow_prediction=result['flow'],
            density_prediction=result['density'],
            congestion_status=result['congestion_status'],
            congestion_level=result['congestion_level'],
            confidence=result['confidence'],
            prediction_time=result['prediction_time'],
            model_type=result['model_type']
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")


@app.post("/predict/batch")
async def predict_batch(requests: List[PredictionRequest]):
    """
    批量预测接口
    
    请求示例：
    [
        {
            "sensor_id": "sensor_001",
            "sequence_data": [[100.5, 60.2, 0.5], ...],
            "model_type": "lstm"
        },
        ...
    ]
    """
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="模型未加载，请先训练模型"
        )
    
    try:
        results = []
        for req in requests:
            input_data = np.array(req.sequence_data)
            result = predictor.predict(
                input_data, 
                sensor_id=req.sensor_id,
                save_to_db=True
            )
            
            results.append(PredictionResponse(
                sensor_id=req.sensor_id,
                flow_prediction=result['flow'],
                density_prediction=result['density'],
                congestion_status=result['congestion_status'],
                congestion_level=result['congestion_level'],
                confidence=result['confidence'],
                prediction_time=result['prediction_time'],
                model_type=result['model_type']
            ))
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量预测失败: {str(e)}")


@app.get("/history/{sensor_id}")
async def get_prediction_history(
    sensor_id: str,
    limit: int = 100
):
    """
    查询指定传感器的历史预测记录
    
    参数：
    - sensor_id: 传感器ID
    - limit: 返回记录数（默认100）
    """
    try:
        from src.utils.db_utils import get_db_manager
        db = get_db_manager()
        
        records = db.get_predictions_by_sensor(
            sensor_id=sensor_id,
            limit=limit
        )
        
        return {
            "sensor_id": sensor_id,
            "count": len(records),
            "records": records
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@app.get("/history/recent")
async def get_recent_predictions(limit: int = 50):
    """
    获取最近的预测记录
    
    参数：
    - limit: 返回记录数（默认50）
    """
    try:
        from src.utils.db_utils import get_db_manager
        db = get_db_manager()
        
        try:
            records = db.get_recent_predictions(limit=limit)
        except Exception as db_error:
            # 数据库查询失败，返回空数据
            print(f"[ERROR] 数据库查询失败: {db_error}")
            import traceback
            traceback.print_exc()
            return {
                "count": 0,
                "records": [],
                "error": "数据库暂无数据或连接失败"
            }
        
        return {
            "count": len(records),
            "records": records
        }
    
    except Exception as e:
        # 返回空数据而不是500错误
        print(f"[ERROR] 查询历史记录失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "count": 0,
            "records": [],
            "error": f"查询失败: {str(e)}"
        }


@app.post("/model/switch/{model_name}")
async def switch_model(model_name: str):
    """
    切换预测模型
    
    参数：
    - model_name: 模型名称（lstm 或 gru）
    """
    global predictor
    
    if model_name.lower() not in ['lstm', 'gru']:
        raise HTTPException(
            status_code=400,
            detail="不支持的模型类型，仅支持 lstm 或 gru"
        )
    
    try:
        predictor = create_predictor(model_name.lower())
        return {
            "message": f"成功切换到 {model_name.upper()} 模型",
            "current_model": model_name.upper()
        }
    
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"模型文件不存在: {model_name}_best.pth，请先训练该模型"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"切换模型失败: {str(e)}"
        )


@app.get("/models")
async def list_models():
    """列出可用模型"""
    from src.utils.config import config
    models_dir = Path(config.get('paths.models_best'))
    
    available_models = []
    if models_dir.exists():
        for model_file in models_dir.glob('*.pth'):
            available_models.append(model_file.stem.replace('_best', ''))
    
    return {
        "available_models": available_models,
        "current_model": predictor.model_type.upper() if predictor else None
    }


@app.get("/training/history")
async def get_training_history(limit: int = 10):
    """
    获取训练历史记录
    
    参数：
    - limit: 返回记录数（默认10）
    """
    try:
        from src.utils.db_utils import get_db_manager
        db = get_db_manager()
        
        records = db.get_training_history(limit=limit)
        
        return {
            "count": len(records),
            "records": records
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@app.get("/stats/summary")
async def get_system_stats():
    """
    获取系统统计信息
    """
    try:
        from src.utils.db_utils import get_db_manager
        db = get_db_manager()
        
        # 获取统计信息
        try:
            recent_predictions = db.get_recent_predictions(limit=1000)
        except Exception as e:
            print(f"[ERROR] 获取预测记录失败: {e}")
            import traceback
            traceback.print_exc()
            recent_predictions = []
        
        try:
            training_records = db.get_training_history(limit=100)
        except Exception as e:
            print(f"[ERROR] 获取训练记录失败: {e}")
            training_records = []
        
        # 计算统计
        total_predictions = len(recent_predictions)
        
        # 拥堵状态分布
        congestion_stats = {0: 0, 1: 0, 2: 0, 3: 0}
        for pred in recent_predictions:
            status = pred.get('congestion_prediction', 0)
            if status in congestion_stats:
                congestion_stats[status] += 1
        
        return {
            "total_predictions": total_predictions,
            "total_training_runs": len(training_records),
            "congestion_distribution": {
                "畅通": congestion_stats[0],
                "正常": congestion_stats[1],
                "拥堵": congestion_stats[2],
                "严重拥堵": congestion_stats[3]
            },
            "model_info": {
                "current_model": predictor.model_type.upper() if predictor else "未加载",
                "device": str(predictor.device) if predictor else "N/A"
            }
        }
    
    except Exception as e:
        # 返回默认值而不是抛出异常
        return {
            "total_predictions": 0,
            "total_training_runs": 0,
            "congestion_distribution": {
                "畅通": 0,
                "正常": 0,
                "拥堵": 0,
                "严重拥堵": 0
            },
            "model_info": {
                "current_model": predictor.model_type.upper() if predictor else "未加载",
                "device": str(predictor.device) if predictor else "N/A"
            },
            "error": f"数据库查询失败: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动FastAPI服务...")
    print("   访问 http://127.0.0.1:8000/docs 查看API文档")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


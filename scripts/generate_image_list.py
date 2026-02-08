"""生成图片列表JSON文件"""
import os
import json
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent.parent
images_dir = project_root / 'static' / 'data' / 'images'

# 天气类型映射
weather_types = {
    'dusttornado': '晴天',
    'mist': '多云',
    'foggy': '雾天',
    'rain_storm': '雨天',
    'snow_storm': '暴雪',
    'haze': '雾霾',
    'sand_storm': '沙尘暴'
}

# 收集所有图片
image_catalog = {}

for prefix in weather_types.keys():
    images = []
    pattern = f"{prefix}-*.jpg"
    
    # 查找所有匹配的文件
    for file in images_dir.glob(pattern):
        images.append(file.name)
    
    # 排序
    images.sort()
    
    image_catalog[prefix] = {
        'weather': weather_types[prefix],
        'count': len(images),
        'files': images
    }
    
    print(f"{prefix:15} {len(images):3}张 - {weather_types[prefix]}")

# 保存到JSON文件
output_file = project_root / 'static' / 'data' / 'image_catalog.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(image_catalog, f, ensure_ascii=False, indent=2)

print(f"\n✅ 图片目录已生成: {output_file}")
print(f"   总计: {sum(cat['count'] for cat in image_catalog.values())} 张图片")


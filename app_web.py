"""
智能交通流预测系统 - Web前端服务
基于Flask的现代化后台管理界面
"""

from flask import Flask, render_template, send_from_directory, redirect
from flask_cors import CORS
import os

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# 启用CORS以便与FastAPI通信
CORS(app)

@app.route('/')
def index():
    """默认跳转到登录页面"""
    return redirect('/login')

@app.route('/login')
def login():
    """登录页面"""
    return render_template('login.html')

@app.route('/register')
def register():
    """注册页面（与登录页面合并，通过JavaScript切换）"""
    return render_template('login.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """静态文件服务"""
    return send_from_directory('static', filename)

# ================= 新增全国城市预测页面 =================
@app.route('/input')
def city_input():
    """全国城市预测 - 参数输入页面"""
    return render_template('input.html')


@app.route('/city-result/<city>')
def city_result(city: str):
    """城市结果页"""
    return render_template('city_result.html', city=city)


@app.route('/history')
def history_page():
    """历史预测数据页面"""
    return render_template('history.html')


@app.route('/profile')
def profile_page():
    """个人中心页面"""
    return render_template('profile.html')


@app.route('/model-config')
def model_config_page():
    """模型配置页面"""
    return render_template('model_config.html')


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 智能交通流预测系统 - Web前端服务")
    print("=" * 60)
    print()
    print("📱 Web界面: http://127.0.0.1:5000")
    print("📡 API服务: http://127.0.0.1:8000 (需要单独启动)")
    print()
    print("⚠️  使用提示:")
    print("   1. 确保FastAPI服务已启动: python run_api.py")
    print("   2. 确保MySQL数据库已运行")
    print("   3. 确保模型已训练: python src/scripts/train_model.py")
    print()
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    print()
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )


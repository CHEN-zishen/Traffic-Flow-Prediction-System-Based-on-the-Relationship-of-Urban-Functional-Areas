"""认证相关API路由"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models_db.user import User
from src.utils.db_utils import get_session
from src.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    validate_password_strength,
    validate_email,
    validate_username
)

router = APIRouter(prefix="/auth", tags=["认证"])


# Pydantic模型
class RegisterRequest(BaseModel):
    """注册请求"""
    username: str
    email: EmailStr
    password: str
    nickname: Optional[str] = None


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[dict] = None


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: str
    nickname: Optional[str]
    avatar: Optional[str]
    role: str
    status: int
    login_count: int
    last_login_time: Optional[str]
    created_at: str


@router.post("/register", response_model=dict)
def register(request: RegisterRequest):
    """
    用户注册
    
    - **username**: 用户名（3-20位，只能包含字母、数字、下划线）
    - **email**: 邮箱
    - **password**: 密码（6-50位）
    - **nickname**: 昵称（可选）
    """
    # 验证用户名
    is_valid, error_msg = validate_username(request.username)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # 验证邮箱
    is_valid, error_msg = validate_email(request.email)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # 验证密码强度
    is_valid, error_msg = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    session = get_session()
    
    try:
        # 检查用户名是否已存在
        existing_user = session.query(User).filter(User.username == request.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 检查邮箱是否已存在
        existing_email = session.query(User).filter(User.email == request.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="邮箱已被注册")
        
        # 创建新用户
        password_hash = hash_password(request.password)
        
        new_user = User(
            username=request.username,
            email=request.email,
            password_hash=password_hash,
            nickname=request.nickname or request.username,
            role='user',
            status=1
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        # 创建欢迎通知（直接使用当前session，避免依赖外部管理器）
        try:
            from src.models_db.message import UserNotification
            import logging
            
            logger = logging.getLogger(__name__)
            logger.info(f"[欢迎通知] 开始为用户 {new_user.id} ({new_user.username}) 创建欢迎通知")
            print(f"🔔 [欢迎通知] 开始为用户 {new_user.username} (ID: {new_user.id}) 创建欢迎通知...")
            
            notification_content = f"""尊敬的 {new_user.nickname}，您好！

🎊 热烈欢迎您成为"智能交通流预测系统"的用户！

📱 系统简介
本系统是一个基于深度学习的智能交通流量预测平台，为您提供：
• 精准的交通流量预测服务
• 多城市、多场景的预测支持
• 实时的交通状况分析
• 直观的数据可视化展示

✨ 快速开始
• 点击"数据输入"进行交通预测
• 在"历史数据"查看预测记录
• 在"个人中心"管理您的账户
• 在"模型配置"自定义预测参数

🔒 隐私与安全
我们高度重视您的数据安全和隐私保护：
• 所有数据传输均采用加密技术
• 您的个人信息严格保密
• 预测数据仅供您个人使用
• 我们不会与第三方分享您的数据

💡 温馨提示
如有任何疑问或建议，欢迎随时联系我们。祝您使用愉快！

智能交通流预测系统团队"""
            
            # 直接在当前session中创建通知
            welcome_notification = UserNotification(
                user_id=new_user.id,
                title="🎉 欢迎加入智能交通流预测系统！",
                content=notification_content,
                send_time=datetime.now(),
                is_read=False
            )
            
            session.add(welcome_notification)
            session.commit()
            session.refresh(welcome_notification)
            
            notification_id = welcome_notification.id
            
            logger.info(f"[欢迎通知] ✅ 成功创建通知 ID: {notification_id}")
            print(f"✅ [欢迎通知] 成功！用户 {new_user.username} (ID: {new_user.id}) 的欢迎通知已创建")
            print(f"   通知ID: {notification_id}")
            print(f"   标题: {welcome_notification.title}")
            print(f"   发送时间: {welcome_notification.send_time}")
            
        except Exception as e:
            # 通知发送失败不影响注册流程，但要详细记录错误
            import traceback
            error_detail = traceback.format_exc()
            print(f"❌ [欢迎通知错误] 创建失败 - 用户: {new_user.username} (ID: {new_user.id})")
            print(f"   错误类型: {type(e).__name__}")
            print(f"   错误信息: {str(e)}")
            print(f"   详细堆栈:\n{error_detail}")
            
            # 同时记录到日志
            try:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"创建欢迎通知失败 - 用户ID: {new_user.id}, 错误: {str(e)}", exc_info=True)
            except:
                pass
            
            # 回滚通知（不影响用户创建）
            try:
                session.rollback()
            except:
                pass
        
        return {
            "success": True,
            "message": "注册成功",
            "user": new_user.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")
    finally:
        session.close()


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, http_request: Request):
    """
    用户登录
    
    - **username**: 用户名
    - **password**: 密码
    
    返回JWT令牌
    """
    session = get_session()
    
    try:
        # 查找用户
        user = session.query(User).filter(User.username == request.username).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        
        # 检查用户状态
        if user.status != 1:
            raise HTTPException(status_code=403, detail="账户已被禁用")
        
        # 验证密码
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        
        # 更新登录信息
        user.last_login_time = datetime.now()
        user.last_login_ip = http_request.client.host if http_request.client else None
        user.login_count = (user.login_count or 0) + 1
        session.commit()
        
        # 生成JWT令牌
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role
        }
        access_token = create_access_token(token_data)
        
        return LoginResponse(
            success=True,
            message="登录成功",
            token=access_token,
            user=user.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")
    finally:
        session.close()


@router.get("/current", response_model=UserResponse)
def get_current_user(token: str):
    """
    获取当前用户信息
    
    - **token**: JWT令牌（通过查询参数传递）
    """
    from src.utils.auth import decode_access_token
    
    # 解码令牌
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="令牌数据无效")
    
    session = get_session()
    
    try:
        # 查找用户
        user = session.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        if user.status != 1:
            raise HTTPException(status_code=403, detail="账户已被禁用")
        
        return UserResponse(**user.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")
    finally:
        session.close()


@router.post("/logout")
def logout():
    """
    用户登出
    
    前端应删除本地存储的令牌
    """
    return {
        "success": True,
        "message": "登出成功"
    }


@router.get("/check")
def check_auth(token: str):
    """
    检查认证状态
    
    - **token**: JWT令牌
    """
    from src.utils.auth import decode_access_token
    
    payload = decode_access_token(token)
    
    if payload:
        return {
            "authenticated": True,
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "role": payload.get("role")
        }
    else:
        return {
            "authenticated": False
        }


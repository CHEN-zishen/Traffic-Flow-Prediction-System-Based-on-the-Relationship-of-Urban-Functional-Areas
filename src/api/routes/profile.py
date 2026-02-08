"""个人中心和模型配置API路由"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import sys
from pathlib import Path
import os
import uuid

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models_db.user import User
from src.models_db.city_prediction import CityPrediction
from src.utils.db_utils import get_session
from src.utils.auth import hash_password, verify_password, decode_access_token

router = APIRouter(prefix="/profile", tags=["个人中心"])


# Pydantic模型
class UpdateProfileRequest(BaseModel):
    """更新个人资料请求"""
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str


class UpdateSettingsRequest(BaseModel):
    """更新账号设置请求"""
    receive_email: Optional[bool] = None


class ModelConfigRequest(BaseModel):
    """模型配置请求"""
    model_type: Optional[str] = None
    weather_sensitivity: Optional[float] = None
    time_sensitivity: Optional[float] = None
    district_sensitivity: Optional[float] = None
    other_sensitivity: Optional[float] = None
    use_gpu: Optional[bool] = None
    multi_predict: Optional[bool] = None


def get_user_from_token(token: str):
    """从token获取用户"""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="令牌数据无效")
    
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        if user.status != 1:
            raise HTTPException(status_code=403, detail="账户已被禁用")
        return user, session
    except HTTPException:
        session.close()
        raise
    except Exception as e:
        session.close()
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")


@router.get("/info")
def get_profile_info(token: str):
    """
    获取个人资料信息
    
    - **token**: JWT令牌
    """
    user, session = get_user_from_token(token)
    
    try:
        # 从city_predictions表统计真实预测次数
        try:
            prediction_count = session.query(CityPrediction).filter(
                CityPrediction.user_id == user.id
            ).count()
            
            # 同步更新用户表中的预测次数
            if user.prediction_count != prediction_count:
                user.prediction_count = prediction_count
                session.commit()
        except Exception as count_error:
            print(f"[WARN] 统计预测次数失败: {count_error}")
            # 如果统计失败，使用用户表中的值
            prediction_count = user.prediction_count if user.prediction_count is not None else 0
        
        user_data = user.to_dict()
        user_data['prediction_count'] = prediction_count
        
        return {
            "success": True,
            "data": user_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取个人资料失败: {str(e)}")
    finally:
        session.close()


@router.put("/update")
def update_profile(token: str, request: UpdateProfileRequest):
    """
    更新个人资料
    
    - **token**: JWT令牌
    - **nickname**: 昵称
    - **email**: 邮箱
    - **avatar**: 头像URL
    """
    user, session = get_user_from_token(token)
    
    try:
        if request.nickname is not None:
            user.nickname = request.nickname
        
        if request.email is not None:
            # 检查邮箱是否已被其他用户使用
            existing_email = session.query(User).filter(
                User.email == request.email,
                User.id != user.id
            ).first()
            if existing_email:
                raise HTTPException(status_code=400, detail="邮箱已被其他用户使用")
            user.email = request.email
        
        if request.avatar is not None:
            user.avatar = request.avatar
        
        user.updated_at = datetime.now()
        session.commit()
        session.refresh(user)
        
        return {
            "success": True,
            "message": "个人资料更新成功",
            "data": user.to_dict()
        }
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"更新个人资料失败: {str(e)}")
    finally:
        session.close()


@router.post("/change-password")
def change_password(token: str, request: ChangePasswordRequest):
    """
    修改密码
    
    - **token**: JWT令牌
    - **old_password**: 旧密码
    - **new_password**: 新密码
    """
    user, session = get_user_from_token(token)
    
    try:
        # 验证旧密码
        if not verify_password(request.old_password, user.password_hash):
            raise HTTPException(status_code=400, detail="旧密码错误")
        
        # 验证新密码强度
        if len(request.new_password) < 6:
            raise HTTPException(status_code=400, detail="新密码长度至少为6位")
        
        if len(request.new_password) > 50:
            raise HTTPException(status_code=400, detail="新密码长度不能超过50位")
        
        # 更新密码
        user.password_hash = hash_password(request.new_password)
        user.updated_at = datetime.now()
        session.commit()
        
        return {
            "success": True,
            "message": "密码修改成功"
        }
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"修改密码失败: {str(e)}")
    finally:
        session.close()


@router.put("/settings")
def update_settings(token: str, request: UpdateSettingsRequest):
    """
    更新账号设置
    
    - **token**: JWT令牌
    - **receive_email**: 是否接收邮件
    """
    user, session = get_user_from_token(token)
    
    try:
        if request.receive_email is not None:
            user.receive_email = request.receive_email
        
        user.updated_at = datetime.now()
        session.commit()
        session.refresh(user)
        
        return {
            "success": True,
            "message": "账号设置更新成功",
            "data": user.to_dict()
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"更新账号设置失败: {str(e)}")
    finally:
        session.close()


@router.get("/model-config")
def get_model_config(token: str):
    """
    获取模型配置
    
    - **token**: JWT令牌
    """
    user, session = get_user_from_token(token)
    
    try:
        config = {
            "model_type": user.model_type,
            "weather_sensitivity": user.weather_sensitivity,
            "time_sensitivity": user.time_sensitivity,
            "district_sensitivity": user.district_sensitivity,
            "other_sensitivity": user.other_sensitivity,
            "use_gpu": user.use_gpu,
            "multi_predict": user.multi_predict
        }
        
        return {
            "success": True,
            "data": config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型配置失败: {str(e)}")
    finally:
        session.close()


@router.put("/model-config")
def update_model_config(token: str, request: ModelConfigRequest):
    """
    更新模型配置
    
    - **token**: JWT令牌
    - **model_type**: 模型类型（lstm/gru/ml-hgstn/transformer/tcn）
    - **weather_sensitivity**: 天气因素敏感度（0-1）
    - **time_sensitivity**: 时间段因素敏感度（0-1）
    - **district_sensitivity**: 城市功能区因素敏感度（0-1）
    - **other_sensitivity**: 其他因素敏感度（0-1）
    - **use_gpu**: 是否使用GPU加速
    - **multi_predict**: 是否多次预测
    """
    user, session = get_user_from_token(token)
    
    try:
        if request.model_type is not None:
            # 支持的模型类型列表
            allowed_models = ['lstm', 'gru', 'ml-hgstn', 'transformer', 'tcn']
            if request.model_type not in allowed_models:
                raise HTTPException(
                    status_code=400, 
                    detail=f"模型类型必须是以下之一: {', '.join(allowed_models)}"
                )
            user.model_type = request.model_type
        
        # 验证敏感度范围（0-1）
        sensitivity_fields = [
            ('weather_sensitivity', request.weather_sensitivity),
            ('time_sensitivity', request.time_sensitivity),
            ('district_sensitivity', request.district_sensitivity),
            ('other_sensitivity', request.other_sensitivity)
        ]
        
        for field_name, value in sensitivity_fields:
            if value is not None:
                if not (0 <= value <= 1):
                    raise HTTPException(
                        status_code=400, 
                        detail=f"{field_name}必须在0到1之间"
                    )
        
        if request.weather_sensitivity is not None:
            user.weather_sensitivity = request.weather_sensitivity
        if request.time_sensitivity is not None:
            user.time_sensitivity = request.time_sensitivity
        if request.district_sensitivity is not None:
            user.district_sensitivity = request.district_sensitivity
        if request.other_sensitivity is not None:
            user.other_sensitivity = request.other_sensitivity
        if request.use_gpu is not None:
            user.use_gpu = request.use_gpu
        if request.multi_predict is not None:
            user.multi_predict = request.multi_predict
        
        user.updated_at = datetime.now()
        session.commit()
        session.refresh(user)
        
        return {
            "success": True,
            "message": "模型配置更新成功",
            "data": {
                "model_type": user.model_type,
                "weather_sensitivity": user.weather_sensitivity,
                "time_sensitivity": user.time_sensitivity,
                "district_sensitivity": user.district_sensitivity,
                "other_sensitivity": user.other_sensitivity,
                "use_gpu": user.use_gpu,
                "multi_predict": user.multi_predict
            }
        }
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"更新模型配置失败: {str(e)}")
    finally:
        session.close()


@router.post("/model-config/reset")
def reset_model_config(token: str):
    """
    重置模型配置为默认值
    
    - **token**: JWT令牌
    """
    user, session = get_user_from_token(token)
    
    try:
        user.model_type = 'lstm'
        user.weather_sensitivity = 0.5
        user.time_sensitivity = 0.5
        user.district_sensitivity = 0.5
        user.other_sensitivity = 0.5
        user.use_gpu = False
        user.multi_predict = False
        user.updated_at = datetime.now()
        
        session.commit()
        session.refresh(user)
        
        return {
            "success": True,
            "message": "模型配置已重置为默认值",
            "data": {
                "model_type": user.model_type,
                "weather_sensitivity": user.weather_sensitivity,
                "time_sensitivity": user.time_sensitivity,
                "district_sensitivity": user.district_sensitivity,
                "other_sensitivity": user.other_sensitivity,
                "use_gpu": user.use_gpu,
                "multi_predict": user.multi_predict
            }
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"重置模型配置失败: {str(e)}")
    finally:
        session.close()


@router.post("/upload-avatar")
async def upload_avatar(token: str, file: UploadFile = File(...)):
    """
    上传头像
    
    - **token**: JWT令牌
    - **file**: 头像文件
    """
    user, session = get_user_from_token(token)
    
    try:
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="只支持图片文件")
        
        # 验证文件大小（限制10MB）
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="图片文件大小不能超过10MB")
        
        # 创建上传目录
        upload_dir = Path(project_root) / "static" / "avatars"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成唯一文件名
        file_ext = Path(file.filename).suffix
        new_filename = f"{user.id}_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = upload_dir / new_filename
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 更新用户头像URL（使用完整的后端公网地址）
        # 后端生产地址
        backend_url = "https://yjwkusxabeto.sealoshzh.site"
        avatar_url = f"{backend_url}/static/avatars/{new_filename}"
        user.avatar = avatar_url
        user.updated_at = datetime.now()
        session.commit()
        session.refresh(user)
        
        return {
            "success": True,
            "message": "头像上传成功",
            "avatar_url": avatar_url
        }
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"上传头像失败: {str(e)}")
    finally:
        session.close()


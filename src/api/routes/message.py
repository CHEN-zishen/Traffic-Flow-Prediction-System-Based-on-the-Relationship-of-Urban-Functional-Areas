"""
消息中心相关路由
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

from src.utils.db_utils import get_db_manager
from src.api.routes.auth import get_current_user

router = APIRouter(prefix="/message", tags=["消息中心"])


class AnnouncementResponse(BaseModel):
    """系统公告响应"""
    id: int
    title: str
    content: str
    publish_time: str
    is_active: bool


class NotificationResponse(BaseModel):
    """用户通知响应"""
    id: int
    title: str
    content: str
    is_read: bool
    send_time: str


class MessageCenterResponse(BaseModel):
    """消息中心响应"""
    announcements: List[Dict[str, Any]]
    notifications: List[Dict[str, Any]]
    unread_count: int


@router.get("/center", response_model=MessageCenterResponse)
async def get_message_center(token: str = Query(..., description="用户token")):
    """
    获取消息中心数据（系统公告 + 用户通知）
    """
    try:
        # 验证用户token
        user_info = get_current_user(token)
        if not user_info:
            raise HTTPException(status_code=401, detail="未授权访问")
        
        db = get_db_manager()
        
        # 获取系统公告
        announcements = db.get_system_announcements(limit=50)
        
        # 获取用户通知
        notifications = db.get_user_notifications(user_id=user_info.id, limit=50)
        
        # 获取未读通知数量
        unread_count = db.get_unread_notification_count(user_id=user_info.id)
        
        return {
            "announcements": announcements,
            "notifications": notifications,
            "unread_count": unread_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取消息失败: {str(e)}")


@router.get("/announcements")
async def get_announcements(limit: int = Query(50, description="返回数量")):
    """
    获取系统公告列表
    """
    try:
        db = get_db_manager()
        announcements = db.get_system_announcements(limit=limit)
        return {"success": True, "data": announcements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取公告失败: {str(e)}")


@router.get("/notifications")
async def get_notifications(
    token: str = Query(..., description="用户token"),
    limit: int = Query(50, description="返回数量")
):
    """
    获取用户通知列表
    """
    try:
        # 验证用户token
        user_info = get_current_user(token)
        if not user_info:
            raise HTTPException(status_code=401, detail="未授权访问")
        
        db = get_db_manager()
        notifications = db.get_user_notifications(user_id=user_info.id, limit=limit)
        return {"success": True, "data": notifications}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取通知失败: {str(e)}")


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    token: str = Query(..., description="用户token")
):
    """
    标记通知为已读
    """
    try:
        # 验证用户token
        user_info = get_current_user(token)
        if not user_info:
            raise HTTPException(status_code=401, detail="未授权访问")
        
        db = get_db_manager()
        success = db.mark_notification_as_read(notification_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="通知不存在")
        
        return {"success": True, "message": "已标记为已读"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


@router.get("/unread-count")
async def get_unread_count(token: str = Query(..., description="用户token")):
    """
    获取未读通知数量
    """
    try:
        # 验证用户token
        user_info = get_current_user(token)
        if not user_info:
            raise HTTPException(status_code=401, detail="未授权访问")
        
        db = get_db_manager()
        count = db.get_unread_notification_count(user_id=user_info.id)
        
        return {"success": True, "count": count}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取未读数量失败: {str(e)}")



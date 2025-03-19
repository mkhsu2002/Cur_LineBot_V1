from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

# 建立藍圖
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/ping')
def ping():
    """簡單的健康檢查端點"""
    return jsonify({'status': 'ok', 'message': 'API is running'})

@api_bp.route('/user')
@login_required
def user_info():
    """獲取當前用戶信息"""
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'is_admin': current_user.is_admin
    })

@api_bp.route('/stats')
@login_required
def stats():
    """獲取系統統計數據"""
    if not current_user.is_admin:
        return jsonify({'error': '您沒有權限'}), 403
    
    from models import LineUser, ChatMessage, Document
    
    return jsonify({
        'line_users': LineUser.query.count(),
        'messages': ChatMessage.query.count(),
        'documents': Document.query.count()
    }) 
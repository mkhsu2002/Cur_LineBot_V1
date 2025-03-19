import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from forms import LoginForm

# 建立藍圖
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """處理登入請求"""
    # 如果用戶已登入，重定向到管理面板
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        from models import User
        
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('登入成功！', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        else:
            flash('登入失敗，請檢查帳號和密碼。', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """處理登出請求"""
    logout_user()
    flash('您已登出。', 'info')
    return redirect(url_for('auth.login'))

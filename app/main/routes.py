from flask import render_template, current_app, jsonify
from app.main import bp
import os
import sys

@bp.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('main/index.html', title='الرئيسية')

@bp.route('/about')
def about():
    """صفحة حول الخدمة"""
    return render_template('main/about.html', title='حول الخدمة')

@bp.route('/pricing')
def pricing():
    """صفحة الأسعار"""
    message_price = current_app.config['MESSAGE_PRICE']
    free_limit = current_app.config['FREE_MESSAGES_LIMIT']
    
    return render_template('main/pricing.html', 
                         title='الأسعار',
                         message_price=message_price,
                         free_limit=free_limit)

@bp.route('/docs')
def documentation():
    """صفحة التوثيق"""
    return render_template('main/docs.html', title='التوثيق')

@bp.route('/contact')
def contact():
    """صفحة التواصل"""
    return render_template('main/contact.html', title='تواصل معنا')

@bp.route('/health')
def health_check():
    """نقطة فحص صحة التطبيق للخادم"""
    try:
        from app import db
        # فحص اتصال قاعدة البيانات
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'message': 'Email Sender Pro is running',
            'python_version': sys.version,
            'environment': os.environ.get('FLASK_ENV', 'development')
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'message': str(e)
        }), 500

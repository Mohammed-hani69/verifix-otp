from functools import wraps
from flask import request, jsonify, current_app
from app.models import Company

def api_key_required(f):
    """ديكوريتر للتحقق من صحة مفتاح API"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.json.get('api_key') if request.json else None
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'مفتاح API مطلوب',
                'code': 'API_KEY_REQUIRED'
            }), 401
        
        company = Company.query.filter_by(api_key=api_key).first()
        if not company:
            return jsonify({
                'success': False,
                'error': 'مفتاح API غير صحيح',
                'code': 'INVALID_API_KEY'
            }), 401
        
        if not company.is_active:
            return jsonify({
                'success': False,
                'error': 'الحساب غير نشط',
                'code': 'ACCOUNT_INACTIVE'
            }), 403
        
        # إضافة الشركة إلى السياق
        request.current_company = company
        return f(*args, **kwargs)
    
    return decorated_function

def validate_email_settings(company):
    """التحقق من إعدادات البريد الإلكتروني"""
    required_fields = ['smtp_server', 'smtp_port', 'smtp_username', 'smtp_password', 'sender_email']
    
    for field in required_fields:
        if not getattr(company, field):
            return False, f'إعداد البريد الإلكتروني مفقود: {field}'
    
    return True, None

from flask import request, jsonify, current_app
from app.api import bp
from app.api.auth import api_key_required, validate_email_settings
from app.api.email_service import EmailSender, TemplateProcessor
from app.models import Company, EmailService, EmailTemplate, EmailLog, CompanyService
from app import db
from datetime import datetime

@bp.route('/send-verification', methods=['POST'])
@api_key_required
def send_verification():
    """إرسال كود التحقق"""
    data = request.get_json()
    
    # التحقق من البيانات المطلوبة
    if not data or not data.get('email'):
        return jsonify({
            'success': False,
            'error': 'البريد الإلكتروني مطلوب',
            'code': 'EMAIL_REQUIRED'
        }), 400
    
    company = request.current_company
    
    # التحقق من إعدادات البريد الإلكتروني
    is_valid, error_msg = validate_email_settings(company)
    if not is_valid:
        return jsonify({
            'success': False,
            'error': error_msg,
            'code': 'EMAIL_SETTINGS_INCOMPLETE'
        }), 400
    
    # التحقق من إمكانية إرسال رسالة
    if not company.can_send_message():
        return jsonify({
            'success': False,
            'error': 'رصيدك غير كافي لإرسال رسائل',
            'code': 'INSUFFICIENT_BALANCE'
        }), 403
    
    try:
        # إنتاج كود التحقق
        verification_code = TemplateProcessor.generate_verification_code()
        
        # البحث عن قالب مخصص أو استخدام الافتراضي
        template = EmailTemplate.query.filter_by(
            company_id=company.id,
            service_id=1  # خدمة كود التحقق
        ).first()
        
        if not template:
            # استخدام القالب الافتراضي
            html_content = TemplateProcessor.get_default_template('verification')
        else:
            html_content = template.html_content
        
        # معالجة القالب
        variables = {
            'verification_code': verification_code,
            'email': data['email']
        }
        
        processed_content = TemplateProcessor.process_template(
            template or type('obj', (object,), {
                'html_content': html_content,
                'primary_color': '#007bff',
                'secondary_color': '#6c757d',
                'logo_url': None
            })(),
            variables,
            company
        )
        
        # إرسال البريد الإلكتروني
        email_sender = EmailSender(company)
        success, message = email_sender.send_email(
            data['email'],
            'كود التحقق',
            processed_content,
            'verification'
        )
        
        if success:
            # خصم التكلفة وتسجيل العملية
            company.deduct_message_cost()
            
            # تسجيل العملية
            log = EmailLog(
                company_id=company.id,
                service_id=1,
                template_id=template.id if template else None,
                recipient_email=data['email'],
                subject='كود التحقق',
                status='sent',
                cost=0 if company.free_messages_used <= current_app.config['FREE_MESSAGES_LIMIT'] else current_app.config['MESSAGE_PRICE'],
                was_free=company.free_messages_used <= current_app.config['FREE_MESSAGES_LIMIT']
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'تم إرسال كود التحقق بنجاح',
                'verification_code': verification_code,  # في الإنتاج، يجب عدم إرجاع الكود
                'remaining_balance': company.balance,
                'free_messages_remaining': max(0, current_app.config['FREE_MESSAGES_LIMIT'] - company.free_messages_used)
            })
        else:
            # تسجيل الفشل
            log = EmailLog(
                company_id=company.id,
                service_id=1,
                recipient_email=data['email'],
                subject='كود التحقق',
                status='failed',
                error_message=message,
                cost=0
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({
                'success': False,
                'error': f'فشل في إرسال البريد الإلكتروني: {message}',
                'code': 'SEND_FAILED'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}',
            'code': 'SERVER_ERROR'
        }), 500

@bp.route('/send-order', methods=['POST'])
@api_key_required
def send_order():
    """إرسال تفاصيل الطلب"""
    data = request.get_json()
    
    # التحقق من البيانات المطلوبة
    required_fields = ['email', 'order_number', 'customer_name', 'total_amount']
    for field in required_fields:
        if not data or not data.get(field):
            return jsonify({
                'success': False,
                'error': f'الحقل {field} مطلوب',
                'code': 'FIELD_REQUIRED'
            }), 400
    
    company = request.current_company
    
    # التحقق من إعدادات البريد الإلكتروني
    is_valid, error_msg = validate_email_settings(company)
    if not is_valid:
        return jsonify({
            'success': False,
            'error': error_msg,
            'code': 'EMAIL_SETTINGS_INCOMPLETE'
        }), 400
    
    # التحقق من إمكانية إرسال رسالة
    if not company.can_send_message():
        return jsonify({
            'success': False,
            'error': 'رصيدك غير كافي لإرسال رسائل',
            'code': 'INSUFFICIENT_BALANCE'
        }), 403
    
    try:
        # البحث عن قالب مخصص أو استخدام الافتراضي
        template = EmailTemplate.query.filter_by(
            company_id=company.id,
            service_id=2  # خدمة تفاصيل الطلب
        ).first()
        
        if not template:
            html_content = TemplateProcessor.get_default_template('order')
        else:
            html_content = template.html_content
        
        # معالجة القالب
        variables = {
            'customer_name': data['customer_name'],
            'order_number': data['order_number'],
            'order_date': data.get('order_date', datetime.now().strftime('%Y-%m-%d')),
            'total_amount': data['total_amount'],
            'order_status': data.get('order_status', 'تم الاستلام')
        }
        
        processed_content = TemplateProcessor.process_template(
            template or type('obj', (object,), {
                'html_content': html_content,
                'primary_color': '#007bff',
                'secondary_color': '#6c757d',
                'logo_url': None
            })(),
            variables,
            company
        )
        
        # إرسال البريد الإلكتروني
        email_sender = EmailSender(company)
        success, message = email_sender.send_email(
            data['email'],
            f'تفاصيل الطلب #{data["order_number"]}',
            processed_content,
            'order'
        )
        
        if success:
            # خصم التكلفة وتسجيل العملية
            company.deduct_message_cost()
            
            # تسجيل العملية
            log = EmailLog(
                company_id=company.id,
                service_id=2,
                template_id=template.id if template else None,
                recipient_email=data['email'],
                subject=f'تفاصيل الطلب #{data["order_number"]}',
                status='sent',
                cost=0 if company.free_messages_used <= current_app.config['FREE_MESSAGES_LIMIT'] else current_app.config['MESSAGE_PRICE'],
                was_free=company.free_messages_used <= current_app.config['FREE_MESSAGES_LIMIT']
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'تم إرسال تفاصيل الطلب بنجاح',
                'remaining_balance': company.balance,
                'free_messages_remaining': max(0, current_app.config['FREE_MESSAGES_LIMIT'] - company.free_messages_used)
            })
        else:
            return jsonify({
                'success': False,
                'error': f'فشل في إرسال البريد الإلكتروني: {message}',
                'code': 'SEND_FAILED'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}',
            'code': 'SERVER_ERROR'
        }), 500

@bp.route('/send-welcome', methods=['POST'])
@api_key_required
def send_welcome():
    """إرسال رسالة ترحيبية"""
    data = request.get_json()
    
    # التحقق من البيانات المطلوبة
    if not data or not data.get('email') or not data.get('customer_name'):
        return jsonify({
            'success': False,
            'error': 'البريد الإلكتروني واسم العميل مطلوبان',
            'code': 'FIELDS_REQUIRED'
        }), 400
    
    company = request.current_company
    
    # التحقق من إعدادات البريد الإلكتروني
    is_valid, error_msg = validate_email_settings(company)
    if not is_valid:
        return jsonify({
            'success': False,
            'error': error_msg,
            'code': 'EMAIL_SETTINGS_INCOMPLETE'
        }), 400
    
    # التحقق من إمكانية إرسال رسالة
    if not company.can_send_message():
        return jsonify({
            'success': False,
            'error': 'رصيدك غير كافي لإرسال رسائل',
            'code': 'INSUFFICIENT_BALANCE'
        }), 403
    
    try:
        # البحث عن قالب مخصص أو استخدام الافتراضي
        template = EmailTemplate.query.filter_by(
            company_id=company.id,
            service_id=3  # خدمة الرسائل الترحيبية
        ).first()
        
        if not template:
            html_content = TemplateProcessor.get_default_template('welcome')
        else:
            html_content = template.html_content
        
        # معالجة القالب
        variables = {
            'customer_name': data['customer_name']
        }
        
        processed_content = TemplateProcessor.process_template(
            template or type('obj', (object,), {
                'html_content': html_content,
                'primary_color': '#007bff',
                'secondary_color': '#6c757d',
                'logo_url': None
            })(),
            variables,
            company
        )
        
        # إرسال البريد الإلكتروني
        email_sender = EmailSender(company)
        success, message = email_sender.send_email(
            data['email'],
            f'مرحباً بك في {company.company_name}',
            processed_content,
            'welcome'
        )
        
        if success:
            # خصم التكلفة وتسجيل العملية
            company.deduct_message_cost()
            
            # تسجيل العملية
            log = EmailLog(
                company_id=company.id,
                service_id=3,
                template_id=template.id if template else None,
                recipient_email=data['email'],
                subject=f'مرحباً بك في {company.company_name}',
                status='sent',
                cost=0 if company.free_messages_used <= current_app.config['FREE_MESSAGES_LIMIT'] else current_app.config['MESSAGE_PRICE'],
                was_free=company.free_messages_used <= current_app.config['FREE_MESSAGES_LIMIT']
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'تم إرسال رسالة الترحيب بنجاح',
                'remaining_balance': company.balance,
                'free_messages_remaining': max(0, current_app.config['FREE_MESSAGES_LIMIT'] - company.free_messages_used)
            })
        else:
            return jsonify({
                'success': False,
                'error': f'فشل في إرسال البريد الإلكتروني: {message}',
                'code': 'SEND_FAILED'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}',
            'code': 'SERVER_ERROR'
        }), 500

@bp.route('/send-custom', methods=['POST'])
@api_key_required
def send_custom():
    """إرسال رسالة مخصصة"""
    data = request.get_json()
    
    # التحقق من البيانات المطلوبة
    required_fields = ['email', 'subject', 'message_content']
    for field in required_fields:
        if not data or not data.get(field):
            return jsonify({
                'success': False,
                'error': f'الحقل {field} مطلوب',
                'code': 'FIELD_REQUIRED'
            }), 400
    
    company = request.current_company
    
    # التحقق من إعدادات البريد الإلكتروني
    is_valid, error_msg = validate_email_settings(company)
    if not is_valid:
        return jsonify({
            'success': False,
            'error': error_msg,
            'code': 'EMAIL_SETTINGS_INCOMPLETE'
        }), 400
    
    # التحقق من إمكانية إرسال رسالة
    if not company.can_send_message():
        return jsonify({
            'success': False,
            'error': 'رصيدك غير كافي لإرسال رسائل',
            'code': 'INSUFFICIENT_BALANCE'
        }), 403
    
    try:
        # البحث عن قالب مخصص أو استخدام الافتراضي
        template = EmailTemplate.query.filter_by(
            company_id=company.id,
            service_id=4  # خدمة الرسائل العامة
        ).first()
        
        if not template:
            html_content = TemplateProcessor.get_default_template('general')
        else:
            html_content = template.html_content
        
        # معالجة القالب
        variables = {
            'message_title': data.get('message_title', data['subject']),
            'message_content': data['message_content']
        }
        
        processed_content = TemplateProcessor.process_template(
            template or type('obj', (object,), {
                'html_content': html_content,
                'primary_color': '#007bff',
                'secondary_color': '#6c757d',
                'logo_url': None
            })(),
            variables,
            company
        )
        
        # إرسال البريد الإلكتروني
        email_sender = EmailSender(company)
        success, message = email_sender.send_email(
            data['email'],
            data['subject'],
            processed_content,
            'general'
        )
        
        if success:
            # خصم التكلفة وتسجيل العملية
            company.deduct_message_cost()
            
            # تسجيل العملية
            log = EmailLog(
                company_id=company.id,
                service_id=4,
                template_id=template.id if template else None,
                recipient_email=data['email'],
                subject=data['subject'],
                status='sent',
                cost=0 if company.free_messages_used <= current_app.config['FREE_MESSAGES_LIMIT'] else current_app.config['MESSAGE_PRICE'],
                was_free=company.free_messages_used <= current_app.config['FREE_MESSAGES_LIMIT']
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'تم إرسال الرسالة بنجاح',
                'remaining_balance': company.balance,
                'free_messages_remaining': max(0, current_app.config['FREE_MESSAGES_LIMIT'] - company.free_messages_used)
            })
        else:
            return jsonify({
                'success': False,
                'error': f'فشل في إرسال البريد الإلكتروني: {message}',
                'code': 'SEND_FAILED'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}',
            'code': 'SERVER_ERROR'
        }), 500

@bp.route('/balance', methods=['GET'])
@api_key_required
def get_balance():
    """الحصول على معلومات الرصيد"""
    company = request.current_company
    
    return jsonify({
        'success': True,
        'balance': company.balance,
        'free_messages_used': company.free_messages_used,
        'free_messages_remaining': max(0, current_app.config['FREE_MESSAGES_LIMIT'] - company.free_messages_used),
        'total_messages_sent': company.total_messages_sent,
        'can_send_message': company.can_send_message()
    })

@bp.route('/services', methods=['GET'])
@api_key_required
def get_services():
    """الحصول على قائمة الخدمات المتاحة"""
    services = [
        {'code': 'verification', 'name': 'كود التحقق', 'endpoint': '/api/send-verification'},
        {'code': 'order', 'name': 'تفاصيل الطلب', 'endpoint': '/api/send-order'},
        {'code': 'welcome', 'name': 'رسالة ترحيبية', 'endpoint': '/api/send-welcome'},
        {'code': 'general', 'name': 'رسالة عامة', 'endpoint': '/api/send-custom'}
    ]
    
    return jsonify({
        'success': True,
        'services': services
    })

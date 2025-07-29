#!/usr/bin/env python3
"""
ملف تشغيل تطبيق Email Sender Pro
نظام إرسال الرسائل الإلكترونية للشركات
"""

from app import create_app, db
from app.models import Company, EmailService, CompanyService, EmailTemplate, EmailLog
from flask import current_app

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """إعطاء سياق للـ Shell"""
    return {
        'db': db,
        'Company': Company,
        'EmailService': EmailService,
        'CompanyService': CompanyService,
        'EmailTemplate': EmailTemplate,
        'EmailLog': EmailLog
    }

@app.cli.command()
def init_db():
    """إنشاء قاعدة البيانات وإدخال البيانات الأساسية"""
    print("🔄 إنشاء قاعدة البيانات...")
    db.create_all()
    
    # إضافة الخدمات الأساسية
    services = [
        {
            'service_code': 'verification',
            'service_name': 'كود التحقق',
            'description': 'إرسال أكواد التحقق الآمنة للمستخدمين'
        },
        {
            'service_code': 'order',
            'service_name': 'تفاصيل الطلبات',
            'description': 'إرسال فواتير وتفاصيل الطلبات للعملاء'
        },
        {
            'service_code': 'welcome',
            'service_name': 'رسائل ترحيبية',
            'description': 'إرسال رسائل ترحيب للعملاء الجدد'
        },
        {
            'service_code': 'general',
            'service_name': 'رسائل عامة',
            'description': 'إرسال رسائل مخصصة ومتنوعة'
        }
    ]
    
    for service_data in services:
        existing_service = EmailService.query.filter_by(service_code=service_data['service_code']).first()
        if not existing_service:
            service = EmailService(**service_data)
            db.session.add(service)
    
    db.session.commit()
    print("✅ تم إنشاء قاعدة البيانات بنجاح!")

@app.cli.command()
def create_admin():
    """إنشاء حساب إداري"""
    admin_email = input("البريد الإلكتروني للمدير: ")
    admin_password = input("كلمة المرور: ")
    company_name = input("اسم الشركة الإدارية: ")
    
    admin = Company(
        company_name=company_name,
        email=admin_email.lower()
    )
    admin.set_password(admin_password)
    admin.balance = 10000  # رصيد ابتدائي للمدير
    
    db.session.add(admin)
    db.session.commit()
    
    print(f"✅ تم إنشاء حساب المدير بنجاح!")
    print(f"📧 البريد: {admin_email}")
    print(f"🔑 API Key: {admin.api_key}")

if __name__ == '__main__':
    # إعدادات الإنتاج
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

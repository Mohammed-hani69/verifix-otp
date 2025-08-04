#!/usr/bin/env python3
"""
ملف التهيئة الأولية لقاعدة البيانات وإنشاء القوالب الافتراضية
"""

from app import create_app, db
from app.models import EmailTemplateBase, EmailService, Company
from app.utils.email_utils import create_default_templates
from datetime import datetime

def init_database():
    """تهيئة قاعدة البيانات وإنشاء البيانات الأولية"""
    app = create_app()
    
    with app.app_context():
        # إنشاء الجداول
        db.create_all()
        
        # إنشاء الخدمات الأساسية
        services = [
            {'service_code': 'verification', 'service_name': 'كود التحقق', 'description': 'إرسال رموز التحقق للمستخدمين'},
            {'service_code': 'welcome', 'service_name': 'رسائل الترحيب', 'description': 'رسائل ترحيب للمستخدمين الجدد'},
            {'service_code': 'order', 'service_name': 'تأكيد الطلبات', 'description': 'رسائل تأكيد الطلبات والمعاملات'},
            {'service_code': 'notification', 'service_name': 'الإشعارات', 'description': 'إشعارات عامة للمستخدمين'},
            {'service_code': 'marketing', 'service_name': 'التسويق', 'description': 'رسائل تسويقية وترويجية'},
        ]
        
        for service_data in services:
            service = EmailService.query.filter_by(service_code=service_data['service_code']).first()
            if not service:
                service = EmailService(**service_data)
                db.session.add(service)
        
        # إنشاء القوالب الافتراضية
        create_default_templates()
        
        # إنشاء حساب إداري افتراضي إذا لم يوجد
        admin = Company.query.filter_by(is_admin=True).first()
        if not admin:
            admin = Company(
                company_name='Verifix-OTP الإدارة',
                email='admin@verifix-otp.com',
                is_admin=True,
                is_verified=True,
                balance=10000.0
            )
            admin.set_password('admin123456')
            db.session.add(admin)
        
        db.session.commit()
        print("✅ تم تهيئة قاعدة البيانات بنجاح!")
        print("📧 حساب الإدارة: admin@verifix-otp.com")
        print("🔑 كلمة المرور: admin123456")
        print("🏢 اسم الموقع: Verifix-OTP")

if __name__ == '__main__':
    init_database()

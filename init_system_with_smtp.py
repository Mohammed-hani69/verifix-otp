#!/usr/bin/env python3
"""
تهيئة النظام - إنشاء قاعدة البيانات والمسؤول والإعدادات الأساسية
"""

from app import create_app, db
from app.models import Company, EmailService, EmailTemplateBase
from app.utils.email_utils import create_default_templates
import os

def init_system():
    """تهيئة النظام بالكامل"""
    app = create_app()
    
    with app.app_context():
        try:
            # حذف قاعدة البيانات إذا كانت موجودة وإعادة إنشائها
            db.drop_all()
            db.create_all()
            
            # إنشاء المسؤول الرئيسي
            admin_email = app.config.get('ADMIN_EMAIL', 'admin@verifix-otp.com')
            admin_password = app.config.get('ADMIN_PASSWORD', 'admin123456')
            
            admin = Company(
                company_name='Verifix-OTP Admin',
                email=admin_email,
                is_admin=True,
                is_verified=True,
                is_active=True,
                balance=10000.0,  # رصيد ابتدائي للمدير
                # إعدادات SMTP من .env
                smtp_server=app.config.get('MAIL_SERVER'),
                smtp_port=app.config.get('MAIL_PORT', 587),
                smtp_username=app.config.get('MAIL_USERNAME'),
                smtp_password=app.config.get('MAIL_PASSWORD'),
                sender_email=app.config.get('MAIL_USERNAME'),
                sender_name=app.config.get('COMPANY_NAME', 'Verifix-OTP')
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            
            # إنشاء الخدمات الأساسية
            services = [
                {
                    'name': 'OTP Verification',
                    'description': 'خدمة إرسال رموز التحقق',
                    'base_price': 0.25,
                    'is_active': True
                },
                {
                    'name': 'Email Marketing',
                    'description': 'خدمة التسويق عبر البريد الإلكتروني',
                    'base_price': 0.15,
                    'is_active': True
                },
                {
                    'name': 'Transactional Emails',
                    'description': 'رسائل العمليات التجارية',
                    'base_price': 0.20,
                    'is_active': True
                }
            ]
            
            for service_data in services:
                service = EmailService(**service_data)
                db.session.add(service)
            
            # حفظ التغييرات
            db.session.commit()
            
            # إنشاء القوالب الافتراضية
            create_default_templates()
            
            print("✅ تم تهيئة قاعدة البيانات بنجاح!")
            print(f"📧 بريد المدير: {admin_email}")
            print(f"🔑 كلمة مرور المدير: {admin_password}")
            print(f"📨 خادم SMTP: {app.config.get('MAIL_SERVER')}")
            print(f"👤 مستخدم SMTP: {app.config.get('MAIL_USERNAME')}")
            print("🎉 النظام جاهز للاستخدام!")
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في تهيئة النظام: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    init_system()

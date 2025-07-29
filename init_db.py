#!/usr/bin/env python3
"""
سكريبت إنشاء قاعدة البيانات
"""

import os
import sys
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# إضافة مسار المشروع إلى Python path
sys.path.append(os.path.dirname(__file__))

from app import create_app, db
from app.models import Company, EmailService, CompanyService, EmailTemplate, EmailLog

def init_database():
    """إنشاء قاعدة البيانات والبيانات الأساسية"""
    app = create_app()
    
    with app.app_context():
        print("🔄 إنشاء قاعدة البيانات...")
        
        # حذف الجداول الموجودة وإعادة إنشاؤها
        db.drop_all()
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
            service = EmailService(**service_data)
            db.session.add(service)
        
        db.session.commit()
        print("✅ تم إنشاء قاعدة البيانات والخدمات الأساسية بنجاح!")
        
        # إنشاء حساب المدير
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@yourcompany.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123456')
        company_name = os.environ.get('COMPANY_NAME', 'شركة الرسائل الذكية')
        
        # التحقق من عدم وجود المدير مسبقاً
        existing_admin = Company.query.filter_by(email=admin_email).first()
        if not existing_admin:
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
            print(f"🔑 كلمة المرور: {admin_password}")
            print(f"🔐 API Key: {admin.api_key}")
            
            # إنشاء اشتراكات الخدمات للمدير
            for service in EmailService.query.all():
                company_service = CompanyService(
                    company_id=admin.id,
                    service_id=service.id,
                    is_active=True
                )
                db.session.add(company_service)
            
            db.session.commit()
            print("✅ تم تفعيل جميع الخدمات للمدير!")
        else:
            print(f"⚠️ حساب المدير موجود مسبقاً: {admin_email}")

if __name__ == '__main__':
    init_database()

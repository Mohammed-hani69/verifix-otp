#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت للتحقق من إعدادات البريد الإلكتروني وإصلاح المشاكل
"""

from app import create_app, db
from app.models import Company, EmailTemplateBase
from app.utils.email_utils import send_verification_email
import os

def check_email_config():
    """التحقق من إعدادات البريد الإلكتروني"""
    app = create_app()
    with app.app_context():
        print("🔍 فحص إعدادات البريد الإلكتروني...")
        print("=" * 50)
        
        # 1. التحقق من إعدادات المدير
        admin = Company.query.filter_by(is_admin=True).first()
        if admin:
            print("👤 حساب المدير:")
            print(f"   البريد: {admin.email}")
            print(f"   SMTP Server: {admin.smtp_server}")
            print(f"   SMTP Port: {admin.smtp_port}")
            print(f"   SMTP Username: {admin.smtp_username}")
            print(f"   SMTP Password: {'✅ موجود' if admin.smtp_password else '❌ مفقود'}")
            print(f"   Sender Email: {admin.sender_email}")
            print(f"   Sender Name: {admin.sender_name}")
            print()
        else:
            print("❌ لم يتم العثور على حساب المدير")
            return False
        
        # 2. التحقق من متغيرات البيئة
        print("🌐 متغيرات البيئة:")
        env_vars = {
            'MAIL_SERVER': os.getenv('MAIL_SERVER'),
            'MAIL_PORT': os.getenv('MAIL_PORT'),
            'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
            'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD')
        }
        
        for key, value in env_vars.items():
            print(f"   {key}: {'✅ موجود' if value else '❌ مفقود'}")
        print()
        
        # 3. التحقق من قوالب البريد
        print("📧 قوالب البريد:")
        verification_template = EmailTemplateBase.query.filter_by(template_type='verification').first()
        welcome_template = EmailTemplateBase.query.filter_by(template_type='welcome').first()
        
        print(f"   قالب التحقق: {'✅ موجود' if verification_template else '❌ مفقود'}")
        print(f"   قالب الترحيب: {'✅ موجود' if welcome_template else '❌ مفقود'}")
        print()
        
        # 4. اختبار إرسال رسالة
        if admin and admin.smtp_server:
            print("🧪 اختبار إرسال رسالة...")
            try:
                success, message = send_verification_email(
                    admin.email,
                    "123456",
                    admin.company_name
                )
                
                if success:
                    print("✅ تم إرسال رسالة اختبار بنجاح!")
                else:
                    print(f"❌ فشل إرسال الرسالة: {message}")
                    
            except Exception as e:
                print(f"❌ خطأ في الاختبار: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("⚠️ لا يمكن اختبار الإرسال - إعدادات SMTP مفقودة")
        
        return True

def fix_email_config():
    """إصلاح إعدادات البريد الإلكتروني"""
    app = create_app()
    with app.app_context():
        print("🔧 إصلاح إعدادات البريد الإلكتروني...")
        
        # البحث عن المدير أو إنشاؤه
        admin = Company.query.filter_by(is_admin=True).first()
        if not admin:
            print("❌ لم يتم العثور على حساب المدير")
            return False
        
        # تحديث إعدادات SMTP من .env إذا كانت فارغة
        if not admin.smtp_server:
            admin.smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
            admin.smtp_port = int(os.getenv('MAIL_PORT', 587))
            admin.smtp_username = os.getenv('MAIL_USERNAME', 'hanizezo72@gmail.com')
            admin.smtp_password = os.getenv('MAIL_PASSWORD', 'jxtr qylc lzkj ehpb')
            admin.sender_email = admin.smtp_username
            admin.sender_name = 'Verifix-OTP'
            
            db.session.commit()
            print("✅ تم تحديث إعدادات SMTP للمدير")
        
        # إنشاء القوالب الافتراضية إذا لم تكن موجودة
        from app.utils.email_utils import create_default_templates
        try:
            create_default_templates()
            print("✅ تم التأكد من وجود قوالب البريد")
        except Exception as e:
            print(f"❌ خطأ في إنشاء القوالب: {e}")
        
        return True

def main():
    """الدالة الرئيسية"""
    print("🚀 فحص وإصلاح إعدادات البريد الإلكتروني")
    print("=" * 60)
    
    # فحص الإعدادات الحالية
    check_email_config()
    
    # إصلاح المشاكل
    print("\n" + "=" * 60)
    fix_email_config()
    
    # فحص مرة أخرى
    print("\n" + "=" * 60)
    print("🔍 فحص نهائي بعد الإصلاح:")
    check_email_config()

if __name__ == '__main__':
    main()

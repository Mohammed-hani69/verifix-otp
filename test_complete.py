#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار كامل للنظام
"""

import os
import sys

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Company
from app.utils.email_utils import send_admin_email, send_verification_email

def test_system():
    """اختبار شامل للنظام"""
    print("🔧 بدء اختبار النظام...")
    
    # إنشاء التطبيق
    app = create_app()
    
    with app.app_context():
        print("\n📋 فحص حساب المدير...")
        admin = Company.query.filter_by(is_admin=True).first()
        
        if not admin:
            print("❌ لا يوجد حساب مدير - سيتم إنشاؤه تلقائياً")
            return
        
        print("✅ تم العثور على حساب المدير:")
        print(f"   الاسم: {admin.company_name}")
        print(f"   البريد: {admin.email}")
        print(f"   SMTP Server: {admin.smtp_server}")
        print(f"   SMTP Port: {admin.smtp_port}")  
        print(f"   SMTP Username: {admin.smtp_username}")
        print(f"   Sender Email: {admin.sender_email}")
        print(f"   Sender Name: {admin.sender_name}")
        
        # اختبار إرسال بريد تحقق
        print("\n📧 اختبار إرسال رسالة تحقق...")
        try:
            success, message = send_verification_email(
                "test@example.com",
                "123456", 
                "شركة اختبار"
            )
            
            if success:
                print("✅ تم إرسال رسالة التحقق بنجاح!")
            else:
                print(f"❌ فشل إرسال رسالة التحقق: {message}")
                
        except Exception as e:
            print(f"❌ خطأ في إرسال رسالة التحقق: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_system()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار إعداد النظام والتحقق من أن الأمور تعمل بشكل صحيح
"""

import os
import sys
from app import create_app, db
from app.models import Company
from app.utils.email_utils import send_verification_email

def test_admin_account():
    """اختبار وجود حساب المدير"""
    print("🔍 اختبار حساب المدير...")
    
    admin = Company.query.filter_by(is_admin=True).first()
    if admin:
        print(f"✅ تم العثور على حساب المدير: {admin.email}")
        print(f"📧 إعدادات SMTP: {admin.smtp_server}:{admin.smtp_port}")
        print(f"👤 اسم المرسل: {admin.sender_name}")
        return True
    else:
        print("❌ لم يتم العثور على حساب مدير!")
        return False

def test_email_sending():
    """اختبار إرسال البريد الإلكتروني"""
    print("\n📧 اختبار إرسال البريد الإلكتروني...")
    
    try:
        # اختبار إرسال رسالة تحقق
        success, message = send_verification_email(
            "test@example.com", 
            "123456", 
            "شركة تجريبية"
        )
        
        if success:
            print("✅ تم إرسال رسالة الاختبار بنجاح!")
            return True
        else:
            print(f"❌ فشل إرسال رسالة الاختبار: {message}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في اختبار الإرسال: {e}")
        return False

def main():
    """تشغيل الاختبارات"""
    print("🚀 بدء اختبار النظام...")
    print("=" * 50)
    
    # إنشاء التطبيق
    app = create_app()
    
    with app.app_context():
        # اختبار حساب المدير
        admin_ok = test_admin_account()
        
        # اختبار إرسال البريد
        email_ok = test_email_sending()
        
        print("\n" + "=" * 50)
        print("📊 نتائج الاختبار:")
        print(f"🏛️  حساب المدير: {'✅ جاهز' if admin_ok else '❌ غير جاهز'}")
        print(f"📧 إرسال البريد: {'✅ يعمل' if email_ok else '❌ لا يعمل'}")
        
        if admin_ok and email_ok:
            print("\n🎉 النظام جاهز للعمل!")
        else:
            print("\n⚠️  يحتاج النظام إلى مراجعة!")

if __name__ == '__main__':
    main()

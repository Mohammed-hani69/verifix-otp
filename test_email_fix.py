#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار إرسال رسائل التحقق مع إصلاح مشكلة encoding
"""

import os
import sys
from app import create_app
from app.models import Company
from app.utils.email_utils import send_verification_email, send_admin_email

def test_email_with_arabic():
    """اختبار إرسال الرسائل مع الأحرف العربية"""
    app = create_app()
    
    with app.app_context():
        print("🧪 اختبار إرسال رسائل التحقق مع إصلاح encoding...")
        print("=" * 60)
        
        # البحث عن المدير
        admin = Company.query.filter_by(is_admin=True).first()
        
        if not admin:
            print("❌ لم يتم العثور على حساب المدير!")
            return False
        
        print("✅ تم العثور على حساب المدير:")
        print(f"   📧 البريد: {admin.email}")
        print(f"   📨 SMTP: {admin.smtp_server}:{admin.smtp_port}")
        print(f"   👤 المستخدم: {admin.smtp_username}")
        print(f"   📧 المرسل: {admin.sender_email}")
        print(f"   🏷️ اسم المرسل: {admin.sender_name}")
        
        # اختبار إرسال رسالة تحتوي على أحرف عربية
        test_email = "ezezo291@gmail.com"  # نفس الإيميل من الخطأ
        verification_code = "123456"
        company_name = "شركة اختبار عربية"  # اسم عربي للاختبار
        
        print(f"\n📨 إرسال رسالة اختبار إلى: {test_email}")
        print(f"🏢 اسم الشركة: {company_name}")
        print(f"🔢 كود التحقق: {verification_code}")
        
        try:
            # اختبار الدالة الجديدة
            success, message = send_verification_email(
                test_email,
                verification_code,
                company_name
            )
            
            if success:
                print("✅ تم إرسال رسالة الاختبار بنجاح!")
                print("📧 تحقق من بريدك الإلكتروني")
                print("🎉 تم حل مشكلة encoding الأحرف العربية!")
                return True
            else:
                print(f"❌ فشل إرسال الرسالة: {message}")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في إرسال الرسالة: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_admin_email_directly():
    """اختبار إرسال رسالة من المدير مباشرة"""
    app = create_app()
    
    with app.app_context():
        print("\n🔧 اختبار إرسال رسالة من المدير مباشرة...")
        print("=" * 50)
        
        test_email = "ezezo291@gmail.com"
        subject = "اختبار الرسائل العربية من Verifix-OTP"
        
        html_content = '''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>رسالة اختبار</title>
</head>
<body style="font-family: Arial, sans-serif; text-align: center; padding: 20px;">
    <h1 style="color: #28a745;">🎉 اختبار ناجح!</h1>
    <p style="font-size: 18px;">تم حل مشكلة encoding الأحرف العربية بنجاح</p>
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h2 style="color: #0066cc;">معلومات الاختبار:</h2>
        <p>✅ دعم كامل للغة العربية</p>
        <p>✅ تشفير UTF-8 محسّن</p>
        <p>✅ إرسال من حساب المدير</p>
        <p>✅ قوالب HTML متطورة</p>
    </div>
    <p style="color: #666; font-size: 14px;">© 2025 Verifix-OTP - جميع الحقوق محفوظة</p>
</body>
</html>
        '''
        
        try:
            success, message = send_admin_email(test_email, subject, html_content)
            
            if success:
                print("✅ تم إرسال رسالة الاختبار المباشرة بنجاح!")
                return True
            else:
                print(f"❌ فشل إرسال الرسالة المباشرة: {message}")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في إرسال الرسالة المباشرة: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    print("🚀 بدء اختبار إصلاح مشكلة encoding الأحرف العربية")
    print("=" * 70)
    
    # اختبار 1: رسالة التحقق
    result1 = test_email_with_arabic()
    
    # اختبار 2: رسالة مباشرة من المدير
    result2 = test_admin_email_directly()
    
    print("\n" + "=" * 70)
    print("📊 نتائج الاختبار:")
    print(f"   رسالة التحقق: {'✅ نجح' if result1 else '❌ فشل'}")
    print(f"   الرسالة المباشرة: {'✅ نجح' if result2 else '❌ فشل'}")
    
    if result1 and result2:
        print("\n🎉 تم حل مشكلة encoding بنجاح!")
        print("💡 الآن يمكن إرسال جميع الرسائل باللغة العربية دون مشاكل")
    else:
        print("\n⚠️ لا تزال هناك مشاكل في النظام")

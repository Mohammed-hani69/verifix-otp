#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت اختبار النظام الجديد
"""

from app import create_app, db
from app.models import Company
from app.utils.email_utils import send_verification_email

def test_system():
    """اختبار النظام"""
    print("🚀 اختبار النظام الجديد...")
    print("=" * 50)
    
    app = create_app()
    with app.app_context():
        print("✅ تم إنشاء التطبيق بنجاح!")
        
        # التحقق من وجود المدير
        admin = Company.query.filter_by(email='admin@verifix-otp.com').first()
        
        if admin:
            print("✅ تم العثور على حساب المدير:")
            print(f"   📧 البريد: {admin.email}")
            print(f"   🏢 الاسم: {admin.company_name}")
            print(f"   🔑 API Key: {admin.api_key}")
            print(f"   📨 SMTP Server: {admin.smtp_server}")
            print(f"   👤 SMTP Username: {admin.smtp_username}")
            print(f"   ✅ Is Admin: {admin.is_admin}")
            print(f"   ✅ Is Verified: {admin.is_verified}")
            print(f"   💰 Balance: {admin.balance}")
            
            # اختبار إرسال رسالة
            print("\n🧪 اختبار إرسال رسالة...")
            try:
                success, message = send_verification_email(
                    admin.email,
                    "123456",
                    "Test Company"
                )
                if success:
                    print("✅ تم إرسال رسالة الاختبار بنجاح!")
                else:
                    print(f"❌ فشل إرسال الرسالة: {message}")
            except Exception as e:
                print(f"❌ خطأ في اختبار الإرسال: {e}")
                
        else:
            print("❌ لم يتم العثور على حساب المدير!")
            
        # التحقق من عدد الشركات
        total_companies = Company.query.count()
        print(f"\n📊 إجمالي الشركات في النظام: {total_companies}")

if __name__ == '__main__':
    test_system()

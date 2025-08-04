#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريپت تشغيل وتجربة النظام
"""

import os
import sys

def run_app():
    """تشغيل التطبيق"""
    try:
        print("🚀 بدء تشغيل نظام Verifix-OTP...")
        print("=" * 50)
        
        # تحميل التطبيق
        from app import create_app
        app = create_app()
        
        print("✅ تم تحميل التطبيق بنجاح!")
        
        # التحقق من قاعدة البيانات
        with app.app_context():
            from app.models import Company, EmailService
            
            # فحص حساب المدير
            admin = Company.query.filter_by(email='admin@verifix-otp.com').first()
            
            if admin:
                print("\n✅ حساب المدير موجود:")
                print(f"   📧 البريد الإلكتروني: {admin.email}")
                print(f"   🏢 اسم الشركة: {admin.company_name}")
                print(f"   🔐 API Key: {admin.api_key}")
                print(f"   📨 خادم SMTP: {admin.smtp_server}")
                print(f"   👤 مستخدم SMTP: {admin.smtp_username}")
                print(f"   📧 بريد المرسل: {admin.sender_email}")
                print(f"   🏷️ اسم المرسل: {admin.sender_name}")
                print(f"   ✅ مدير: {admin.is_admin}")
                print(f"   ✅ مفعل: {admin.is_verified}")
                print(f"   💰 الرصيد: {admin.balance}")
            else:
                print("❌ حساب المدير غير موجود!")
            
            # فحص الخدمات
            services = EmailService.query.all()
            print(f"\n📊 عدد الخدمات المتاحة: {len(services)}")
            for service in services:
                print(f"   - {service.service_name}")
            
            # فحص إجمالي الشركات
            total_companies = Company.query.count()
            print(f"\n📈 إجمالي الشركات المسجلة: {total_companies}")
        
        print("\n🎉 النظام جاهز للاستخدام!")
        print("🌐 يمكنك الوصول للتطبيق على: http://localhost:5000")
        print("👤 معلومات تسجيل الدخول للمدير:")
        print("   📧 البريد: admin@verifix-otp.com")
        print("   🔑 كلمة المرور: zxc65432")
        
        # تشغيل الخادم
        print("\n🚀 بدء تشغيل الخادم...")
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_app()

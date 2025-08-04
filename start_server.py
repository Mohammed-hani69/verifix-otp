#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت تشغيل النظام مع اختبار الإصلاحات
"""

from app import create_app
from app.models import Company

def check_and_run():
    """فحص النظام وتشغيله"""
    app = create_app()
    
    with app.app_context():
        print("🔍 فحص حالة النظام...")
        
        # التحقق من المدير
        admin = Company.query.filter_by(is_admin=True).first()
        if admin:
            print(f"✅ حساب المدير موجود: {admin.email}")
            print(f"📧 إعدادات SMTP: {admin.smtp_server}:{admin.smtp_port}")
            print(f"👤 مستخدم SMTP: {admin.smtp_username}")
        else:
            print("❌ لا يوجد حساب مدير!")
            return
        
        print("\n🚀 تشغيل الخادم...")
        app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    check_and_run()

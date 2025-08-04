#!/usr/bin/env python3
"""
اختبار تحميل الإعدادات
"""

from app import create_app
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

def test_config():
    """اختبار تحميل الإعدادات"""
    app = create_app()
    
    with app.app_context():
        print("🧪 اختبار تحميل الإعدادات...")
        
        # اختبار إعدادات البريد
        mail_server = app.config.get('MAIL_SERVER')
        mail_username = app.config.get('MAIL_USERNAME')
        mail_password = app.config.get('MAIL_PASSWORD')
        
        print(f"📧 خادم البريد: {mail_server}")
        print(f"👤 اسم المستخدم: {mail_username}")
        print(f"🔐 كلمة المرور: {'موجودة' if mail_password else 'غير موجودة'}")
        
        # اختبار متغيرات البيئة مباشرة
        print(f"🌍 MAIL_SERVER من البيئة: {os.environ.get('MAIL_SERVER')}")
        print(f"🌍 MAIL_USERNAME من البيئة: {os.environ.get('MAIL_USERNAME')}")
        print(f"🌍 MAIL_PASSWORD من البيئة: {'موجودة' if os.environ.get('MAIL_PASSWORD') else 'غير موجودة'}")

if __name__ == '__main__':
    test_config()

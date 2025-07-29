#!/usr/bin/env python3
"""
تحديث إعدادات SMTP للمدير
"""

from app import create_app, db
from app.models import Company

def update_smtp_settings():
    app = create_app()
    with app.app_context():
        admin = Company.query.filter_by(email='admin@yourcompany.com').first()
        if admin:
            # تحديث إعدادات SMTP
            admin.smtp_server = 'smtp.gmail.com'
            admin.smtp_port = 587
            admin.smtp_username = 'hanizezo72@gmail.com'
            admin.smtp_password = 'jxtr qylc lzkj ehpb'
            admin.sender_email = 'hanizezo72@gmail.com'
            admin.sender_name = 'شركة الرسائل الذكية'
            
            db.session.commit()
            print('✅ تم تحديث إعدادات SMTP بنجاح!')
            print(f'🔐 API Key: {admin.api_key}')
            print(f'📧 SMTP Server: {admin.smtp_server}')
            print(f'👤 SMTP Username: {admin.smtp_username}')
            print(f'📮 Sender Email: {admin.sender_email}')
            print(f'🏢 Sender Name: {admin.sender_name}')
            return admin.api_key
        else:
            print('❌ لم يتم العثور على حساب المدير')
            return None

if __name__ == '__main__':
    api_key = update_smtp_settings()
    if api_key:
        print(f'\n🚀 النظام جاهز للإرسال! استخدم API Key: {api_key}')

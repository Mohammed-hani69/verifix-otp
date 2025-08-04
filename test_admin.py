#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models import Company

def test_admin():
    """اختبار حساب المدير"""
    app = create_app()
    with app.app_context():
        admin = Company.query.filter_by(is_admin=True).first()
        if admin:
            print('✅ تم العثور على حساب المدير:')
            print(f'   الاسم: {admin.company_name}')
            print(f'   البريد: {admin.email}')
            print(f'   SMTP Server: {admin.smtp_server}')
            print(f'   SMTP Port: {admin.smtp_port}')
            print(f'   SMTP Username: {admin.smtp_username}')
            if admin.smtp_password:
                print(f'   SMTP Password: {admin.smtp_password[:4] + "***"}')
            else:
                print('   SMTP Password: لا يوجد')
            print(f'   Sender Email: {admin.sender_email}')
            print(f'   Sender Name: {admin.sender_name}')
            print(f'   نشط: {admin.is_active}')
            print(f'   تم التحقق: {admin.is_verified}')
            
            # تجربة إرسال رسالة اختبار
            print('\n🧪 اختبار إرسال رسالة...')
            from app.utils.email_utils import send_admin_email
            
            success, message = send_admin_email(
                admin.email,  # إرسال للمدير نفسه
                "اختبار النظام - Verifix-OTP",
                """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #28a745; text-align: center;">اختبار النظام</h2>
                    <p>هذه رسالة اختبار من نظام Verifix-OTP</p>
                    <p>تم إرسال الرسالة بنجاح من حساب المدير</p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">نظام إرسال الرسائل الإلكترونية - Verifix-OTP</p>
                </div>
                """
            )
            
            if success:
                print(f'✅ تم إرسال رسالة الاختبار بنجاح: {message}')
            else:
                print(f'❌ فشل إرسال رسالة الاختبار: {message}')
        else:
            print('❌ لا يوجد حساب مدير!')

if __name__ == '__main__':
    test_admin()

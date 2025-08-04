#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار بسيط لحل مشكلة encoding
"""

from app import create_app
from app.models import Company
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def simple_test():
    """اختبار بسيط لإرسال رسالة عربية"""
    app = create_app()
    
    with app.app_context():
        print("🧪 اختبار إرسال رسالة عربية...")
        
        # الحصول على بيانات المدير
        admin = Company.query.filter_by(is_admin=True).first()
        if not admin:
            print("❌ لا يوجد حساب مدير")
            return
            
        print(f"✅ المدير: {admin.email}")
        
        # بيانات الاختبار
        to_email = "ezezo291@gmail.com"
        subject = "رسالة اختبار عربية من Verifix-OTP"
        
        # محتوى HTML عربي
        html_content = '''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>اختبار</title>
</head>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <h1 style="color: #28a745;">مرحباً من Verifix-OTP</h1>
    <p>هذه رسالة اختبار لحل مشكلة encoding الأحرف العربية.</p>
    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3>معلومات الاختبار:</h3>
        <p>✅ دعم اللغة العربية</p>
        <p>✅ تشفير UTF-8</p>
        <p>✅ إرسال من حساب المدير</p>
    </div>
    <p style="color: #666;">© 2025 Verifix-OTP</p>
</body>
</html>
        '''
        
        try:
            # إنشاء الرسالة مع UTF-8
            msg = MIMEMultipart('alternative')
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = Header(f"{admin.sender_name} <{admin.sender_email}>", 'utf-8')
            msg['To'] = Header(to_email, 'utf-8')
            
            # إضافة المحتوى
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            print("📨 محاولة الإرسال...")
            
            # الإرسال
            with smtplib.SMTP(admin.smtp_server, admin.smtp_port) as server:
                server.starttls()
                server.login(admin.smtp_username, admin.smtp_password)
                text = msg.as_string()
                if isinstance(text, str):
                    text = text.encode('utf-8')
                server.sendmail(admin.sender_email, to_email, text)
            
            print("✅ تم الإرسال بنجاح!")
            print("🎉 تم حل مشكلة encoding!")
            
        except Exception as e:
            print(f"❌ خطأ: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    simple_test()

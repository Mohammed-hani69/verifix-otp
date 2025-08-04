#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار إرسال البريد الإلكتروني مع إصلاح المشاكل
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr

def test_direct_smtp():
    """اختبار إرسال البريد مباشرة"""
    print("🧪 اختبار SMTP مباشرة...")
    
    # إعدادات SMTP
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    username = 'hanizezo72@gmail.com'
    password = 'jxtr qylc lzkj ehpb'
    
    # إعداد الرسالة
    msg = MIMEMultipart('alternative')
    msg['Subject'] = Header('اختبار من Verifix-OTP', 'utf-8')
    msg['From'] = formataddr(('Verifix-OTP', username))
    msg['To'] = username  # إرسال للمرسل نفسه للاختبار
    
    # محتوى HTML
    html_content = """
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #28a745; text-align: center;">اختبار النظام</h2>
        <p>هذه رسالة اختبار من نظام Verifix-OTP</p>
        <p><strong>كود التحقق:</strong> 123456</p>
        <hr>
        <p style="color: #666; font-size: 12px;">نظام إرسال الرسائل الإلكترونية - Verifix-OTP</p>
    </div>
    """
    
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(html_part)
    
    try:
        # إرسال الرسالة
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg, from_addr=username, to_addrs=[username])
            
        print("✅ تم إرسال رسالة الاختبار بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ فشل إرسال رسالة الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_email():
    """اختبار إرسال البريد عبر النظام"""
    print("\n🧪 اختبار إرسال البريد عبر النظام...")
    
    try:
        import os
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from app import create_app, db
        from app.models import Company
        from app.utils.email_utils import send_admin_email
        
        app = create_app()
        with app.app_context():
            admin = Company.query.filter_by(is_admin=True).first()
            
            if not admin:
                print("❌ لا يوجد حساب مدير")
                return False
                
            print("✅ تم العثور على حساب المدير")
            
            # اختبار إرسال رسالة
            success, message = send_admin_email(
                admin.email,
                "اختبار النظام - Verifix-OTP",
                """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #dc3545; text-align: center;">اختبار النظام</h2>
                    <p>هذه رسالة اختبار من نظام Verifix-OTP</p>
                    <p><strong>حالة النظام:</strong> يعمل بشكل طبيعي</p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">نظام إرسال الرسائل الإلكترونية - Verifix-OTP</p>
                </div>
                """
            )
            
            if success:
                print("✅ تم إرسال رسالة النظام بنجاح!")
                return True
            else:
                print(f"❌ فشل إرسال رسالة النظام: {message}")
                return False
                
    except Exception as e:
        print(f"❌ خطأ في اختبار النظام: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 بدء اختبار شامل للبريد الإلكتروني")
    print("=" * 50)
    
    # اختبار SMTP مباشرة
    direct_test = test_direct_smtp()
    
    # اختبار النظام
    system_test = test_system_email()
    
    print("\n" + "=" * 50)
    print("📊 نتائج الاختبار:")
    print(f"   اختبار SMTP مباشر: {'✅ نجح' if direct_test else '❌ فشل'}")
    print(f"   اختبار النظام: {'✅ نجح' if system_test else '❌ فشل'}")
    
    if direct_test and system_test:
        print("\n🎉 جميع الاختبارات نجحت! النظام جاهز للعمل")
    elif direct_test:
        print("\n⚠️ SMTP يعمل لكن هناك مشكلة في النظام")
    else:
        print("\n❌ هناك مشكلة في إعدادات SMTP")

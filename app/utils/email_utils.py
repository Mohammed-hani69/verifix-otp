import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from flask import current_app, render_template_string
from app.models import EmailTemplateBase, Company
import sys


def send_email(to_email, subject, html_content, company=None):
    """إرسال بريد إلكتروني عبر SMTP مع دعم كامل للأحرف العربية"""
    try:
        # استخدام إعدادات الشركة أو الإعدادات العامة
        if company and company.smtp_server:
            smtp_server = company.smtp_server
            smtp_port = company.smtp_port
            smtp_username = company.smtp_username
            smtp_password = company.smtp_password
            sender_email = company.sender_email
            sender_name = company.sender_name or 'Verifix-OTP'
        else:
            # استخدام إعدادات النظام الافتراضية من .env أو admin
            admin = Company.query.filter_by(is_admin=True).first()
            if admin and admin.smtp_server:
                smtp_server = admin.smtp_server
                smtp_port = admin.smtp_port
                smtp_username = admin.smtp_username
                smtp_password = admin.smtp_password
                sender_email = admin.sender_email
                sender_name = admin.sender_name or 'Verifix-OTP'
            else:
                # استخدام إعدادات من .env
                smtp_server = current_app.config.get('MAIL_SERVER')
                smtp_port = current_app.config.get('MAIL_PORT', 587)
                smtp_username = current_app.config.get('MAIL_USERNAME')
                smtp_password = current_app.config.get('MAIL_PASSWORD')
                sender_email = smtp_username or current_app.config.get('ADMIN_EMAIL')
                sender_name = current_app.config.get('COMPANY_NAME', 'Verifix-OTP')
                
                if not smtp_server or not smtp_username or not smtp_password:
                    raise Exception("لا توجد إعدادات SMTP متاحة في التكوين")

        # إنشاء الرسالة مع دعم UTF-8 الكامل
        msg = MIMEMultipart('alternative')
        
        # تشفير العنوان والمرسل باستخدام UTF-8
        msg['Subject'] = Header(subject, 'utf-8').encode()
        msg['From'] = Header(f"{sender_name} <{sender_email}>", 'utf-8').encode()
        msg['To'] = to_email
        msg.set_charset('utf-8')

        # إضافة المحتوى HTML مع تشفير UTF-8
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)

        # إرسال الرسالة مع دعم UTF-8 الكامل
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            # إرسال الرسالة مع التشفير الصحيح
            server.sendmail(sender_email, [to_email], msg.as_bytes())

        return True, "تم إرسال الرسالة بنجاح"

    except Exception as e:
        error_msg = str(e)
        print(f"خطأ في إرسال البريد الإلكتروني: {error_msg}")
        return False, error_msg


def send_admin_email(to_email, subject, html_content):
    """إرسال رسالة من حساب المدير فقط - للرسائل الإدارية"""
    try:
        # الحصول على حساب المدير
        admin = Company.query.filter_by(is_admin=True).first()
        if not admin:
            return False, "لا يوجد حساب مدير مكوّن في النظام"
        
        if not admin.smtp_server or not admin.smtp_username or not admin.smtp_password:
            return False, "إعدادات SMTP للمدير غير مكتملة"
        
        return send_email(to_email, subject, html_content, company=admin)
        
    except Exception as e:
        print(f"خطأ في إرسال رسالة المدير: {e}")
        return False, str(e)


def get_email_template(template_type):
    """الحصول على قالب البريد"""
    template = EmailTemplateBase.query.filter_by(
        template_type=template_type,
        is_active=True
    ).first()
    
    if not template:
        # قالب افتراضي بسيط
        return {
            'subject': 'رسالة من Verifix-OTP',
            'html_content': '''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #28a745;">{{subject}}</h2>
                <p>{{content}}</p>
                <p>مع تحيات فريق Verifix-OTP</p>
            </div>
            '''
        }
    
    return {
        'subject': template.subject,
        'html_content': template.html_content
    }


def send_verification_email(to_email, verification_code, company_name):
    """إرسال رسالة كود التحقق - دائماً من حساب المدير"""
    try:
        template = get_email_template('verification')
        
        # استبدال المتغيرات في القالب
        subject = template['subject'].replace('{{company_name}}', company_name)
        subject = subject.replace('{{site_name}}', 'Verifix-OTP')
        
        html_content = template['html_content'].replace('{{company_name}}', company_name)
        html_content = html_content.replace('{{verification_code}}', verification_code)
        html_content = html_content.replace('{{site_name}}', 'Verifix-OTP')
        html_content = html_content.replace('{{current_year}}', str(current_app.config.get('CURRENT_YEAR', 2025)))
        
        # إرسال من حساب المدير فقط
        return send_admin_email(to_email, subject, html_content)
        
    except Exception as e:
        error_msg = f"خطأ في إنشاء رسالة التحقق: {e}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return False, error_msg


def send_welcome_email(to_email, company_name):
    """إرسال رسالة ترحيبية - دائماً من حساب المدير"""
    try:
        template = get_email_template('welcome')
        
        # استبدال المتغيرات في القالب
        subject = template['subject'].replace('{{company_name}}', company_name)
        subject = subject.replace('{{site_name}}', 'Verifix-OTP')
        
        html_content = template['html_content'].replace('{{company_name}}', company_name)
        html_content = html_content.replace('{{site_name}}', 'Verifix-OTP')
        html_content = html_content.replace('{{current_year}}', str(current_app.config.get('CURRENT_YEAR', 2025)))
        
        # إرسال من حساب المدير فقط
        return send_admin_email(to_email, subject, html_content)
        
    except Exception as e:
        error_msg = f"خطأ في إنشاء رسالة الترحيب: {e}"
        print(error_msg)
        return False, error_msg


def send_low_balance_notification(to_email, company_name, current_balance):
    """إرسال تنبيه نقص الرصيد - من حساب المدير"""
    try:
        subject = f"تنبيه: انخفاض رصيد الرسائل - {company_name}"
        
        html_content = f'''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تنبيه انخفاض الرصيد</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 15px; overflow: hidden; box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%); padding: 30px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 28px; font-weight: bold;">⚠️ تنبيه مهم</h1>
            <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">انخفاض رصيد الرسائل</p>
        </div>
        
        <!-- Content -->
        <div style="padding: 40px 30px;">
            <h2 style="color: #dc3545; margin-bottom: 20px; font-size: 24px;">عزيزي {company_name}</h2>
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 20px; color: #333;">
                نود إعلامك بأن رصيد الرسائل في حسابك أصبح منخفضاً.
            </p>
            
            <!-- Balance Info -->
            <div style="background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 10px; padding: 20px; text-align: center; margin: 30px 0;">
                <p style="margin: 0 0 10px 0; font-size: 14px; color: #856404;">الرصيد الحالي:</p>
                <span style="font-size: 32px; font-weight: bold; color: #dc3545;">{current_balance}</span>
                <span style="font-size: 16px; color: #856404;"> رسالة</span>
            </div>
            
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 20px; color: #333;">
                يرجى إعادة شحن رصيدك لضمان استمرار الخدمة دون انقطاع.
            </p>
            
            <div style="text-align: center; margin: 30px 0;">
                <p style="font-size: 14px; color: #6c757d;">
                    للمزيد من المعلومات، يرجى تسجيل الدخول إلى حسابك
                </p>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #dee2e6;">
            <p style="margin: 0 0 10px 0; color: #6c757d; font-size: 14px;">
                © 2025 Verifix-OTP - جميع الحقوق محفوظة
            </p>
        </div>
    </div>
</body>
</html>
        '''
        
        # إرسال من حساب المدير
        return send_admin_email(to_email, subject, html_content)
        
    except Exception as e:
        error_msg = f"خطأ في إرسال تنبيه الرصيد: {e}"
        print(error_msg)
        return False, error_msg


def create_default_templates():
    """إنشاء القوالب الافتراضية للنظام"""
    from app import db
    
    # قالب كود التحقق
    verification_template = EmailTemplateBase.query.filter_by(template_type='verification').first()
    if not verification_template:
        verification_template = EmailTemplateBase(
            template_type='verification',
            template_name='قالب كود التحقق',
            subject='كود التحقق من {{site_name}}',
            html_content='''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>كود التحقق</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 15px; overflow: hidden; box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 30px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 28px; font-weight: bold;">{{site_name}}</h1>
            <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">خدمات البريد الإلكتروني المتقدمة</p>
        </div>
        
        <!-- Content -->
        <div style="padding: 40px 30px;">
            <h2 style="color: #28a745; margin-bottom: 20px; font-size: 24px;">مرحباً بك في {{site_name}}</h2>
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 20px; color: #333;">
                شكراً لك على التسجيل في منصتنا. لإكمال عملية التحقق من حسابك، يرجى إدخال الكود التالي:
            </p>
            
            <!-- Verification Code Box -->
            <div style="background-color: #f8f9fa; border: 3px dashed #28a745; border-radius: 15px; padding: 30px; text-align: center; margin: 30px 0;">
                <p style="margin: 0 0 10px 0; font-size: 14px; color: #6c757d;">كود التحقق الخاص بك:</p>
                <span style="font-size: 42px; font-weight: bold; color: #28a745; letter-spacing: 8px; font-family: 'Courier New', monospace;">{{verification_code}}</span>
            </div>
            
            <div style="background-color: #e7f3ff; border-left: 4px solid #0066cc; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0; font-size: 14px; color: #0066cc;">
                    <strong>ملاحظة:</strong> هذا الكود صالح لمدة 10 دقائق فقط. يرجى عدم مشاركته مع أي شخص آخر.
                </p>
            </div>
            
            <p style="font-size: 16px; line-height: 1.6; margin-top: 30px; color: #333;">
                إذا لم تقم بإنشاء هذا الحساب، يرجى تجاهل هذه الرسالة.
            </p>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #dee2e6;">
            <p style="margin: 0 0 10px 0; color: #6c757d; font-size: 14px;">
                © {{current_year}} {{site_name}} - جميع الحقوق محفوظة
            </p>
            <p style="margin: 0; color: #6c757d; font-size: 12px;">
                هذه رسالة آلية، يرجى عدم الرد عليها
            </p>
        </div>
    </div>
</body>
</html>
            ''',
            primary_color='#28a745',
            secondary_color='#ffffff'
        )
        db.session.add(verification_template)
    
    # قالب الترحيب
    welcome_template = EmailTemplateBase.query.filter_by(template_type='welcome').first()
    if not welcome_template:
        welcome_template = EmailTemplateBase(
            template_type='welcome',
            template_name='قالب الترحيب',
            subject='مرحباً بك في {{site_name}} - {{company_name}}',
            html_content='''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مرحباً بك</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 15px; overflow: hidden; box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 40px 30px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 32px; font-weight: bold;">{{site_name}}</h1>
            <p style="margin: 15px 0 0 0; font-size: 18px; opacity: 0.9;">منصة خدمات البريد الإلكتروني</p>
        </div>
        
        <!-- Welcome Icon -->
        <div style="text-align: center; padding: 30px 0 0 0;">
            <div style="width: 80px; height: 80px; background-color: #28a745; border-radius: 50%; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
                <span style="color: white; font-size: 36px;">🎉</span>
            </div>
        </div>
        
        <!-- Content -->
        <div style="padding: 30px 40px 40px 40px; text-align: center;">
            <h2 style="color: #28a745; margin-bottom: 20px; font-size: 28px;">مرحباً بك {{company_name}}!</h2>
            <p style="font-size: 18px; line-height: 1.6; margin-bottom: 30px; color: #333;">
                نحن سعداء جداً لانضمامك إلى عائلة {{site_name}}
            </p>
            
            <!-- Features -->
            <div style="background-color: #f8f9fa; border-radius: 10px; padding: 30px; margin: 30px 0; text-align: right;">
                <h3 style="color: #28a745; margin-bottom: 20px; text-align: center;">ماذا يمكنك فعله الآن؟</h3>
                <div style="margin-bottom: 15px;">
                    <span style="color: #28a745; font-size: 18px;">✓</span>
                    <span style="margin-right: 10px; font-size: 16px;">إرسال رسائل التحقق بسهولة</span>
                </div>
                <div style="margin-bottom: 15px;">
                    <span style="color: #28a745; font-size: 18px;">✓</span>
                    <span style="margin-right: 10px; font-size: 16px;">إدارة قوالب البريد الإلكتروني</span>
                </div>
                <div style="margin-bottom: 15px;">
                    <span style="color: #28a745; font-size: 18px;">✓</span>
                    <span style="margin-right: 10px; font-size: 16px;">متابعة إحصائيات الإرسال</span>
                </div>
                <div>
                    <span style="color: #28a745; font-size: 18px;">✓</span>
                    <span style="margin-right: 10px; font-size: 16px;">الحصول على 1000 رسالة مجانية</span>
                </div>
            </div>
            
            <!-- Bonus -->
            <div style="background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%); color: white; border-radius: 10px; padding: 20px; margin: 20px 0;">
                <h4 style="margin: 0 0 10px 0; font-size: 20px;">🎁 مكافأة الترحيب</h4>
                <p style="margin: 0; font-size: 16px;">لقد حصلت على 1000 رسالة مجانية للبدء!</p>
            </div>
            
            <p style="font-size: 16px; line-height: 1.6; margin-top: 30px; color: #666;">
                إذا كان لديك أي استفسار، لا تتردد في التواصل معنا.
            </p>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #dee2e6;">
            <p style="margin: 0 0 10px 0; color: #6c757d; font-size: 14px;">
                © {{current_year}} {{site_name}} - جميع الحقوق محفوظة
            </p>
            <p style="margin: 0; color: #6c757d; font-size: 12px;">
                شكراً لك على اختيار خدماتنا
            </p>
        </div>
    </div>
</body>
</html>
            ''',
            primary_color='#28a745',
            secondary_color='#ffffff'
        )
        db.session.add(welcome_template)
    
    db.session.commit()
    return True
    
    html_content = template['html_content'].replace('{{company_name}}', company_name)
    html_content = html_content.replace('{{site_name}}', 'Verifix-OTP')
    html_content = html_content.replace('{{free_messages}}', '1000')
    
    return send_email(to_email, subject, html_content)

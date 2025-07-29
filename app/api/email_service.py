import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from flask import current_app
import re
import random
import string
from datetime import datetime

class EmailSender:
    """فئة إرسال البريد الإلكتروني"""
    
    def __init__(self, company):
        self.company = company
    
    def send_email(self, recipient_email, subject, html_content, service_code='general'):
        """إرسال بريد إلكتروني"""
        try:
            # إنشاء الرسالة
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.company.sender_name} <{self.company.sender_email}>"
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # إضافة المحتوى HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # الاتصال بخادم SMTP وإرسال الرسالة
            with smtplib.SMTP(self.company.smtp_server, self.company.smtp_port) as server:
                server.starttls()
                server.login(self.company.smtp_username, self.company.smtp_password)
                server.send_message(msg)
            
            return True, "تم إرسال الرسالة بنجاح"
            
        except Exception as e:
            return False, str(e)

class TemplateProcessor:
    """معالج القوالب"""
    
    @staticmethod
    def generate_verification_code(length=6):
        """إنتاج كود التحقق"""
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def process_template(template, variables, company):
        """معالجة القالب واستبدال المتغيرات"""
        html_content = template.html_content
        
        # استبدال المتغيرات الأساسية
        html_content = html_content.replace('{{company_name}}', company.company_name)
        html_content = html_content.replace('{{current_year}}', str(datetime.now().year))
        
        # استبدال المتغيرات المخصصة
        for key, value in variables.items():
            placeholder = '{{' + key + '}}'
            html_content = html_content.replace(placeholder, str(value))
        
        # إضافة الألوان المخصصة
        html_content = html_content.replace('{{primary_color}}', template.primary_color)
        html_content = html_content.replace('{{secondary_color}}', template.secondary_color)
        
        # إضافة الشعار إذا كان متوفراً
        if template.logo_url:
            logo_html = f'<img src="{template.logo_url}" alt="شعار الشركة" style="max-height: 60px;">'
            html_content = html_content.replace('{{logo}}', logo_html)
        else:
            html_content = html_content.replace('{{logo}}', '')
        
        # إضافة اسم الشركة في النهاية للحسابات المجانية
        if company.free_messages_used < current_app.config['FREE_MESSAGES_LIMIT']:
            footer_text = f"<br><hr><p style='color: #888; font-size: 12px; text-align: center;'>مدعوم من {current_app.config['COMPANY_NAME']}</p>"
            html_content += footer_text
        
        return html_content
    
    @staticmethod
    def get_default_template(service_code, primary_color='#007bff', secondary_color='#6c757d'):
        """الحصول على القالب الافتراضي حسب نوع الخدمة"""
        
        base_template = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{{{subject}}}}</title>
        </head>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    {{{{logo}}}}
                    <h1 style="margin: 10px 0 0 0; font-size: 24px;">{{{{company_name}}}}</h1>
                </div>
                <div style="padding: 30px;">
                    {'{'}content{'}'}
                </div>
                <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; color: #6c757d; font-size: 14px;">
                    <p>© {{{{current_year}}}} {{{{company_name}}}}. جميع الحقوق محفوظة.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        if service_code == 'verification':
            content = """
            <h2 style="color: {primary_color}; margin-bottom: 20px;">كود التحقق</h2>
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 20px;">مرحباً،</p>
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 30px;">كود التحقق الخاص بك هو:</p>
            <div style="background-color: #f8f9fa; border: 2px dashed {primary_color}; border-radius: 10px; padding: 20px; text-align: center; margin: 30px 0;">
                <span style="font-size: 36px; font-weight: bold; color: {primary_color}; letter-spacing: 5px;">{{{{verification_code}}}}</span>
            </div>
            <p style="font-size: 14px; color: #6c757d; margin-top: 20px;">هذا الكود صالح لمدة محدودة. يرجى عدم مشاركته مع أي شخص آخر.</p>
            """
        
        elif service_code == 'order':
            content = """
            <h2 style="color: {primary_color}; margin-bottom: 20px;">تفاصيل الطلب</h2>
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 20px;">عزيزي {{{{customer_name}}}},</p>
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 20px;">شكراً لك على طلبك. إليك التفاصيل:</p>
            <div style="background-color: #f8f9fa; border-radius: 10px; padding: 20px; margin: 20px 0;">
                <p><strong>رقم الطلب:</strong> {{{{order_number}}}}</p>
                <p><strong>تاريخ الطلب:</strong> {{{{order_date}}}}</p>
                <p><strong>المبلغ الإجمالي:</strong> {{{{total_amount}}}} جنيه</p>
                <p><strong>حالة الطلب:</strong> {{{{order_status}}}}</p>
            </div>
            <p style="font-size: 16px; line-height: 1.6;">سنقوم بتحديثك بأي تطورات على طلبك.</p>
            """
        
        elif service_code == 'welcome':
            content = """
            <h2 style="color: {primary_color}; margin-bottom: 20px;">مرحباً بك!</h2>
            <p style="font-size: 18px; line-height: 1.8; margin-bottom: 20px;">أهلاً وسهلاً {{{{customer_name}}}},</p>
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 20px;">نحن سعداء جداً بانضمامك إلينا! مرحباً بك في عائلة {{{{company_name}}}}.</p>
            <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); border-radius: 10px; padding: 25px; margin: 25px 0; text-align: center;">
                <h3 style="color: {primary_color}; margin: 0 0 15px 0;">نصائح للبداية:</h3>
                <ul style="list-style: none; padding: 0; margin: 0;">
                    <li style="margin: 10px 0;">✓ اكتشف خدماتنا المميزة</li>
                    <li style="margin: 10px 0;">✓ تواصل معنا إذا كان لديك أي استفسار</li>
                    <li style="margin: 10px 0;">✓ ابق على اطلاع بآخر العروض</li>
                </ul>
            </div>
            <p style="font-size: 16px; line-height: 1.6;">نتطلع إلى خدمتك وتقديم أفضل تجربة ممكنة.</p>
            """
        
        else:  # general
            content = """
            <h2 style="color: {primary_color}; margin-bottom: 20px;">{{{{message_title}}}}</h2>
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 20px;">{{{{message_content}}}}</p>
            """
        
        return base_template.replace('{content}', content).format(
            primary_color=primary_color,
            secondary_color=secondary_color
        )

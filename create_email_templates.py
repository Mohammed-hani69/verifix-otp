"""
إنشاء قوالب البريد الافتراضية
"""

from app import create_app, db
from app.models import EmailTemplateBase

def create_default_templates():
    """إنشاء قوالب البريد الافتراضية"""
    app = create_app()
    with app.app_context():
        
        # قالب كود التحقق
        verification_template = EmailTemplateBase(
            template_type='verification',
            template_name='كود التحقق',
            subject='كود التفعيل - {{company_name}} | Verifix-OTP',
            html_content='''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>كود التفعيل</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 40px 30px; text-align: center;">
            <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">
                Verifix-OTP
            </h1>
            <p style="color: #ffffff; margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">
                منصة إرسال رسائل التحقق الموثوقة
            </p>
        </div>
        
        <!-- Content -->
        <div style="padding: 40px 30px;">
            <h2 style="color: #28a745; margin: 0 0 20px 0; font-size: 24px;">
                مرحباً {{company_name}}
            </h2>
            
            <p style="color: #6c757d; line-height: 1.6; margin: 0 0 30px 0; font-size: 16px;">
                شكراً لتسجيلك في منصة Verifix-OTP. لإتمام عملية التفعيل، يرجى استخدام كود التحقق التالي:
            </p>
            
            <!-- Verification Code -->
            <div style="background-color: #f8f9fa; border: 2px dashed #28a745; border-radius: 10px; padding: 30px; text-align: center; margin: 30px 0;">
                <p style="color: #6c757d; margin: 0 0 10px 0; font-size: 14px;">
                    كود التفعيل الخاص بك:
                </p>
                <div style="font-size: 36px; font-weight: bold; color: #28a745; letter-spacing: 5px; font-family: 'Courier New', monospace;">
                    {{verification_code}}
                </div>
                <p style="color: #dc3545; margin: 15px 0 0 0; font-size: 12px;">
                    صالح لمدة 10 دقائق فقط
                </p>
            </div>
            
            <div style="background-color: #e3f2fd; border-radius: 8px; padding: 20px; margin: 30px 0;">
                <h3 style="color: #1976d2; margin: 0 0 10px 0; font-size: 16px;">
                    💡 نصائح مهمة:
                </h3>
                <ul style="color: #424242; margin: 0; padding-right: 20px; line-height: 1.6;">
                    <li>لا تشارك هذا الكود مع أي شخص</li>
                    <li>استخدم الكود خلال 10 دقائق من استلامه</li>
                    <li>إذا لم تطلب هذا الكود، تجاهل هذه الرسالة</li>
                </ul>
            </div>
            
            <p style="color: #6c757d; line-height: 1.6; margin: 30px 0 0 0; font-size: 14px;">
                إذا واجهت أي مشكلة، لا تتردد في التواصل معنا.
            </p>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e9ecef;">
            <p style="color: #6c757d; margin: 0 0 10px 0; font-size: 14px;">
                مع تحيات فريق Verifix-OTP
            </p>
            <p style="color: #adb5bd; margin: 0; font-size: 12px;">
                هذه رسالة تلقائية، يرجى عدم الرد عليها
            </p>
        </div>
        
    </div>
</body>
</html>
            ''',
            primary_color='#28a745',
            secondary_color='#ffffff'
        )
        
        # قالب الترحيب
        welcome_template = EmailTemplateBase(
            template_type='welcome',
            template_name='رسالة ترحيبية',
            subject='مرحباً بك في Verifix-OTP - {{company_name}}',
            html_content='''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مرحباً بك</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 40px 30px; text-align: center;">
            <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">
                🎉 مرحباً بك في Verifix-OTP
            </h1>
            <p style="color: #ffffff; margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">
                منصة إرسال رسائل التحقق الموثوقة والآمنة
            </p>
        </div>
        
        <!-- Content -->
        <div style="padding: 40px 30px;">
            <h2 style="color: #28a745; margin: 0 0 20px 0; font-size: 24px;">
                أهلاً وسهلاً {{company_name}} 👋
            </h2>
            
            <p style="color: #6c757d; line-height: 1.6; margin: 0 0 30px 0; font-size: 16px;">
                تم تفعيل حسابك بنجاح! نحن سعداء لانضمامك إلى منصة Verifix-OTP، المنصة الرائدة في إرسال رسائل التحقق والإشعارات.
            </p>
            
            <!-- Gift Box -->
            <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); border-radius: 15px; padding: 30px; text-align: center; margin: 30px 0; border: 2px solid #f39c12;">
                <div style="font-size: 48px; margin-bottom: 15px;">🎁</div>
                <h3 style="color: #d68910; margin: 0 0 10px 0; font-size: 20px;">
                    هدية ترحيبية خاصة!
                </h3>
                <p style="color: #b7950b; margin: 0 0 15px 0; font-size: 16px; font-weight: bold;">
                    {{free_messages}} رسالة مجانية في انتظارك!
                </p>
                <p style="color: #8b7355; margin: 0; font-size: 14px;">
                    يمكنك البدء فوراً في إرسال رسائل التحقق بدون أي تكلفة
                </p>
            </div>
            
            <!-- Features -->
            <div style="margin: 30px 0;">
                <h3 style="color: #28a745; margin: 0 0 20px 0; font-size: 18px;">
                    ماذا يمكنك فعله الآن؟
                </h3>
                
                <div style="display: table; width: 100%;">
                    <div style="display: table-row;">
                        <div style="display: table-cell; padding: 15px; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 10px;">
                            <div style="display: flex; align-items: center;">
                                <span style="font-size: 24px; margin-left: 15px;">⚙️</span>
                                <div>
                                    <strong style="color: #495057;">إعداد SMTP</strong><br>
                                    <span style="color: #6c757d; font-size: 14px;">قم بإعداد خادم البريد الخاص بك</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="display: table-row;">
                        <div style="display: table-cell; padding: 15px; background-color: #f8f9fa; border-radius: 8px; margin: 10px 0;">
                            <div style="display: flex; align-items: center;">
                                <span style="font-size: 24px; margin-left: 15px;">🔑</span>
                                <div>
                                    <strong style="color: #495057;">مفتاح API</strong><br>
                                    <span style="color: #6c757d; font-size: 14px;">احصل على مفتاح API لبدء الإرسال</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="display: table-row;">
                        <div style="display: table-cell; padding: 15px; background-color: #f8f9fa; border-radius: 8px; margin-top: 10px;">
                            <div style="display: flex; align-items: center;">
                                <span style="font-size: 24px; margin-left: 15px;">📊</span>
                                <div>
                                    <strong style="color: #495057;">تتبع الإحصائيات</strong><br>
                                    <span style="color: #6c757d; font-size: 14px;">راقب أداء رسائلك في الوقت الفعلي</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- CTA Button -->
            <div style="text-align: center; margin: 40px 0;">
                <a href="#" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: #ffffff; text-decoration: none; padding: 15px 30px; border-radius: 25px; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);">
                    🚀 ادخل إلى لوحة التحكم
                </a>
            </div>
            
            <!-- Support -->
            <div style="background-color: #e8f5e8; border-radius: 8px; padding: 20px; margin: 30px 0;">
                <h3 style="color: #155724; margin: 0 0 10px 0; font-size: 16px;">
                    🆘 تحتاج مساعدة؟
                </h3>
                <p style="color: #155724; margin: 0; line-height: 1.6; font-size: 14px;">
                    فريق الدعم الفني متاح 24/7 لمساعدتك. تواصل معنا عبر البريد الإلكتروني أو الدردشة المباشرة في لوحة التحكم.
                </p>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e9ecef;">
            <p style="color: #6c757d; margin: 0 0 10px 0; font-size: 14px;">
                شكراً لاختيارك Verifix-OTP 💚
            </p>
            <p style="color: #adb5bd; margin: 0; font-size: 12px;">
                هذه رسالة ترحيبية تلقائية
            </p>
        </div>
        
    </div>
</body>
</html>
            ''',
            primary_color='#28a745',
            secondary_color='#ffffff'
        )
        
        # إضافة القوالب إلى قاعدة البيانات
        existing_verification = EmailTemplateBase.query.filter_by(template_type='verification').first()
        if not existing_verification:
            db.session.add(verification_template)
        
        existing_welcome = EmailTemplateBase.query.filter_by(template_type='welcome').first()
        if not existing_welcome:
            db.session.add(welcome_template)
        
        db.session.commit()
        print("✅ تم إنشاء قوالب البريد الافتراضية بنجاح!")

if __name__ == '__main__':
    create_default_templates()

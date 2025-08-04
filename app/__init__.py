from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import config
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# إنشاء كائنات التطبيق
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app(config_name=None):
    """إنشاء تطبيق Flask"""
    app = Flask(__name__)
    
    # تحديد إعدادات التطبيق
    config_name = config_name or os.environ.get('FLASK_CONFIG') or 'default'
    app.config.from_object(config[config_name])
    
    # تهيئة الإضافات
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # إعدادات تسجيل الدخول
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة.'
    login_manager.login_message_category = 'info'
    
    # تسجيل البلوبرينتس
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from app.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # إنشاء مجلدات الرفع إذا لم تكن موجودة
    upload_folder = os.path.join(app.instance_path, app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_folder, exist_ok=True)
    
    # تهيئة قاعدة البيانات وإنشاء حساب المدير تلقائياً
    with app.app_context():
        init_database_and_admin()
    
    return app

def init_database_and_admin():
    """تهيئة قاعدة البيانات وإنشاء حساب المدير تلقائياً"""
    try:
        # إنشاء الجداول
        db.create_all()
        
        # التحقق من وجود حساب المدير
        from app.models import Company, EmailService, EmailTemplateBase
        admin = Company.query.filter_by(email='hanizezo72@gmail.com').first()
        
        if not admin:
            print("🔧 إنشاء حساب المدير...")
            
            # إنشاء حساب المدير الجديد باستخدام hanizezo72@gmail.com كحساب إداري
            admin = Company(
                company_name='Verifix-OTP Admin',
                email='hanizezo72@gmail.com',  # هذا هو الحساب الإداري الفعلي
                is_admin=True,
                is_verified=True,
                is_active=True,
                balance=10000.0,
                # إعدادات SMTP تلقائياً
                smtp_server='smtp.gmail.com',
                smtp_port=587,
                smtp_username='hanizezo72@gmail.com',
                smtp_password='jxtr qylc lzkj ehpb',
                sender_email='hanizezo72@gmail.com',
                sender_name='Verifix-OTP'
            )
            admin.set_password('zxc65432')
            db.session.add(admin)
            
            # إنشاء الخدمات الأساسية إذا لم تكن موجودة
            services = [
                {'service_code': 'verification', 'service_name': 'كود التحقق', 'description': 'إرسال رموز التحقق للمستخدمين'},
                {'service_code': 'welcome', 'service_name': 'رسائل الترحيب', 'description': 'رسائل ترحيب للمستخدمين الجدد'},
                {'service_code': 'order', 'service_name': 'تأكيد الطلبات', 'description': 'رسائل تأكيد الطلبات والمعاملات'},
                {'service_code': 'notification', 'service_name': 'الإشعارات', 'description': 'إشعارات عامة للمستخدمين'},
                {'service_code': 'marketing', 'service_name': 'التسويق', 'description': 'رسائل تسويقية وترويجية'},
            ]
            
            for service_data in services:
                service = EmailService.query.filter_by(service_code=service_data['service_code']).first()
                if not service:
                    service = EmailService(**service_data)
                    db.session.add(service)
            
            db.session.commit()
            
            # إنشاء القوالب الافتراضية
            from app.utils.email_utils import create_default_templates
            create_default_templates()
            
            print("✅ تم إنشاء حساب المدير بنجاح!")
            print("📧 البريد: hanizezo72@gmail.com")
            print("🔑 كلمة المرور: zxc65432")
            print("📨 إعدادات SMTP جاهزة!")
        else:
            # تحديث إعدادات SMTP إذا كانت فارغة
            if not admin.smtp_server:
                admin.smtp_server = 'smtp.gmail.com'
                admin.smtp_port = 587
                admin.smtp_username = 'hanizezo72@gmail.com'
                admin.smtp_password = 'jxtr qylc lzkj ehpb'
                admin.sender_email = 'hanizezo72@gmail.com'
                admin.sender_name = 'Verifix-OTP'
                db.session.commit()
                print("✅ تم تحديث إعدادات SMTP للمدير!")
    
    except Exception as e:
        print(f"⚠️ خطأ في تهيئة النظام: {e}")
        db.session.rollback()

@login_manager.user_loader
def load_user(user_id):
    """تحميل المستخدم من قاعدة البيانات"""
    from app.models import Company
    return Company.query.get(int(user_id))

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import json
from app import db

class Company(UserMixin, db.Model):
    """نموذج الشركة"""
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    
    # إعدادات البريد الإلكتروني
    smtp_server = db.Column(db.String(100))
    smtp_port = db.Column(db.Integer, default=587)
    smtp_username = db.Column(db.String(120))
    smtp_password = db.Column(db.String(200))
    sender_email = db.Column(db.String(120))
    sender_name = db.Column(db.String(100))
    
    # إعدادات الحساب
    balance = db.Column(db.Float, default=0.0)
    free_messages_used = db.Column(db.Integer, default=0)
    total_messages_sent = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    # الطوابع الزمنية
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # العلاقات
    email_templates = db.relationship('EmailTemplate', backref='company', lazy='dynamic', cascade='all, delete-orphan')
    email_logs = db.relationship('EmailLog', backref='company', lazy='dynamic', cascade='all, delete-orphan')
    services = db.relationship('CompanyService', backref='company', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Company, self).__init__(**kwargs)
        if not self.api_key:
            self.api_key = self.generate_api_key()
    
    def set_password(self, password):
        """تشفير كلمة المرور"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """التحقق من كلمة المرور"""
        return check_password_hash(self.password_hash, password)
    
    def generate_api_key(self):
        """إنتاج مفتاح API جديد"""
        return str(uuid.uuid4()).replace('-', '')
    
    def regenerate_api_key(self):
        """إعادة إنتاج مفتاح API"""
        self.api_key = self.generate_api_key()
        db.session.commit()
        return self.api_key
    
    def can_send_message(self):
        """التحقق من إمكانية إرسال رسالة"""
        from flask import current_app
        free_limit = current_app.config['FREE_MESSAGES_LIMIT']
        
        # إذا لم يستخدم كامل الرسائل المجانية
        if self.free_messages_used < free_limit:
            return True
        
        # إذا كان لديه رصيد
        message_price = current_app.config['MESSAGE_PRICE']
        return self.balance >= message_price
    
    def deduct_message_cost(self):
        """خصم تكلفة الرسالة"""
        from flask import current_app
        free_limit = current_app.config['FREE_MESSAGES_LIMIT']
        message_price = current_app.config['MESSAGE_PRICE']
        
        if self.free_messages_used < free_limit:
            self.free_messages_used += 1
        else:
            self.balance -= message_price
        
        self.total_messages_sent += 1
        db.session.commit()
    
    def add_balance(self, amount):
        """إضافة رصيد"""
        self.balance += amount
        db.session.commit()
    
    def is_low_balance(self):
        """التحقق من انخفاض الرصيد"""
        from flask import current_app
        threshold = current_app.config['LOW_BALANCE_THRESHOLD']
        free_limit = current_app.config['FREE_MESSAGES_LIMIT']
        
        if self.free_messages_used >= free_limit:
            return self.balance <= threshold
        return False
    
    def __repr__(self):
        return f'<Company {self.company_name}>'

class EmailService(db.Model):
    """خدمات البريد الإلكتروني المتاحة"""
    __tablename__ = 'email_services'
    
    id = db.Column(db.Integer, primary_key=True)
    service_code = db.Column(db.String(20), unique=True, nullable=False)
    service_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # العلاقات
    company_services = db.relationship('CompanyService', backref='service', lazy='dynamic')
    templates = db.relationship('EmailTemplate', backref='service', lazy='dynamic')
    
    def __repr__(self):
        return f'<EmailService {self.service_name}>'

class CompanyService(db.Model):
    """خدمات الشركة المشتركة"""
    __tablename__ = 'company_services'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('email_services.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CompanyService {self.company.company_name} - {self.service.service_name}>'

class EmailTemplate(db.Model):
    """قوالب البريد الإلكتروني"""
    __tablename__ = 'email_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('email_services.id'), nullable=False)
    
    template_name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    html_content = db.Column(db.Text, nullable=False)
    
    # إعدادات التصميم
    primary_color = db.Column(db.String(7), default='#007bff')
    secondary_color = db.Column(db.String(7), default='#6c757d')
    logo_url = db.Column(db.String(200))
    
    # متغيرات القالب (JSON)
    variables = db.Column(db.Text)  # JSON string
    
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_variables(self):
        """الحصول على متغيرات القالب"""
        if self.variables:
            return json.loads(self.variables)
        return {}
    
    def set_variables(self, variables_dict):
        """تعيين متغيرات القالب"""
        self.variables = json.dumps(variables_dict)
    
    def __repr__(self):
        return f'<EmailTemplate {self.template_name}>'

class EmailLog(db.Model):
    """سجل الرسائل المرسلة"""
    __tablename__ = 'email_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('email_services.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('email_templates.id'))
    
    recipient_email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    
    # حالة الرسالة
    status = db.Column(db.String(20), default='sent')  # sent, failed, pending
    error_message = db.Column(db.Text)
    
    # تفاصيل الإرسال
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    message_id = db.Column(db.String(100))
    
    # التكلفة
    cost = db.Column(db.Float, default=0.0)
    was_free = db.Column(db.Boolean, default=False)
    
    # العلاقات
    template = db.relationship('EmailTemplate', backref='logs')
    service_rel = db.relationship('EmailService', backref='logs')
    
    def __repr__(self):
        return f'<EmailLog {self.recipient_email} - {self.status}>'

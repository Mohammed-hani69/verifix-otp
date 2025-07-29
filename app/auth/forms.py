from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError
from wtforms.widgets import PasswordInput
from app.models import Company

class LoginForm(FlaskForm):
    """نموذج تسجيل الدخول"""
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    password = PasswordField('كلمة المرور', validators=[DataRequired()])
    remember_me = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')

class RegistrationForm(FlaskForm):
    """نموذج التسجيل"""
    company_name = StringField('اسم الشركة', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('تأكيد كلمة المرور', 
                              validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('إنشاء حساب')
    
    def validate_email(self, email):
        """التحقق من عدم وجود البريد الإلكتروني مسبقاً"""
        company = Company.query.filter_by(email=email.data).first()
        if company:
            raise ValidationError('هذا البريد الإلكتروني مسجل مسبقاً. يرجى اختيار بريد آخر.')

class EmailSettingsForm(FlaskForm):
    """نموذج إعدادات البريد الإلكتروني"""
    smtp_server = StringField('خادم SMTP', validators=[DataRequired()])
    smtp_port = IntegerField('منفذ SMTP', validators=[DataRequired(), NumberRange(min=1, max=65535)])
    smtp_username = StringField('اسم المستخدم', validators=[DataRequired()])
    smtp_password = PasswordField('كلمة المرور', validators=[DataRequired()])
    sender_email = StringField('البريد المرسل', validators=[DataRequired(), Email()])
    sender_name = StringField('اسم المرسل', validators=[DataRequired()])
    submit = SubmitField('حفظ الإعدادات')

class ChangePasswordForm(FlaskForm):
    """نموذج تغيير كلمة المرور"""
    current_password = PasswordField('كلمة المرور الحالية', validators=[DataRequired()])
    new_password = PasswordField('كلمة المرور الجديدة', validators=[DataRequired(), Length(min=8)])
    new_password2 = PasswordField('تأكيد كلمة المرور الجديدة', 
                                  validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('تغيير كلمة المرور')

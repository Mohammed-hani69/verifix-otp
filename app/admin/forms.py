from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, FloatField, SubmitField, TextAreaField, SelectField, BooleanField, IntegerField, DateField
from wtforms.validators import DataRequired, NumberRange, Length
from datetime import datetime, timedelta

class BalanceApprovalForm(FlaskForm):
    """نموذج الموافقة على طلب شحن الرصيد"""
    admin_notes = TextAreaField('ملاحظات الإدارة', validators=[Length(max=500)])
    submit_approve = SubmitField('موافقة')
    submit_reject = SubmitField('رفض')

class CompanyManagementForm(FlaskForm):
    """نموذج إدارة الشركات"""
    is_active = BooleanField('حساب نشط')
    balance = FloatField('الرصيد الحالي', validators=[NumberRange(min=0)])
    admin_notes = TextAreaField('ملاحظات إدارية', validators=[Length(max=500)])
    submit = SubmitField('حفظ التغييرات')

class ManualBalanceForm(FlaskForm):
    """نموذج إضافة رصيد يدوياً"""
    amount = FloatField('المبلغ', validators=[DataRequired(), NumberRange(min=1, max=10000)])
    reason = TextAreaField('سبب الإضافة', validators=[DataRequired(), Length(min=5, max=200)])
    submit = SubmitField('إضافة الرصيد')

class EmailTemplateForm(FlaskForm):
    """نموذج إدارة قوالب البريد"""
    template_name = StringField('اسم القالب', validators=[DataRequired(), Length(min=2, max=100)])
    subject = StringField('عنوان الرسالة', validators=[DataRequired(), Length(min=5, max=200)])
    html_content = TextAreaField('محتوى الرسالة (HTML)', validators=[DataRequired()])
    primary_color = StringField('اللون الأساسي', validators=[DataRequired()], default='#28a745')
    secondary_color = StringField('اللون الثانوي', validators=[DataRequired()], default='#ffffff')
    is_active = BooleanField('نشط')
    submit = SubmitField('حفظ القالب')

class StatsFilterForm(FlaskForm):
    """نموذج تصفية الإحصائيات"""
    period = SelectField('الفترة الزمنية', choices=[
        ('today', 'اليوم'),
        ('week', 'هذا الأسبوع'),
        ('month', 'هذا الشهر'),
        ('quarter', 'هذا الربع'),
        ('year', 'هذا العام'),
        ('custom', 'فترة مخصصة')
    ], default='month')
    start_date = DateField('تاريخ البداية')
    end_date = DateField('تاريخ النهاية')
    submit = SubmitField('تطبيق المرشح')

class AdminUserForm(FlaskForm):
    """نموذج إدارة المستخدمين/الشركات من الإدارة"""
    company_name = StringField('اسم الشركة', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('البريد الإلكتروني', validators=[DataRequired()])
    is_active = BooleanField('الحساب نشط', default=True)
    is_admin = BooleanField('صلاحيات إدارية')
    balance = FloatField('الرصيد', validators=[NumberRange(min=0)], default=0.0)
    free_messages_used = IntegerField('الرسائل المجانية المستخدمة', validators=[NumberRange(min=0)], default=0)
    notes = TextAreaField('ملاحظات إدارية', validators=[Length(max=500)])
    submit = SubmitField('حفظ التغييرات')

class BulkActionForm(FlaskForm):
    """نموذج العمليات المجمعة"""
    action = SelectField('الإجراء', choices=[
        ('activate', 'تفعيل المحدد'),
        ('deactivate', 'إلغاء تفعيل المحدد'),
        ('add_balance', 'إضافة رصيد للمحدد'),
        ('reset_free_messages', 'إعادة تعيين الرسائل المجانية')
    ])
    amount = FloatField('المبلغ (في حالة إضافة رصيد)', validators=[NumberRange(min=0)])
    reason = TextAreaField('السبب/الملاحظات', validators=[Length(max=200)])
    submit = SubmitField('تنفيذ العملية')

class SystemSettingsForm(FlaskForm):
    """نموذج إعدادات النظام"""
    company_name = StringField('اسم الشركة', validators=[DataRequired()], default='Verifix-OTP')
    admin_email = StringField('بريد الإدارة', validators=[DataRequired()])
    message_price = FloatField('سعر الرسالة', validators=[DataRequired(), NumberRange(min=0.01)], default=0.25)
    free_messages_limit = IntegerField('حد الرسائل المجانية', validators=[DataRequired(), NumberRange(min=1)], default=1000)
    low_balance_threshold = IntegerField('حد التحذير من انخفاض الرصيد', validators=[DataRequired(), NumberRange(min=1)], default=50)
    transfer_phone = StringField('رقم التليفون للتحويل', validators=[DataRequired()], default='01033607749')
    submit = SubmitField('حفظ الإعدادات')

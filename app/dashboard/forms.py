from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, HiddenField, FileField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.widgets import ColorInput
from flask_wtf.file import FileAllowed

class TemplateForm(FlaskForm):
    """نموذج إنشاء/تعديل قالب البريد الإلكتروني"""
    template_name = StringField('اسم القالب', validators=[DataRequired(), Length(max=100)])
    service_id = SelectField('نوع الخدمة', coerce=int, validators=[DataRequired()])
    subject = StringField('موضوع الرسالة', validators=[DataRequired(), Length(max=200)])
    
    # إعدادات التصميم
    primary_color = StringField('اللون الأساسي', default='#007bff', widget=ColorInput())
    secondary_color = StringField('اللون الثانوي', default='#6c757d', widget=ColorInput())
    
    # رفع الشعار
    logo = FileField('الشعار', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'يرجى رفع صورة صالحة فقط!')
    ])
    
    # محتوى القالب
    html_content = TextAreaField('محتوى الرسالة', validators=[DataRequired()])
    
    submit = SubmitField('حفظ القالب')

class AddBalanceForm(FlaskForm):
    """نموذج إضافة رصيد"""
    amount = StringField('المبلغ (جنيه)', validators=[DataRequired()])
    submit = SubmitField('إضافة رصيد')

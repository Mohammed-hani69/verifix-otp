from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import os
from werkzeug.utils import secure_filename

from app.dashboard import bp
from app.dashboard.forms import TemplateForm, AddBalanceForm
from app.models import Company, EmailService, CompanyService, EmailTemplate, EmailLog
from app import db

@bp.route('/')
@login_required
def index():
    """لوحة التحكم الرئيسية"""
    # إحصائيات أساسية
    total_sent = current_user.total_messages_sent
    free_used = current_user.free_messages_used
    balance = current_user.balance
    
    # إحصائيات هذا الشهر
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_sent = EmailLog.query.filter(
        EmailLog.company_id == current_user.id,
        EmailLog.sent_at >= start_of_month
    ).count()
    
    # إحصائيات آخر 7 أيام
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_stats = db.session.query(
        func.date(EmailLog.sent_at).label('date'),
        func.count(EmailLog.id).label('count')
    ).filter(
        EmailLog.company_id == current_user.id,
        EmailLog.sent_at >= week_ago
    ).group_by(func.date(EmailLog.sent_at)).all()
    
    # آخر الرسائل المرسلة
    recent_logs = EmailLog.query.filter_by(company_id=current_user.id)\
                                .order_by(desc(EmailLog.sent_at))\
                                .limit(10).all()
    
    # التحقق من انخفاض الرصيد
    low_balance_warning = current_user.is_low_balance()
    
    return render_template('dashboard/index.html',
                         title='لوحة التحكم',
                         total_sent=total_sent,
                         free_used=free_used,
                         balance=balance,
                         monthly_sent=monthly_sent,
                         weekly_stats=weekly_stats,
                         recent_logs=recent_logs,
                         low_balance_warning=low_balance_warning)

@bp.route('/services')
@login_required
def services():
    """إدارة الخدمات"""
    company_services = db.session.query(CompanyService, EmailService)\
                                 .join(EmailService)\
                                 .filter(CompanyService.company_id == current_user.id)\
                                 .all()
    
    return render_template('dashboard/services.html',
                         title='الخدمات',
                         company_services=company_services)

@bp.route('/templates')
@login_required
def templates():
    """إدارة القوالب"""
    templates = EmailTemplate.query.filter_by(company_id=current_user.id)\
                                   .order_by(desc(EmailTemplate.created_at)).all()
    
    return render_template('dashboard/templates.html',
                         title='القوالب',
                         templates=templates)

@bp.route('/templates/create', methods=['GET', 'POST'])
@bp.route('/templates/edit/<int:template_id>', methods=['GET', 'POST'])
@login_required
def create_edit_template(template_id=None):
    """إنشاء أو تعديل قالب"""
    template = None
    if template_id:
        template = EmailTemplate.query.filter_by(
            id=template_id, 
            company_id=current_user.id
        ).first_or_404()
    
    form = TemplateForm()
    
    # تحديد خيارات الخدمات المتاحة
    form.service_id.choices = [
        (cs.service.id, cs.service.service_name) 
        for cs in current_user.services.join(EmailService).filter(CompanyService.is_active == True)
    ]
    
    if form.validate_on_submit():
        if not template:
            template = EmailTemplate(company_id=current_user.id)
            db.session.add(template)
        
        template.template_name = form.template_name.data
        template.service_id = form.service_id.data
        template.subject = form.subject.data
        template.primary_color = form.primary_color.data
        template.secondary_color = form.secondary_color.data
        template.html_content = form.html_content.data
        
        # معالجة رفع الشعار
        if form.logo.data:
            filename = secure_filename(form.logo.data.filename)
            logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                                   'logos', str(current_user.id))
            os.makedirs(logo_path, exist_ok=True)
            
            file_path = os.path.join(logo_path, filename)
            form.logo.data.save(file_path)
            template.logo_url = f'/static/uploads/logos/{current_user.id}/{filename}'
        
        template.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('تم حفظ القالب بنجاح!', 'success')
        return redirect(url_for('dashboard.templates'))
    
    # ملء البيانات للتعديل
    if template and request.method == 'GET':
        form.template_name.data = template.template_name
        form.service_id.data = template.service_id
        form.subject.data = template.subject
        form.primary_color.data = template.primary_color
        form.secondary_color.data = template.secondary_color
        form.html_content.data = template.html_content
    
    return render_template('dashboard/create_template.html',
                         title='إنشاء قالب' if not template else 'تعديل قالب',
                         form=form,
                         template=template)

@bp.route('/templates/delete/<int:template_id>', methods=['POST'])
@login_required
def delete_template(template_id):
    """حذف قالب"""
    template = EmailTemplate.query.filter_by(
        id=template_id, 
        company_id=current_user.id
    ).first_or_404()
    
    db.session.delete(template)
    db.session.commit()
    
    flash('تم حذف القالب بنجاح!', 'success')
    return redirect(url_for('dashboard.templates'))

@bp.route('/logs')
@login_required
def logs():
    """سجل الرسائل"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    logs = EmailLog.query.filter_by(company_id=current_user.id)\
                         .order_by(desc(EmailLog.sent_at))\
                         .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('dashboard/logs.html',
                         title='سجل الرسائل',
                         logs=logs)

@bp.route('/balance', methods=['GET', 'POST'])
@login_required
def balance():
    """إدارة الرصيد"""
    form = AddBalanceForm()
    
    if form.validate_on_submit():
        try:
            amount = float(form.amount.data)
            if amount > 0:
                current_user.add_balance(amount)
                flash(f'تم إضافة {amount} جنيه إلى رصيدك!', 'success')
            else:
                flash('يرجى إدخال مبلغ صحيح أكبر من صفر.', 'error')
        except ValueError:
            flash('يرجى إدخال مبلغ صحيح.', 'error')
        
        return redirect(url_for('dashboard.balance'))
    
    return render_template('dashboard/balance.html',
                         title='إدارة الرصيد',
                         form=form)

@bp.route('/api-settings')
@login_required
def api_settings():
    """إعدادات API"""
    return render_template('dashboard/api_settings.html',
                         title='إعدادات API')

@bp.route('/profile')
@login_required
def profile():
    """الملف الشخصي"""
    return render_template('dashboard/profile.html',
                         title='الملف الشخصي')

@bp.route('/statistics')
@login_required
def statistics():
    """الإحصائيات التفصيلية"""
    # إحصائيات حسب الخدمة
    service_stats = db.session.query(
        EmailService.service_name,
        func.count(EmailLog.id).label('count'),
        func.sum(EmailLog.cost).label('total_cost')
    ).join(EmailLog)\
     .filter(EmailLog.company_id == current_user.id)\
     .group_by(EmailService.service_name).all()
    
    # إحصائيات شهرية
    monthly_stats = db.session.query(
        func.strftime('%Y-%m', EmailLog.sent_at).label('month'),
        func.count(EmailLog.id).label('count'),
        func.sum(EmailLog.cost).label('cost')
    ).filter(EmailLog.company_id == current_user.id)\
     .group_by(func.strftime('%Y-%m', EmailLog.sent_at))\
     .order_by(desc('month')).limit(12).all()
    
    return render_template('dashboard/statistics.html',
                         title='الإحصائيات',
                         service_stats=service_stats,
                         monthly_stats=monthly_stats)

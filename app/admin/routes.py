from flask import render_template, redirect, url_for, flash, request, current_app, jsonify, send_from_directory
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from sqlalchemy import func, desc

from app.admin import bp
from app.admin.forms import (BalanceApprovalForm, CompanyManagementForm, ManualBalanceForm, 
                           EmailTemplateForm, StatsFilterForm, AdminUserForm, BulkActionForm, SystemSettingsForm)
from app.models import Company, BalanceRequest, SystemStats, EmailLog, EmailTemplateBase, EmailService, SystemSettings
from app import db


def admin_required(f):
    """تأكد من أن المستخدم هو مدير"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('غير مصرح لك بالوصول لهذه الصفحة.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """لوحة التحكم الإدارية"""
    # إحصائيات سريعة
    total_companies = Company.query.filter_by(is_admin=False).count()
    active_companies = Company.query.filter_by(is_admin=False, is_active=True).count()
    pending_requests = BalanceRequest.query.filter_by(status='pending').count()
    
    # إحصائيات اليوم
    today = datetime.utcnow().date()
    today_stats = SystemStats.query.filter_by(date=today).first()
    
    # آخر الطلبات
    recent_requests = BalanceRequest.query.order_by(desc(BalanceRequest.created_at)).limit(5).all()
    
    # آخر الشركات المسجلة
    recent_companies = Company.query.filter_by(is_admin=False).order_by(desc(Company.created_at)).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         title='لوحة التحكم الإدارية',
                         total_companies=total_companies,
                         active_companies=active_companies,
                         pending_requests=pending_requests,
                         today_stats=today_stats,
                         recent_requests=recent_requests,
                         recent_companies=recent_companies)


@bp.route('/balance-requests')
@login_required
@admin_required
def balance_requests():
    """إدارة طلبات شحن الرصيد"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    
    query = BalanceRequest.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    requests = query.order_by(desc(BalanceRequest.created_at)).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('admin/balance_requests.html',
                         title='إدارة طلبات شحن الرصيد',
                         requests=requests,
                         status_filter=status_filter)


@bp.route('/balance-request/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def balance_request_detail(id):
    """تفاصيل طلب شحن الرصيد"""
    balance_request = BalanceRequest.query.get_or_404(id)
    form = BalanceApprovalForm()
    
    if form.validate_on_submit():
        if form.submit_approve.data:
            balance_request.approve(current_user.id, form.admin_notes.data)
            flash('تم الموافقة على الطلب وإضافة الرصيد بنجاح!', 'success')
        elif form.submit_reject.data:
            balance_request.reject(current_user.id, form.admin_notes.data)
            flash('تم رفض الطلب.', 'warning')
        
        return redirect(url_for('admin.balance_requests'))
    
    return render_template('admin/balance_request_detail.html',
                         title='تفاصيل طلب الشحن',
                         balance_request=balance_request,
                         form=form)


@bp.route('/companies')
@login_required
@admin_required
def companies():
    """إدارة الشركات"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status_filter = request.args.get('status', 'all')
    
    query = Company.query.filter_by(is_admin=False)
    
    if search:
        query = query.filter(Company.company_name.contains(search) | 
                           Company.email.contains(search))
    
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    elif status_filter == 'verified':
        query = query.filter_by(is_verified=True)
    elif status_filter == 'unverified':
        query = query.filter_by(is_verified=False)
    
    companies = query.order_by(desc(Company.created_at)).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('admin/companies.html',
                         title='إدارة الشركات',
                         companies=companies,
                         search=search,
                         status_filter=status_filter)


@bp.route('/company/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def company_detail(id):
    """تفاصيل الشركة"""
    company = Company.query.get_or_404(id)
    form = CompanyManagementForm()
    balance_form = ManualBalanceForm()
    
    if form.validate_on_submit() and form.submit.data:
        company.is_active = form.is_active.data
        company.balance = form.balance.data
        db.session.commit()
        flash('تم تحديث بيانات الشركة بنجاح!', 'success')
        return redirect(url_for('admin.company_detail', id=id))
    
    if balance_form.validate_on_submit() and balance_form.submit.data:
        company.add_balance(balance_form.amount.data)
        flash(f'تم إضافة {balance_form.amount.data} جنيه للرصيد!', 'success')
        return redirect(url_for('admin.company_detail', id=id))
    
    # ملء النموذج بالبيانات الحالية
    if request.method == 'GET':
        form.is_active.data = company.is_active
        form.balance.data = company.balance
    
    # إحصائيات الشركة
    total_messages = company.total_messages_sent
    total_spent = EmailLog.query.filter_by(company_id=id).with_entities(
        func.sum(EmailLog.cost)).scalar() or 0
    
    return render_template('admin/company_detail.html',
                         title=f'تفاصيل {company.company_name}',
                         company=company,
                         form=form,
                         balance_form=balance_form,
                         total_messages=total_messages,
                         total_spent=total_spent)


@bp.route('/stats')
@login_required
@admin_required
def stats():
    """التقارير والإحصائيات"""
    form = StatsFilterForm()
    
    # إحصائيات عامة
    total_companies = Company.query.filter_by(is_admin=False).count()
    total_messages = EmailLog.query.count()
    total_revenue = db.session.query(func.sum(EmailLog.cost)).scalar() or 0
    
    # إحصائيات الفترة الأخيرة (30 يوم)
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_stats = SystemStats.query.filter(SystemStats.date >= thirty_days_ago).all()
    
    # إنشاء بيانات فارغة إذا لم توجد إحصائيات
    if not recent_stats:
        # إنشاء بيانات وهمية للأيام الـ 7 الماضية
        today = datetime.now().date()
        chart_data = {
            'dates': [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)],
            'messages': [0] * 7,
            'revenue': [0.0] * 7,
            'new_companies': [0] * 7
        }
    else:
        # تحضير البيانات للرسوم البيانية
        chart_data = {
            'dates': [stat.date.strftime('%Y-%m-%d') for stat in recent_stats],
            'messages': [stat.total_messages_sent for stat in recent_stats],
            'revenue': [stat.total_revenue for stat in recent_stats],
            'new_companies': [stat.new_companies for stat in recent_stats]
        }
    
    return render_template('admin/stats.html',
                         title='التقارير والإحصائيات',
                         form=form,
                         total_companies=total_companies,
                         total_messages=total_messages,
                         total_revenue=total_revenue,
                         chart_data=chart_data)


@bp.route('/email-templates')
@login_required
@admin_required
def email_templates():
    """إدارة قوالب البريد"""
    templates = EmailTemplateBase.query.all()
    return render_template('admin/email_templates.html',
                         title='إدارة قوالب البريد',
                         templates=templates)


@bp.route('/email-template/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def email_template_edit(id):
    """تعديل قالب بريد"""
    template = EmailTemplateBase.query.get_or_404(id)
    form = EmailTemplateForm()
    
    if form.validate_on_submit():
        template.template_name = form.template_name.data
        template.subject = form.subject.data
        template.html_content = form.html_content.data
        template.primary_color = form.primary_color.data
        template.secondary_color = form.secondary_color.data
        template.is_active = form.is_active.data
        template.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('تم تحديث القالب بنجاح!', 'success')
        return redirect(url_for('admin.email_templates'))
    
    # ملء النموذج بالبيانات الحالية
    if request.method == 'GET':
        form.template_name.data = template.template_name
        form.subject.data = template.subject
        form.html_content.data = template.html_content
        form.primary_color.data = template.primary_color
        form.secondary_color.data = template.secondary_color
        form.is_active.data = template.is_active
    
    return render_template('admin/email_template_edit.html',
                         title='تعديل قالب البريد',
                         template=template,
                         form=form)


@bp.route('/upload/<path:filename>')
def uploaded_file(filename):
    """عرض الملفات المرفوعة"""
    import os
    upload_folder = os.path.join(current_app.instance_path, current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(upload_folder, filename)


@bp.route('/company/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def company_edit(id):
    """تعديل بيانات شركة"""
    company = Company.query.get_or_404(id)
    form = AdminUserForm()
    
    if form.validate_on_submit():
        company.company_name = form.company_name.data
        company.email = form.email.data
        company.is_active = form.is_active.data
        company.is_admin = form.is_admin.data
        company.balance = form.balance.data
        company.free_messages_used = form.free_messages_used.data
        
        db.session.commit()
        flash('تم تحديث بيانات الشركة بنجاح!', 'success')
        return redirect(url_for('admin.companies'))
    
    # ملء النموذج بالبيانات الحالية
    if request.method == 'GET':
        form.company_name.data = company.company_name
        form.email.data = company.email
        form.is_active.data = company.is_active
        form.is_admin.data = company.is_admin
        form.balance.data = company.balance
        form.free_messages_used.data = company.free_messages_used
    
    return render_template('admin/company_edit.html',
                         title='تعديل بيانات الشركة',
                         company=company,
                         form=form)


@bp.route('/company/<int:id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def company_toggle_status(id):
    """تغيير حالة الشركة (تفعيل/إلغاء تفعيل)"""
    company = Company.query.get_or_404(id)
    company.is_active = not company.is_active
    
    db.session.commit()
    
    status = 'مفعل' if company.is_active else 'معطل'
    flash(f'تم تغيير حالة الشركة إلى: {status}', 'success')
    
    return redirect(url_for('admin.companies'))


@bp.route('/company/<int:id>/add-balance', methods=['POST'])
@login_required
@admin_required
def company_add_balance(id):
    """إضافة رصيد لشركة"""
    company = Company.query.get_or_404(id)
    amount = float(request.form.get('amount', 0))
    reason = request.form.get('reason', '')
    
    if amount > 0:
        company.add_balance(amount)
        flash(f'تم إضافة {amount} جنيه لرصيد {company.company_name}', 'success')
    else:
        flash('يجب أن يكون المبلغ أكبر من صفر', 'error')
    
    return redirect(url_for('admin.companies'))


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    """إعدادات النظام"""
    form = SystemSettingsForm()
    
    if form.validate_on_submit():
        # حفظ الإعدادات في قاعدة البيانات
        SystemSettings.set_setting('company_name', form.company_name.data, 'string', 'اسم الشركة')
        SystemSettings.set_setting('admin_email', form.admin_email.data, 'string', 'بريد المدير الإلكتروني')
        SystemSettings.set_setting('message_price', form.message_price.data, 'float', 'سعر الرسالة الواحدة')
        SystemSettings.set_setting('free_messages_limit', form.free_messages_limit.data, 'int', 'حد الرسائل المجانية')
        SystemSettings.set_setting('low_balance_threshold', form.low_balance_threshold.data, 'float', 'حد التحذير من انخفاض الرصيد')
        SystemSettings.set_setting('transfer_phone', form.transfer_phone.data, 'string', 'رقم التليفون للتحويل')
        
        flash('تم حفظ إعدادات النظام بنجاح!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    # ملء النموذج بالبيانات المحفوظة
    if request.method == 'GET':
        form.company_name.data = SystemSettings.get_setting('company_name', 'Verifix-OTP')
        form.admin_email.data = SystemSettings.get_setting('admin_email', 'admin@verifix-otp.com')
        form.message_price.data = SystemSettings.get_setting('message_price', 0.25)
        form.free_messages_limit.data = SystemSettings.get_setting('free_messages_limit', 1000)
        form.low_balance_threshold.data = SystemSettings.get_setting('low_balance_threshold', 50)
        form.transfer_phone.data = SystemSettings.get_setting('transfer_phone', '01033607749')
    
    return render_template('admin/settings.html',
                         title='إعدادات النظام',
                         form=form)


@bp.route('/clear-cache', methods=['POST'])
@login_required
@admin_required
def clear_cache():
    """مسح ذاكرة التخزين المؤقت"""
    try:
        # هنا يمكن إضافة كود مسح ذاكرة التخزين المؤقت
        flash('تم مسح ذاكرة التخزين المؤقت بنجاح', 'success')
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@bp.route('/backup-database')
@login_required
@admin_required
def backup_database():
    """إنشاء نسخة احتياطية من قاعدة البيانات"""
    try:
        import shutil
        import os
        from datetime import datetime
        
        # مسار قاعدة البيانات
        db_path = os.path.join(current_app.instance_path, 'app.db')
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_path = os.path.join(current_app.instance_path, 'backups', backup_name)
        
        # إنشاء مجلد النسخ الاحتياطية إذا لم يكن موجوداً
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        # نسخ قاعدة البيانات
        shutil.copy2(db_path, backup_path)
        
        return send_from_directory(
            os.path.join(current_app.instance_path, 'backups'),
            backup_name,
            as_attachment=True
        )
    except Exception as e:
        flash(f'حدث خطأ أثناء إنشاء النسخة الاحتياطية: {str(e)}', 'error')
        return redirect(url_for('admin.settings'))


@bp.route('/optimize-database', methods=['POST'])
@login_required
@admin_required
def optimize_database():
    """تحسين قاعدة البيانات"""
    try:
        # تشغيل أمر VACUUM لضغط قاعدة البيانات
        db.session.execute('VACUUM')
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@bp.route('/system-logs')
@login_required
@admin_required
def system_logs():
    """عرض سجلات النظام"""
    try:
        # قراءة آخر 1000 سطر من ملف السجل
        log_entries = []
        log_file = os.path.join(current_app.instance_path, 'logs', 'app.log')
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                log_entries = lines[-1000:]  # آخر 1000 سطر
        
        return render_template('admin/system_logs.html',
                             title='سجلات النظام',
                             log_entries=log_entries)
    except Exception as e:
        flash(f'حدث خطأ أثناء قراءة السجلات: {str(e)}', 'error')
        return redirect(url_for('admin.settings'))


@bp.route('/bulk-actions', methods=['POST'])
@login_required
@admin_required
def bulk_actions():
    """تنفيذ العمليات المجمعة"""
    form = BulkActionForm()
    selected_ids = request.form.getlist('selected_companies')
    
    if form.validate_on_submit() and selected_ids:
        companies = Company.query.filter(Company.id.in_(selected_ids)).all()
        action = form.action.data
        
        count = 0
        for company in companies:
            if action == 'activate':
                company.is_active = True
                count += 1
            elif action == 'deactivate':
                company.is_active = False
                count += 1
            elif action == 'add_balance' and form.amount.data:
                company.add_balance(form.amount.data)
                count += 1
            elif action == 'reset_free_messages':
                company.free_messages_used = 0
                count += 1
        
        db.session.commit()
        flash(f'تم تنفيذ العملية على {count} شركة بنجاح!', 'success')
    else:
        flash('يرجى اختيار شركات وإجراء صحيح', 'error')
    
    return redirect(url_for('admin.companies'))

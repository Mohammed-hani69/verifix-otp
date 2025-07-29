from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, EmailSettingsForm, ChangePasswordForm
from app.models import Company, EmailService, CompanyService
from app import db

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        company = Company.query.filter_by(email=form.email.data).first()
        
        if company and company.check_password(form.password.data):
            if not company.is_active:
                flash('تم إيقاف حسابك. يرجى التواصل مع الإدارة.', 'error')
                return redirect(url_for('auth.login'))
            
            login_user(company, remember=form.remember_me.data)
            company.last_login = datetime.utcnow()
            db.session.commit()
            
            flash(f'مرحباً {company.company_name}!', 'success')
            
            # إعادة توجيه إلى الصفحة المطلوبة
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('dashboard.index')
            return redirect(next_page)
        else:
            flash('بيانات الدخول غير صحيحة.', 'error')
    
    return render_template('auth/login.html', title='تسجيل الدخول', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """صفحة التسجيل"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        company = Company(
            company_name=form.company_name.data,
            email=form.email.data.lower()
        )
        company.set_password(form.password.data)
        
        db.session.add(company)
        db.session.commit()
        
        # إضافة الخدمات الأساسية للشركة الجديدة
        basic_services = EmailService.query.filter_by(is_active=True).all()
        for service in basic_services:
            company_service = CompanyService(
                company_id=company.id,
                service_id=service.id
            )
            db.session.add(company_service)
        
        db.session.commit()
        
        flash('تم إنشاء حسابك بنجاح! يمكنك الآن تسجيل الدخول.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='إنشاء حساب', form=form)

@bp.route('/logout')
@login_required
def logout():
    """تسجيل الخروج"""
    logout_user()
    flash('تم تسجيل الخروج بنجاح.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/email-settings', methods=['GET', 'POST'])
@login_required
def email_settings():
    """إعدادات البريد الإلكتروني"""
    form = EmailSettingsForm()
    
    if form.validate_on_submit():
        current_user.smtp_server = form.smtp_server.data
        current_user.smtp_port = form.smtp_port.data
        current_user.smtp_username = form.smtp_username.data
        current_user.smtp_password = form.smtp_password.data
        current_user.sender_email = form.sender_email.data
        current_user.sender_name = form.sender_name.data
        
        db.session.commit()
        flash('تم حفظ إعدادات البريد الإلكتروني بنجاح!', 'success')
        return redirect(url_for('dashboard.index'))
    
    # ملء النموذج بالبيانات الحالية
    if request.method == 'GET':
        form.smtp_server.data = current_user.smtp_server
        form.smtp_port.data = current_user.smtp_port
        form.smtp_username.data = current_user.smtp_username
        form.smtp_password.data = current_user.smtp_password
        form.sender_email.data = current_user.sender_email
        form.sender_name.data = current_user.sender_name
    
    return render_template('auth/email_settings.html', title='إعدادات البريد', form=form)

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """تغيير كلمة المرور"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('تم تغيير كلمة المرور بنجاح!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('كلمة المرور الحالية غير صحيحة.', 'error')
    
    return render_template('auth/change_password.html', title='تغيير كلمة المرور', form=form)

@bp.route('/regenerate-api-key', methods=['GET', 'POST'])
@login_required
def regenerate_api_key():
    """إعادة إنتاج مفتاح API"""
    new_api_key = current_user.regenerate_api_key()
    flash(f'تم إنشاء مفتاح API جديد: {new_api_key}', 'success')
    return redirect(url_for('dashboard.api_settings'))

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import os
from werkzeug.utils import secure_filename

from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, EmailSettingsForm, ChangePasswordForm, VerificationForm, BalanceRequestForm
from app.models import Company, EmailService, CompanyService, BalanceRequest
from app import db
from app.utils.email_utils import send_verification_email, send_welcome_email

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
            
            if not company.is_verified:
                flash('يجب تفعيل حسابك أولاً. تحقق من بريدك الإلكتروني.', 'warning')
                return redirect(url_for('auth.verify_email', email=company.email))
            
            login_user(company, remember=form.remember_me.data)
            company.last_login = datetime.utcnow()
            db.session.commit()
            
            flash(f'مرحباً {company.company_name}!', 'success')
            
            # إعادة توجيه إلى الصفحة المطلوبة
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                if company.is_admin:
                    next_page = url_for('admin.dashboard')
                else:
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
        
        # إنشاء كود التحقق وإرساله
        verification_code = company.generate_verification_code()
        db.session.commit()
        
        # إرسال رسالة التحقق
        try:
            success, message = send_verification_email(company.email, verification_code, company.company_name)
            if not success:
                print(f"فشل إرسال رسالة التحقق: {message}")
                # لا نوقف العملية، فقط نسجل الخطأ
        except Exception as e:
            print(f"خطأ في إرسال رسالة التحقق: {e}")
            import traceback
            traceback.print_exc()
        
        # إضافة الخدمات الأساسية للشركة الجديدة
        basic_services = EmailService.query.filter_by(is_active=True).all()
        for service in basic_services:
            company_service = CompanyService(
                company_id=company.id,
                service_id=service.id
            )
            db.session.add(company_service)
        
        db.session.commit()
        
        flash('تم إنشاء حسابك بنجاح! تحقق من بريدك الإلكتروني لتفعيل الحساب.', 'success')
        return redirect(url_for('auth.verify_email', email=company.email))
    
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


@bp.route('/verify-email/<email>', methods=['GET', 'POST'])
def verify_email(email):
    """صفحة إدخال كود التحقق"""
    company = Company.query.filter_by(email=email).first_or_404()
    
    if company.is_verified:
        flash('تم تفعيل حسابك بالفعل.', 'info')
        return redirect(url_for('auth.login'))
    
    form = VerificationForm()
    
    if form.validate_on_submit():
        # التحقق من كود التفعيل
        if company.verify_code(form.verification_code.data):
            db.session.commit()
            
            # إرسال رسالة ترحيبية
            try:
                send_welcome_email(company.email, company.company_name)
            except Exception as e:
                print(f"خطأ في إرسال رسالة الترحيب: {e}")
            
            flash('تم تفعيل حسابك بنجاح! مرحباً بك في Verifix-OTP', 'success')
            login_user(company)
            return redirect(url_for('dashboard.index'))
        else:
            flash('كود التحقق غير صحيح أو منتهي الصلاحية.', 'error')
    
    return render_template('auth/verify_email.html', 
                         title='تفعيل الحساب', 
                         form=form, 
                         email=email)


@bp.route('/resend-verification/<email>')
def resend_verification(email):
    """إعادة إرسال كود التحقق"""
    company = Company.query.filter_by(email=email).first_or_404()
    
    if company.is_verified:
        flash('تم تفعيل حسابك بالفعل.', 'info')
        return redirect(url_for('auth.login'))
    
    # إنشاء كود جديد
    verification_code = company.generate_verification_code()
    db.session.commit()
    
    try:
        send_verification_email(company.email, verification_code, company.company_name)
        flash('تم إرسال كود التحقق الجديد إلى بريدك الإلكتروني.', 'success')
    except Exception as e:
        flash('حدث خطأ في إرسال كود التحقق. حاول مرة أخرى.', 'error')
        print(f"خطأ في إرسال رسالة التحقق: {e}")
    
    return redirect(url_for('auth.verify_email', email=email))


@bp.route('/balance-request', methods=['GET', 'POST'])
@login_required
def balance_request():
    """طلب شحن الرصيد"""
    form = BalanceRequestForm()
    
    if form.validate_on_submit():
        # حفظ صورة إيصال التحويل
        file = form.transfer_receipt.data
        filename = secure_filename(file.filename)
        
        # إنشاء مسار الحفظ الكامل
        upload_folder = os.path.join(current_app.instance_path, current_app.config['UPLOAD_FOLDER'], 'receipts')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # إنشاء طلب الشحن
        balance_request = BalanceRequest(
            company_id=current_user.id,
            amount=form.amount.data,
            transfer_receipt=f'receipts/{filename}',
            transfer_number=form.transfer_number.data
        )
        
        db.session.add(balance_request)
        db.session.commit()
        
        flash('تم إرسال طلب شحن الرصيد بنجاح! سيتم مراجعته خلال 24 ساعة.', 'success')
        return redirect(url_for('dashboard.balance'))
    
    return render_template('auth/balance_request.html', 
                         title='طلب شحن الرصيد', 
                         form=form)

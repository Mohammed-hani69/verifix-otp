#!/bin/bash

# =============================================================================
# Email Sender Pro - Deployment Script
# سكريبت نشر تطبيق إرسال الرسائل الإلكترونية
# =============================================================================

echo "🚀 بدء عملية نشر Email Sender Pro على الخادم..."

# متغيرات الإعداد
APP_NAME="email-sender"
APP_USER="www-data"
APP_GROUP="www-data"
APP_DIR="/var/www/verifix-otp"
REPO_URL="your-git-repo-url-here"
DOMAIN="verifix-otp.escovfair.com"
PYTHON_VERSION="3.11"

# ألوان للمخرجات
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# دالة طباعة الرسائل
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# التحقق من وجود المستخدم
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "يجب تشغيل هذا السكريبت بصلاحيات المدير (sudo)"
        exit 1
    fi
}

# تحديث النظام
update_system() {
    log_info "تحديث النظام..."
    apt update && apt upgrade -y
    apt install -y software-properties-common curl wget git
}

# تثبيت Python وإعداده
install_python() {
    log_info "تثبيت Python ${PYTHON_VERSION}..."
    apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python${PYTHON_VERSION}-dev
    apt install -y python3-pip
    
    # تثبيت pip للإصدار المحدد
    curl -sS https://bootstrap.pypa.io/get-pip.py | python${PYTHON_VERSION}
}

# تثبيت وإعداد PostgreSQL
install_postgresql() {
    log_info "تثبيت PostgreSQL..."
    apt install -y postgresql postgresql-contrib libpq-dev
    
    # بدء الخدمة
    systemctl start postgresql
    systemctl enable postgresql
    
    # إنشاء قاعدة البيانات والمستخدم
    sudo -u postgres psql << EOF
CREATE DATABASE email_sender_db;
CREATE USER email_user WITH PASSWORD 'email_pass_2025_secure';
GRANT ALL PRIVILEGES ON DATABASE email_sender_db TO email_user;
ALTER USER email_user CREATEDB;
\q
EOF
    
    log_info "تم إعداد PostgreSQL بنجاح"
}

# تثبيت وإعداد Nginx
install_nginx() {
    log_info "تثبيت Nginx..."
    apt install -y nginx
    
    # نسخ ملف الإعداد
    cp ${APP_DIR}/nginx.conf /etc/nginx/sites-available/${DOMAIN}
    ln -sf /etc/nginx/sites-available/${DOMAIN} /etc/nginx/sites-enabled/
    
    # حذف الموقع الافتراضي
    rm -f /etc/nginx/sites-enabled/default
    
    # اختبار الإعداد
    nginx -t
    systemctl restart nginx
    systemctl enable nginx
    
    log_info "تم إعداد Nginx بنجاح"
}

# إعداد SSL مع Let's Encrypt
setup_ssl() {
    log_info "إعداد SSL Certificate..."
    apt install -y certbot python3-certbot-nginx
    
    # الحصول على شهادة SSL
    certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos --email admin@${DOMAIN}
    
    # إعداد التجديد التلقائي
    crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | crontab -
    
    log_info "تم إعداد SSL بنجاح"
}

# إنشاء مستخدم التطبيق
create_app_user() {
    log_info "إنشاء مستخدم التطبيق..."
    
    # إنشاء المستخدم إذا لم يكن موجوداً
    if ! id -u ${APP_USER} >/dev/null 2>&1; then
        useradd --system --gid ${APP_GROUP} --shell /bin/bash --home ${APP_DIR} ${APP_USER}
    fi
}

# إعداد مجلد التطبيق
setup_app_directory() {
    log_info "إعداد مجلد التطبيق..."
    
    # إنشاء المجلدات المطلوبة
    mkdir -p ${APP_DIR}
    mkdir -p /var/log/email_sender
    mkdir -p /var/log/nginx
    
    # تعيين الصلاحيات
    chown -R ${APP_USER}:${APP_GROUP} ${APP_DIR}
    chown -R ${APP_USER}:${APP_GROUP} /var/log/email_sender
    chmod -R 755 ${APP_DIR}
}

# نسخ ملفات التطبيق
deploy_application() {
    log_info "نشر التطبيق..."
    
    # الانتقال لمجلد التطبيق
    cd ${APP_DIR}
    
    # نسخ الملفات (يجب تعديل هذا حسب طريقة النقل المستخدمة)
    # إذا كنت تستخدم Git:
    # git clone ${REPO_URL} .
    # أو نسخ الملفات يدوياً
    
    # إنشاء البيئة الافتراضية
    sudo -u ${APP_USER} python${PYTHON_VERSION} -m venv venv
    
    # تفعيل البيئة وتثبيت المتطلبات
    sudo -u ${APP_USER} bash -c "source venv/bin/activate && pip install --upgrade pip"
    sudo -u ${APP_USER} bash -c "source venv/bin/activate && pip install -r requirements.txt"
    
    # إنشاء قاعدة البيانات
    sudo -u ${APP_USER} bash -c "source venv/bin/activate && python init_db.py"
    
    log_info "تم نشر التطبيق بنجاح"
}

# إعداد خدمة systemd
setup_systemd_service() {
    log_info "إعداد خدمة systemd..."
    
    # نسخ ملف الخدمة
    cp ${APP_DIR}/email-sender.service /etc/systemd/system/
    
    # إعادة تحميل systemd وبدء الخدمة
    systemctl daemon-reload
    systemctl start ${APP_NAME}
    systemctl enable ${APP_NAME}
    
    log_info "تم إعداد خدمة systemd بنجاح"
}

# إعداد جدار الحماية
setup_firewall() {
    log_info "إعداد جدار الحماية..."
    
    ufw --force enable
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 'Nginx Full'
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    log_info "تم إعداد جدار الحماية بنجاح"
}

# التحقق من حالة الخدمات
check_services() {
    log_info "التحقق من حالة الخدمات..."
    
    echo "حالة PostgreSQL:"
    systemctl status postgresql --no-pager -l
    
    echo "حالة Nginx:"
    systemctl status nginx --no-pager -l
    
    echo "حالة التطبيق:"
    systemctl status ${APP_NAME} --no-pager -l
    
    echo "اختبار الاتصال:"
    curl -I https://${DOMAIN}
}

# الدالة الرئيسية
main() {
    log_info "بدء تثبيت Email Sender Pro..."
    
    check_root
    update_system
    install_python
    install_postgresql
    install_nginx
    create_app_user
    setup_app_directory
    
    log_warn "يرجى نسخ ملفات التطبيق إلى ${APP_DIR} ثم تشغيل:"
    log_warn "sudo bash deploy.sh continue"
}

# إكمال التثبيت
continue_deployment() {
    log_info "إكمال عملية النشر..."
    
    deploy_application
    setup_systemd_service
    setup_ssl
    setup_firewall
    check_services
    
    log_info "🎉 تم نشر Email Sender Pro بنجاح!"
    log_info "يمكنك الوصول للموقع على: https://${DOMAIN}"
    log_info "للمراقبة: sudo journalctl -u ${APP_NAME} -f"
}

# تحديد العملية المطلوبة
case "${1:-main}" in
    main)
        main
        ;;
    continue)
        continue_deployment
        ;;
    *)
        echo "الاستخدام: $0 [main|continue]"
        exit 1
        ;;
esac

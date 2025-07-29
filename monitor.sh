#!/bin/bash

# =============================================================================
# Email Sender Pro - Service Monitor
# سكريبت مراقبة خدمة إرسال الرسائل الإلكترونية
# =============================================================================

APP_NAME="email-sender"
DOMAIN="verifix-otp.escovfair.com"
LOG_FILE="/var/log/email_sender/monitor.log"

# ألوان للمخرجات
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# دالة طباعة الرسائل مع الوقت
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# فحص حالة الخدمة
check_service_status() {
    if systemctl is-active --quiet $APP_NAME; then
        log_info "✅ خدمة $APP_NAME تعمل بشكل طبيعي"
        return 0
    else
        log_error "❌ خدمة $APP_NAME لا تعمل"
        return 1
    fi
}

# فحص حالة Nginx
check_nginx_status() {
    if systemctl is-active --quiet nginx; then
        log_info "✅ خدمة Nginx تعمل بشكل طبيعي"
        return 0
    else
        log_error "❌ خدمة Nginx لا تعمل"
        return 1
    fi
}

# فحص اتصال الموقع
check_website_connectivity() {
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/health)
    
    if [ "$HTTP_STATUS" -eq 200 ]; then
        log_info "✅ الموقع يستجيب بشكل طبيعي (HTTP $HTTP_STATUS)"
        return 0
    else
        log_error "❌ الموقع لا يستجيب (HTTP $HTTP_STATUS)"
        return 1
    fi
}

# فحص استخدام القرص
check_disk_usage() {
    DISK_USAGE=$(df /var/www | awk 'NR==2 {print $(NF-1)}' | sed 's/%//')
    
    if [ "$DISK_USAGE" -lt 80 ]; then
        log_info "✅ استخدام القرص طبيعي (${DISK_USAGE}%)"
    elif [ "$DISK_USAGE" -lt 90 ]; then
        log_warn "⚠️ استخدام القرص مرتفع (${DISK_USAGE}%)"
    else
        log_error "❌ مساحة القرص منخفضة جداً (${DISK_USAGE}%)"
    fi
}

# فحص استخدام الذاكرة
check_memory_usage() {
    MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    
    if [ "$MEMORY_USAGE" -lt 80 ]; then
        log_info "✅ استخدام الذاكرة طبيعي (${MEMORY_USAGE}%)"
    elif [ "$MEMORY_USAGE" -lt 90 ]; then
        log_warn "⚠️ استخدام الذاكرة مرتفع (${MEMORY_USAGE}%)"
    else
        log_error "❌ استخدام الذاكرة مرتفع جداً (${MEMORY_USAGE}%)"
    fi
}

# فحص شهادة SSL
check_ssl_certificate() {
    SSL_EXPIRY=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates | grep notAfter | cut -d= -f2)
    SSL_EXPIRY_EPOCH=$(date -d "$SSL_EXPIRY" +%s)
    CURRENT_EPOCH=$(date +%s)
    DAYS_UNTIL_EXPIRY=$(( (SSL_EXPIRY_EPOCH - CURRENT_EPOCH) / 86400 ))
    
    if [ "$DAYS_UNTIL_EXPIRY" -gt 30 ]; then
        log_info "✅ شهادة SSL صالحة لـ $DAYS_UNTIL_EXPIRY يوم"
    elif [ "$DAYS_UNTIL_EXPIRY" -gt 7 ]; then
        log_warn "⚠️ شهادة SSL ستنتهي خلال $DAYS_UNTIL_EXPIRY يوم"
    else
        log_error "❌ شهادة SSL ستنتهي خلال $DAYS_UNTIL_EXPIRY يوم - يجب التجديد فوراً"
    fi
}

# إعادة تشغيل الخدمة عند الحاجة
restart_service_if_needed() {
    if ! check_service_status; then
        log_warn "🔄 محاولة إعادة تشغيل خدمة $APP_NAME"
        systemctl restart $APP_NAME
        sleep 10
        
        if check_service_status; then
            log_info "✅ تم إعادة تشغيل الخدمة بنجاح"
        else
            log_error "❌ فشل في إعادة تشغيل الخدمة"
        fi
    fi
}

# إعادة تشغيل Nginx عند الحاجة
restart_nginx_if_needed() {
    if ! check_nginx_status; then
        log_warn "🔄 محاولة إعادة تشغيل خدمة Nginx"
        systemctl restart nginx
        sleep 5
        
        if check_nginx_status; then
            log_info "✅ تم إعادة تشغيل Nginx بنجاح"
        else
            log_error "❌ فشل في إعادة تشغيل Nginx"
        fi
    fi
}

# عرض الإحصائيات
show_statistics() {
    echo "========================================="
    echo "إحصائيات Email Sender Pro"
    echo "========================================="
    echo "الوقت: $(date)"
    echo "المجال: $DOMAIN"
    echo ""
    
    echo "حالة الخدمات:"
    systemctl is-active --quiet $APP_NAME && echo "  ✅ Email Sender: نشط" || echo "  ❌ Email Sender: متوقف"
    systemctl is-active --quiet nginx && echo "  ✅ Nginx: نشط" || echo "  ❌ Nginx: متوقف"
    systemctl is-active --quiet postgresql && echo "  ✅ PostgreSQL: نشط" || echo "  ❌ PostgreSQL: متوقف"
    
    echo ""
    echo "استخدام الموارد:"
    echo "  💽 القرص: $(df /var/www | awk 'NR==2 {print $(NF-1)}')"
    echo "  🧠 الذاكرة: $(free | awk 'NR==2{printf "%.0f%%", $3*100/$2}')"
    echo "  ⚡ المعالج: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')%"
    
    echo ""
    echo "إحصائيات Nginx:"
    echo "  📊 الطلبات اليوم: $(grep "$(date '+%d/%b/%Y')" /var/log/nginx/verifix-otp_access.log 2>/dev/null | wc -l)"
    echo "  🔴 الأخطاء اليوم: $(grep "$(date '+%Y/%m/%d')" /var/log/nginx/verifix-otp_error.log 2>/dev/null | wc -l)"
    
    echo "========================================="
}

# الدالة الرئيسية
main() {
    case "${1:-monitor}" in
        monitor)
            log_info "🔍 بدء مراقبة Email Sender Pro"
            check_service_status
            check_nginx_status
            check_website_connectivity
            check_disk_usage
            check_memory_usage
            check_ssl_certificate
            ;;
        restart)
            log_info "🔄 فحص وإعادة تشغيل الخدمات عند الحاجة"
            restart_service_if_needed
            restart_nginx_if_needed
            ;;
        stats)
            show_statistics
            ;;
        full)
            log_info "🔍 فحص شامل وإعادة تشغيل عند الحاجة"
            restart_service_if_needed
            restart_nginx_if_needed
            check_website_connectivity
            check_disk_usage
            check_memory_usage
            check_ssl_certificate
            ;;
        *)
            echo "الاستخدام: $0 [monitor|restart|stats|full]"
            echo "  monitor: مراقبة الحالة فقط"
            echo "  restart: إعادة تشغيل الخدمات عند الحاجة"
            echo "  stats: عرض الإحصائيات"
            echo "  full: فحص شامل مع إعادة التشغيل"
            exit 1
            ;;
    esac
}

# تشغيل الدالة الرئيسية
main "$@"

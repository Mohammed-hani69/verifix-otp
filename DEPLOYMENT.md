# دليل نشر Email Sender Pro على الخادم

## معلومات الخادم
- **النطاق**: https://verifix-otp.escovfair.com
- **عنوان IP**: 147.93.52.178
- **نظام التشغيل**: Ubuntu/Debian (مُوصى به)

## خطوات النشر

### 1. تحضير الخادم
```bash
# الاتصال بالخادم
ssh root@147.93.52.178

# تحديث النظام
apt update && apt upgrade -y

# تثبيت Git (إذا لم يكن مثبتاً)
apt install -y git
```

### 2. نقل ملفات المشروع
```bash
# إنشاء مجلد المشروع
mkdir -p /var/www/verifix-otp
cd /var/www/verifix-otp

# نقل الملفات (استخدم أحد الطرق التالية):
# الطريقة 1: باستخدام Git
git clone <your-repo-url> .

# الطريقة 2: باستخدام SCP/SFTP
# من جهازك المحلي:
# scp -r /path/to/email_sender/* root@147.93.52.178:/var/www/verifix-otp/

# الطريقة 3: باستخدام rsync
# rsync -avz /path/to/email_sender/ root@147.93.52.178:/var/www/verifix-otp/
```

### 3. تشغيل سكريبت النشر
```bash
# إعطاء صلاحيات التنفيذ
chmod +x deploy.sh

# تشغيل السكريبت
sudo bash deploy.sh main

# بعد نسخ الملفات، إكمال النشر
sudo bash deploy.sh continue
```

### 4. إعدادات إضافية

#### إعداد قاعدة البيانات يدوياً (إذا لزم الأمر)
```bash
# الدخول لـ PostgreSQL
sudo -u postgres psql

# إنشاء قاعدة البيانات
CREATE DATABASE email_sender_db;
CREATE USER email_user WITH PASSWORD 'email_pass_2025_secure';
GRANT ALL PRIVILEGES ON DATABASE email_sender_db TO email_user;
ALTER USER email_user CREATEDB;
\q
```

#### إعداد متغيرات البيئة
```bash
# تحرير ملف .env
nano /var/www/verifix-otp/.env

# التأكد من الإعدادات التالية:
FLASK_ENV=production
SECRET_KEY=verifix-otp-production-secret-key-2025-secure-token
DATABASE_URL=postgresql://email_user:email_pass_2025_secure@localhost/email_sender_db
SERVER_NAME=verifix-otp.escovfair.com
```

### 5. بدء الخدمات
```bash
# بدء خدمة التطبيق
systemctl start email-sender
systemctl enable email-sender

# بدء Nginx
systemctl start nginx
systemctl enable nginx

# التحقق من الحالة
systemctl status email-sender
systemctl status nginx
```

### 6. إعداد SSL Certificate
```bash
# تثبيت Certbot
apt install -y certbot python3-certbot-nginx

# الحصول على شهادة SSL
certbot --nginx -d verifix-otp.escovfair.com

# إعداد التجديد التلقائي
crontab -e
# إضافة السطر التالي:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 7. إعداد جدار الحماية
```bash
# تفعيل UFW
ufw enable

# السماح بالاتصالات المطلوبة
ufw allow ssh
ufw allow 'Nginx Full'
ufw allow 80/tcp
ufw allow 443/tcp
```

### 8. اختبار التطبيق
```bash
# اختبار health check
curl https://verifix-otp.escovfair.com/health

# اختبار الصفحة الرئيسية
curl -I https://verifix-otp.escovfair.com
```

## إدارة الخدمة

### مراقبة اللوجز
```bash
# مراقبة لوجز التطبيق
journalctl -u email-sender -f

# مراقبة لوجز Nginx
tail -f /var/log/nginx/verifix-otp_access.log
tail -f /var/log/nginx/verifix-otp_error.log

# مراقبة لوجز التطبيق المخصصة
tail -f /var/log/email_sender/access.log
tail -f /var/log/email_sender/error.log
```

### إعادة تشغيل الخدمات
```bash
# إعادة تشغيل التطبيق
systemctl restart email-sender

# إعادة تشغيل Nginx
systemctl restart nginx

# إعادة تحميل إعدادات Nginx فقط
systemctl reload nginx
```

### تحديث التطبيق
```bash
cd /var/www/verifix-otp

# إيقاف الخدمة
systemctl stop email-sender

# سحب التحديثات (إذا كنت تستخدم Git)
git pull origin main

# تحديث المتطلبات
source venv/bin/activate
pip install -r requirements.txt

# تشغيل migrations (إذا وجدت)
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# بدء الخدمة
systemctl start email-sender
```

## استكشاف الأخطاء

### مشاكل شائعة وحلولها

1. **خطأ في الاتصال بقاعدة البيانات**
```bash
# التحقق من حالة PostgreSQL
systemctl status postgresql

# إعادة تشغيل PostgreSQL
systemctl restart postgresql
```

2. **خطأ في الصلاحيات**
```bash
# إعادة تعيين الصلاحيات
chown -R www-data:www-data /var/www/verifix-otp
chmod -R 755 /var/www/verifix-otp
```

3. **خطأ في شهادة SSL**
```bash
# تجديد الشهادة
certbot renew

# إعادة تحميل Nginx
systemctl reload nginx
```

4. **مشكلة في الذاكرة**
```bash
# مراقبة استخدام الذاكرة
htop
free -h

# تقليل عدد العمال في gunicorn.conf.py إذا لزم الأمر
```

## معلومات مهمة

- **مجلد التطبيق**: `/var/www/verifix-otp`
- **مجلد اللوجز**: `/var/log/email_sender/`
- **ملف إعدادات Nginx**: `/etc/nginx/sites-available/verifix-otp.escovfair.com`
- **ملف خدمة systemd**: `/etc/systemd/system/email-sender.service`
- **مستخدم التطبيق**: `www-data`

## نصائح للأداء

1. **مراقبة الموارد بانتظام**
2. **عمل نسخ احتياطية من قاعدة البيانات**
3. **تحديث النظام والتطبيق بانتظام**
4. **مراجعة اللوجز لاكتشاف المشاكل مبكراً**

---

**ملاحظة**: تأكد من تغيير كلمات المرور الافتراضية وإعداد مفاتيح SSH للأمان.

# Verifix-OTP 📧

منصة متكاملة لإرسال رسائل التحقق والبريد الإلكتروني للشركات مع لوحة تحكم إدارية شاملة.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)

## 🌟 المميزات

- **إرسال رسائل آمن ومشفر** مع دعم SMTP متقدم
- **واجهة إدارة متقدمة** لإدارة الشركات والخدمات
- **نظام API قوي** للتكامل مع التطبيقات الخارجية
- **قوالب رسائل قابلة للتخصيص** مع دعم HTML
- **نظام رصيد وفوترة** مرن ومتقدم
- **مراقبة وإحصائيات تفصيلية** لجميع العمليات
- **أمان عالي** مع تشفير البيانات الحساسة
- **دعم كامل للغة العربية** والتوجه من اليمين لليسار

## � التقنيات المستخدمة

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy مع دعم PostgreSQL/MySQL/SQLite
- **Frontend**: Bootstrap 5 + JavaScript
- **Email**: Flask-Mail مع دعم SMTP متقدم
- **Authentication**: Flask-Login مع bcrypt
- **Security**: WTF-CSRF Protection
- **Deployment**: Gunicorn + Nginx + systemd
- 1000 رسالة مجانية عند التسجيل
- إحصائيات مفصلة للاستخدام
- تتبع تكاليف كل خدمة

### 🔐 الأمان والموثوقية
- مفاتيح API فريدة لكل شركة
- تشفير البيانات الحساسة
- مصادقة آمنة للطلبات
- سجلات مفصلة لجميع العمليات

### 📊 لوحة تحكم شاملة
- إحصائيات مرئية تفاعلية
- إدارة الخدمات والقوالب
- تتبع الرصيد والاستخدام
- إعدادات SMTP مخصصة

## 🛠️ التثبيت والإعداد

### المتطلبات الأساسية
- Python 3.8+
- SQLite/PostgreSQL/MySQL
- خادم SMTP (Gmail, SendGrid, إلخ)

### التثبيت

1. **نسخ المشروع**
```bash
git clone <repository-url>
cd email_sender
```

2. **إنشاء بيئة افتراضية**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **تثبيت المتطلبات**
```bash
pip install -r requirements.txt
```

4. **إعداد متغيرات البيئة**
```bash
# إنشاء ملف .env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
ADMIN_EMAIL=admin@yourcompany.com
COMPANY_NAME=شركة الرسائل الذكية
MESSAGE_PRICE=0.25
FREE_MESSAGES_LIMIT=1000
```

5. **تهيئة قاعدة البيانات**
```bash
python run.py init_db
```

6. **إنشاء حساب المدير**
```bash
python run.py create_admin
```

7. **تشغيل التطبيق**
```bash
python run.py
# أو للإنتاج
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## 📖 دليل الاستخدام

### للشركات

1. **التسجيل**
   - قم بإنشاء حساب جديد
   - احصل على مفتاح API الخاص بك
   - استلم 1000 رسالة مجانية

2. **إعداد SMTP**
   - أدخل بيانات خادم البريد الخاص بك
   - اختبر الاتصال

3. **إنشاء القوالب**
   - صمم قوالب بهوية شركتك
   - أضف الشعار والألوان
   - استخدم المتغيرات الديناميكية

4. **البدء في الإرسال**
   - استخدم API endpoints
   - راقب الإحصائيات
   - تتبع الرصيد

### للمطورين

#### 1. رموز التحقق
```python
import requests

url = "https://yourapi.com/api/send-verification"
headers = {"Authorization": "Bearer YOUR_API_KEY"}
data = {
    "email": "user@example.com",
    "code": "123456",
    "company_id": "your-company-id"
}

response = requests.post(url, json=data, headers=headers)
```

#### 2. تفاصيل الطلبات
```python
data = {
    "email": "customer@example.com",
    "order_id": "ORD-12345",
    "amount": 250.00,
    "items": [
        {"name": "منتج 1", "price": 100},
        {"name": "منتج 2", "price": 150}
    ],
    "company_id": "your-company-id"
}

response = requests.post("https://yourapi.com/api/send-order", json=data, headers=headers)
```

#### 3. رسائل الترحيب
```python
data = {
    "email": "newuser@example.com",
    "name": "أحمد محمد",
    "company_id": "your-company-id"
}

response = requests.post("https://yourapi.com/api/send-welcome", json=data, headers=headers)
```

#### 4. رسائل مخصصة
```python
data = {
    "email": "recipient@example.com",
    "subject": "عنوان الرسالة",
    "content": "محتوى الرسالة",
    "template_variables": {
        "name": "محمد",
        "company": "شركة ABC"
    },
    "company_id": "your-company-id"
}

response = requests.post("https://yourapi.com/api/send-custom", json=data, headers=headers)
```

## 🎯 نقاط النهاية (API Endpoints)

### المصادقة
جميع الطلبات تتطلب مفتاح API في header:
```
Authorization: Bearer YOUR_API_KEY
```

### الخدمات المتاحة

| الطريقة | المسار | الوصف |
|---------|-------|--------|
| POST | `/api/send-verification` | إرسال رمز تحقق |
| POST | `/api/send-order` | إرسال تفاصيل طلب |
| POST | `/api/send-welcome` | إرسال رسالة ترحيب |
| POST | `/api/send-custom` | إرسال رسالة مخصصة |
| GET | `/api/balance` | استعلام عن الرصيد |
| GET | `/api/stats` | إحصائيات الاستخدام |

## 🔧 الإعدادات المتقدمة

### إعداد قاعدة البيانات

#### PostgreSQL
```bash
# في ملف .env
DATABASE_URL=postgresql://username:password@localhost/dbname
```

#### MySQL
```bash
# في ملف .env
DATABASE_URL=mysql://username:password@localhost/dbname
```

### إعداد الأمان

#### تشفير إضافي
```python
# في config.py
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
WTF_CSRF_ENABLED = True
```

#### HTTPS
للإنتاج، تأكد من استخدام HTTPS:
```python
# في run.py للإنتاج
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, ssl_context='adhoc')
```

## 📊 المراقبة والصيانة

### سجلات النظام
```python
# عرض آخر 100 رسالة
python run.py show_logs --limit 100

# عرض إحصائيات الشركة
python run.py company_stats --id COMPANY_ID
```

### النسخ الاحتياطي
```bash
# نسخ احتياطي لقاعدة البيانات
sqlite3 app.db ".backup backup.db"

# استعادة النسخ الاحتياطي
sqlite3 app.db ".restore backup.db"
```

## 🐛 استكشاف الأخطاء وحلها

### المشاكل الشائعة

#### 1. خطأ في اتصال SMTP
```python
# تحقق من إعدادات SMTP في لوحة التحكم
# تأكد من صحة كلمة المرور وإعدادات الأمان
```

#### 2. انتهاء الرصيد
```python
# تحقق من الرصيد الحالي
# قم بشحن الرصيد من لوحة التحكم
```

#### 3. فشل API
```python
# تحقق من صحة مفتاح API
# تأكد من صحة بيانات الطلب
# راجع سجلات الأخطاء
```

## 🤝 المساهمة

نرحب بمساهماتكم! لل مساهمة:

1. Fork المشروع
2. أنشئ branch جديد (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push إلى Branch (`git push origin feature/amazing-feature`)
5. افتح Pull Request

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

## 📞 الدعم والتواصل

- **البريد الإلكتروني**: support@yourcompany.com
- **الموقع الإلكتروني**: https://yourwebsite.com
- **الوثائق**: https://docs.yourwebsite.com

## 🚀 الخطط المستقبلية

- [ ] دعم إرسال الرسائل النصية (SMS)
- [ ] تطبيق موبايل
- [ ] تكامل مع منصات التجارة الإلكترونية
- [ ] ذكاء اصطناعي لتحسين معدلات الفتح
- [ ] تحليلات متقدمة ولوحات معلومات تفاعلية
- [ ] دعم عدة لغات
- [ ] API webhooks للإشعارات الفورية

---

**تم تطوير هذا المشروع بـ ❤️ في مصر**

للمزيد من المعلومات، راجع [التوثيق الكامل](https://docs.yourwebsite.com).

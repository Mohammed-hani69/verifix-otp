# 🚀 دليل البدء السريع

## خطوات التشغيل السريع

### 1. تحضير البيئة
```bash
# إنشاء نسخة من إعدادات البيئة
copy .env.example .env

# تعديل الإعدادات في ملف .env
# على الأقل قم بتغيير SECRET_KEY
```

### 2. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 3. تهيئة قاعدة البيانات
```bash
python run.py init_db
```

### 4. إنشاء حساب المدير
```bash
python run.py create_admin
```

### 5. تشغيل التطبيق
```bash
python run.py
```

## الوصول للنظام

- **الموقع الرئيسي**: http://localhost:5000
- **لوحة التحكم**: http://localhost:5000/dashboard
- **تسجيل الدخول**: http://localhost:5000/auth/login

## بيانات المدير الافتراضية

```
البريد الإلكتروني: admin@yourcompany.com
كلمة المرور: admin123456
```

**⚠️ مهم: قم بتغيير كلمة مرور المدير فور تسجيل الدخول الأول!**

## اختبار API

### الحصول على مفتاح API
1. سجل دخول كمدير
2. اذهب إلى إعدادات الشركة
3. انسخ مفتاح API

### مثال على طلب API
```bash
curl -X POST http://localhost:5000/api/send-verification \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "code": "123456",
    "company_id": "YOUR_COMPANY_ID"
  }'
```

## المشاكل الشائعة

### خطأ في قاعدة البيانات
```bash
# احذف قاعدة البيانات الحالية وأعد إنشاؤها
rm app.db
python run.py init_db
python run.py create_admin
```

### خطأ في المكتبات
```bash
# أعد تثبيت المتطلبات
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### فشل إرسال البريد الإلكتروني
1. تأكد من صحة إعدادات SMTP
2. تحقق من كلمة مرور التطبيق للجيميل
3. تأكد من تفعيل "أقل أماناً" للحسابات القديمة

## للإنتاج

### استخدام Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### مع nginx
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## المساعدة

للحصول على المساعدة:
- راجع ملف README.md الكامل
- تحقق من التوثيق في /docs
- تواصل معنا عبر support@yourcompany.com

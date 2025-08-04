from app import create_app, db
from app.models import Company

app = create_app()
with app.app_context():
    admin = Company.query.filter_by(is_admin=True).first()
    if admin:
        print('✅ حساب المدير موجود')
        print(f'البريد: {admin.email}')
        print(f'SMTP: {admin.smtp_server}:{admin.smtp_port}')
        print(f'Username: {admin.smtp_username}')
        print(f'Sender: {admin.sender_email}')
    else:
        print('❌ لا يوجد حساب مدير')

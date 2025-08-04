from app import create_app, db
from app.models import Company

app = create_app()
with app.app_context():
    admin = Company.query.filter_by(is_admin=True).first()
    if admin:
        print(f'Admin email: {admin.email}')
        print(f'SMTP Server: {admin.smtp_server}')
        print(f'SMTP Username: {admin.smtp_username}')
        print(f'SMTP Password configured: {bool(admin.smtp_password)}')
        print(f'Sender Email: {admin.sender_email}')
        print(f'Sender Name: {admin.sender_name}')
    else:
        print('No admin user found')

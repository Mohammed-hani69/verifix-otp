#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إصلاح إعدادات حساب المدير
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Company

def fix_admin_account():
    """إصلاح حساب المدير"""
    print("🔧 إصلاح حساب المدير...")
    
    app = create_app()
    with app.app_context():
        admin = Company.query.filter_by(is_admin=True).first()
        
        if not admin:
            print("❌ لا يوجد حساب مدير! يجب تشغيل التطبيق أولاً لإنشائه")
            return
            
        # تحديث إعدادات SMTP
        admin.smtp_server = 'smtp.gmail.com'
        admin.smtp_port = 587
        admin.smtp_username = 'hanizezo72@gmail.com'
        admin.smtp_password = 'jxtr qylc lzkj ehpb'
        admin.sender_email = 'hanizezo72@gmail.com'
        admin.sender_name = 'Verifix-OTP'
        admin.is_verified = True
        admin.is_active = True
        
        db.session.commit()
        
        print("✅ تم تحديث إعدادات حساب المدير:")
        print(f"   البريد: {admin.email}")
        print(f"   SMTP: {admin.smtp_server}:{admin.smtp_port}")
        print(f"   المرسل: {admin.sender_email}")

if __name__ == '__main__':
    fix_admin_account()

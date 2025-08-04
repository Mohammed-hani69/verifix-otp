/* JavaScript مخصص للتطبيق */

// إعدادات عامة
const app = {
    // إعدادات API
    apiBase: '/api',
    
    // رسائل التأكيد
    confirmMessages: {
        delete: 'هل أنت متأكد من الحذف؟',
        regenerateKey: 'هل تريد إنشاء مفتاح API جديد؟ المفتاح الحالي سيتوقف عن العمل.',
        sendTest: 'هل تريد إرسال رسالة اختبار؟'
    }
};

// دالة عرض الرسائل
function showMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container:first-of-type');
    container.insertBefore(alertDiv, container.firstChild);
    
    // إزالة الرسالة بعد 5 ثوان
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// دالة إضافة حالة التحميل
function setLoading(element, loading = true) {
    if (loading) {
        element.classList.add('loading');
        element.disabled = true;
    } else {
        element.classList.remove('loading');
        element.disabled = false;
    }
}

// دالة نسخ النص
function copyToClipboard(text, button = null) {
    navigator.clipboard.writeText(text).then(() => {
        showMessage('تم نسخ النص بنجاح!', 'success');
        
        if (button) {
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="bi bi-check"></i> تم النسخ';
            button.classList.remove('btn-outline-secondary');
            button.classList.add('btn-success');
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.classList.remove('btn-success');
                button.classList.add('btn-outline-secondary');
            }, 2000);
        }
    }).catch(() => {
        showMessage('فشل في نسخ النص', 'error');
    });
}

// دالة تحديث الرصيد في الوقت الفعلي
function updateBalance() {
    if (!document.querySelector('[data-balance]')) return;
    
    const apiKeyElement = document.querySelector('[data-api-key]');
    if (!apiKeyElement) return;
    
    fetch('/api/balance', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': apiKeyElement.dataset.apiKey
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const balanceElement = document.querySelector('[data-balance]');
            const freeElement = document.querySelector('[data-free-messages]');
            
            if (balanceElement) {
                balanceElement.textContent = data.balance.toFixed(2);
            }
            
            if (freeElement) {
                freeElement.textContent = data.free_messages_remaining;
            }
            
            // تحديث حالة التحذير من انخفاض الرصيد
            if (data.balance < 50 && data.free_messages_remaining === 0) {
                showLowBalanceWarning();
            }
        }
    })
    .catch(error => {
        console.error('خطأ في تحديث الرصيد:', error);
    });
}

// دالة عرض تحذير انخفاض الرصيد
function showLowBalanceWarning() {
    const warningElement = document.querySelector('#low-balance-warning');
    if (!warningElement) {
        const alertDiv = document.createElement('div');
        alertDiv.id = 'low-balance-warning';
        alertDiv.className = 'alert alert-warning alert-dismissible fade show';
        alertDiv.innerHTML = `
            <i class="bi bi-exclamation-triangle"></i>
            <strong>تحذير:</strong> رصيدك منخفض! قم بشحن حسابك لمتابعة إرسال الرسائل.
            <a href="/dashboard/balance" class="btn btn-sm btn-warning ms-2">شحن الرصيد</a>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container:first-of-type');
        container.insertBefore(alertDiv, container.firstChild);
    }
}

// دالة معاينة القالب
function previewTemplate() {
    const htmlContent = document.querySelector('#html_content')?.value;
    const primaryColor = document.querySelector('#primary_color')?.value || '#007bff';
    const secondaryColor = document.querySelector('#secondary_color')?.value || '#6c757d';
    
    if (!htmlContent) return;
    
    // استبدال المتغيرات للمعاينة
    let previewContent = htmlContent
        .replace(/\{\{company_name\}\}/g, 'شركة تجريبية')
        .replace(/\{\{current_year\}\}/g, new Date().getFullYear())
        .replace(/\{\{primary_color\}\}/g, primaryColor)
        .replace(/\{\{secondary_color\}\}/g, secondaryColor)
        .replace(/\{\{verification_code\}\}/g, '123456')
        .replace(/\{\{customer_name\}\}/g, 'أحمد محمد')
        .replace(/\{\{order_number\}\}/g, '12345')
        .replace(/\{\{total_amount\}\}/g, '250.00')
        .replace(/\{\{message_title\}\}/g, 'عنوان الرسالة')
        .replace(/\{\{message_content\}\}/g, 'هذا محتوى تجريبي للرسالة');
    
    // فتح نافذة جديدة للمعاينة
    const previewWindow = window.open('', '_blank', 'width=800,height=600');
    previewWindow.document.write(previewContent);
    previewWindow.document.close();
}

// دالة إرسال رسالة اختبار
function sendTestEmail() {
    const testEmail = prompt('أدخل البريد الإلكتروني لإرسال رسالة اختبار:');
    if (!testEmail) return;
    
    const apiKeyElement = document.querySelector('[data-api-key]');
    if (!apiKeyElement) {
        showMessage('مفتاح API غير متوفر', 'error');
        return;
    }
    
    const button = event.target;
    setLoading(button, true);
    
    fetch('/api/send-verification', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': apiKeyElement.dataset.apiKey
        },
        body: JSON.stringify({
            email: testEmail
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('تم إرسال الرسالة التجريبية بنجاح!', 'success');
            updateBalance(); // تحديث الرصيد
        } else {
            showMessage(`خطأ: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        showMessage('حدث خطأ في الشبكة', 'error');
    })
    .finally(() => {
        setLoading(button, false);
    });
}

// دالة تحديث الإحصائيات
function updateStats() {
    // تحديث إحصائيات لوحة التحكم
    const statsElements = document.querySelectorAll('[data-stat]');
    
    statsElements.forEach(element => {
        const statType = element.dataset.stat;
        
        // إضافة تأثير العد التصاعدي
        const finalValue = parseInt(element.textContent);
        let currentValue = 0;
        const increment = finalValue / 50;
        
        const counter = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                element.textContent = finalValue;
                clearInterval(counter);
            } else {
                element.textContent = Math.floor(currentValue);
            }
        }, 20);
    });
}

// دالة إنشاء الرسوم البيانية
function createCharts() {
    // رسم بياني للرسائل المرسلة خلال الأسبوع
    const weeklyChart = document.querySelector('#weeklyChart');
    if (weeklyChart && typeof Chart !== 'undefined') {
        const ctx = weeklyChart.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['السبت', 'الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة'],
                datasets: [{
                    label: 'الرسائل المرسلة',
                    data: weeklyData || [0, 0, 0, 0, 0, 0, 0],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // رسم بياني دائري للخدمات
    const servicesChart = document.querySelector('#servicesChart');
    if (servicesChart && typeof Chart !== 'undefined') {
        const ctx = servicesChart.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['كود التحقق', 'تفاصيل الطلبات', 'رسائل ترحيبية', 'رسائل عامة'],
                datasets: [{
                    data: servicesData || [25, 30, 20, 25],
                    backgroundColor: [
                        '#667eea',
                        '#764ba2',
                        '#28a745',
                        '#ffc107'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// دالة التحقق من صحة النماذج
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    // التحقق من صحة البريد الإلكتروني
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (field.value && !emailRegex.test(field.value)) {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    return isValid;
}

// دالة تحسين تجربة المستخدم
function enhanceUI() {
    // إضافة تأثيرات على البطاقات
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('fade-in-up');
        });
    });
    
    // تحسين الجداول
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        // إضافة خاصية البحث السريع
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'form-control mb-3';
        searchInput.placeholder = 'البحث في الجدول...';
        
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
        
        table.parentNode.insertBefore(searchInput, table);
    });
}

// دالة معالجة أحداث النقرات العامة
function handleClicks() {
    document.addEventListener('click', function(e) {
        // نسخ مفتاح API
        if (e.target.matches('[data-copy-api-key]')) {
            e.preventDefault();
            const apiKey = e.target.dataset.copyApiKey;
            copyToClipboard(apiKey, e.target);
        }
        
        // إعادة إنشاء مفتاح API
        if (e.target.matches('[data-regenerate-api]')) {
            e.preventDefault();
            if (confirm(app.confirmMessages.regenerateKey)) {
                window.location.href = e.target.href;
            }
        }
        
        // حذف عنصر
        if (e.target.matches('[data-delete]')) {
            e.preventDefault();
            if (confirm(app.confirmMessages.delete)) {
                window.location.href = e.target.href;
            }
        }
        
        // إرسال رسالة اختبار
        if (e.target.matches('[data-test-email]')) {
            e.preventDefault();
            if (confirm(app.confirmMessages.sendTest)) {
                sendTestEmail();
            }
        }
        
        // معاينة القالب
        if (e.target.matches('[data-preview-template]')) {
            e.preventDefault();
            previewTemplate();
        }
    });
}

// دالة التحديث التلقائي للرصيد
function startBalanceUpdater() {
    // تحديث الرصيد كل 5 دقائق
    setInterval(updateBalance, 5 * 60 * 1000);
}

// دالة تحسين النماذج
function enhanceForms() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showMessage('يرجى ملء جميع الحقول المطلوبة بشكل صحيح', 'error');
            }
        });
        
        // إضافة تأثيرات على الحقول
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('focused');
                
                // التحقق من الصحة فور ترك الحقل
                if (this.required && !this.value.trim()) {
                    this.classList.add('is-invalid');
                } else {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
            });
        });
    });
}

// تهيئة التطبيق عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 تم تحميل Email Sender Pro');
    
    // تشغيل الوظائف الأساسية
    enhanceUI();
    handleClicks();
    enhanceForms();
    updateStats();
    createCharts();
    
    // تحديث الرصيد إذا كان المستخدم مسجل دخول
    if (document.querySelector('[data-api-key]')) {
        updateBalance();
        startBalanceUpdater();
    }
    
    // إضافة تأثيرات الحركة
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);
    
    // مراقبة العناصر للحركة
    document.querySelectorAll('.card, .stat-card, .alert').forEach(el => {
        observer.observe(el);
    });
    
    console.log('✅ تم تهيئة التطبيق بنجاح');
});

// دالة تصدير البيانات
function exportData(type) {
    const apiKey = document.querySelector('[data-api-key]')?.dataset.apiKey;
    if (!apiKey) {
        showMessage('مفتاح API غير متوفر', 'error');
        return;
    }
    
    showMessage('جاري تحضير ملف التصدير...', 'info');
    
    // يمكن إضافة المزيد من أنواع التصدير هنا
    fetch(`/api/export/${type}`, {
        headers: {
            'X-API-Key': apiKey
        }
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('فشل في تصدير البيانات');
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `export_${type}_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showMessage('تم تصدير البيانات بنجاح!', 'success');
    })
    .catch(error => {
        showMessage('فشل في تصدير البيانات', 'error');
    });
}

# 🚀 HeartFL Production Deployment Guide

## ✅ Pre-Deployment Checklist

### 1. Security Configuration ✅
- [x] Generate new SECRET_KEY
- [x] Set DEBUG=False
- [x] Configure ALLOWED_HOSTS for your domain
- [x] Enable HTTPS/SSL certificates
- [x] Configure security headers
- [x] Set SECURE_SSL_REDIRECT=True
- [x] Enable SESSION_COOKIE_SECURE and CSRF_COOKIE_SECURE
- [x] Enable HSTS (HTTP Strict Transport Security)

**Status:** ✅ Implemented in settings.py

```bash
# Run security check
python manage.py check --deploy
```

---

## 2. Environment Configuration ✅

### Create Production .env File
```bash
cp .env.example .env.production
# Edit .env.production with production settings
```

### Key Variables for Production
```env
DEBUG=False
DJANGO_SECRET_KEY=<your-secure-key-here>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
EMAIL_BACKEND=smtp
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
```

**Status:** ✅ .env.production created

---

## 3. Database Configuration ✅

### Current: SQLite3
For production, consider migrating to PostgreSQL:

#### Option 1: Continue with SQLite3
```bash
# Regular backups required
./backup_database.sh /backups/heartfl/
```

#### Option 2: Migrate to PostgreSQL (Recommended)
```bash
pip install psycopg2-binary
```

Update settings.py:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'heartfl_db',
        'USER': 'heartfl_user',
        'PASSWORD': 'strong-password-here',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**Status:** ✅ SQLite3 ready, PostgreSQL instructions provided

---

## 4. Static Files & Media Configuration ✅

### Option 1: Direct Serving (Small Projects)
```bash
python manage.py collectstatic --noinput
# Serve from /staticfiles/ directory
```

### Option 2: AWS S3 (Recommended for Scale)
```bash
pip install boto3 django-storages

# Add to .env
USE_S3=True
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=us-east-1
```

**Status:** ✅ Static files collection configured

---

## 5. Install Production Server ✅

### Gunicorn Installation
```bash
pip install gunicorn
# Already installed ✅
```

### Start with Gunicorn
```bash
# Development testing
gunicorn heartfl.wsgi:application --bind 0.0.0.0:8000

# Production with config
gunicorn -c gunicorn_config.py heartfl.wsgi
```

**Status:** ✅ Gunicorn installed and configured

---

## 6. Reverse Proxy Setup (Nginx)

### Nginx Configuration Example
```nginx
upstream heartfl {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "same-origin" always;
    
    # Compression
    gzip on;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss;
    
    # Client size limits
    client_max_body_size 50M;
    
    location /static/ {
        alias /path/to/heartfl/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /path/to/heartfl/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    location / {
        proxy_pass http://heartfl;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

**Status:** ✅ Example provided

---

## 7. SSL/HTTPS Setup

### Let's Encrypt (Free SSL Certificates)
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

**Status:** ✅ Instructions provided

---

## 8. Email Configuration ✅

### Gmail SMTP Setup
1. Enable 2-Step Verification: https://myaccount.google.com
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Add to .env.production:
```env
EMAIL_BACKEND=smtp
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
```

**Status:** ✅ Configured in settings.py

---

## 9. Database Backups ✅

### Automated Backup Script
```bash
# Make script executable
chmod +x backup_database.sh

# Backup manually
./backup_database.sh /backups/heartfl/

# Schedule with cron (daily at 2 AM)
# Add to crontab: 0 2 * * * /path/to/heartfl/backup_database.sh /backups/heartfl/
crontab -e
```

**Status:** ✅ Backup script created

---

## 10. Monitoring & Logging ✅

### Log Files
```
logs/django.log - Application logs
/var/log/heartfl/access.log - Gunicorn access log
/var/log/heartfl/error.log - Gunicorn error log
```

### Enable Log Monitoring
```bash
# Create logs directory
mkdir -p /var/log/heartfl
chmod 755 /var/log/heartfl

# Monitor logs in real-time
tail -f /var/log/heartfl/error.log
```

**Status:** ✅ Logging configured in settings.py

---

## 11. Security Hardening ✅

### CSRF Protection
- ✅ Enabled by default in Django
- Add domain to CSRF_TRUSTED_ORIGINS in settings.py

### XFrame Options
```python
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking
```

### Content Security Policy
```python
SECURE_CONTENT_SECURITY_POLICY = True
```

**Status:** ✅ Implemented in settings.py

---

## 12. Final Deployment Steps

### 1. Apply Migrations in Production
```bash
python manage.py migrate
```

### 2. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 3. Run Security Checks
```bash
python manage.py check --deploy
```

### 4. Create Systemd Service (Optional)
Create `/etc/systemd/system/heartfl.service`:
```ini
[Unit]
Description=HeartFL Gunicorn Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/heartfl
Environment="PATH=/path/to/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=heartfl.settings"
ExecStart=/path/to/venv/bin/gunicorn -c gunicorn_config.py heartfl.wsgi

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable heartfl
sudo systemctl start heartfl
sudo systemctl status heartfl
```

---

## 13. Final Verification

### Check All Deployments
```bash
# Run Django security check
python manage.py check --deploy

# Output should show no errors (only warnings are okay)
```

### Test HTTPS
```bash
curl -I https://yourdomain.com
# Should return 200 OK
```

### Test Email
```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

---

## 📊 Deployment Checklist Summary

| Task | Status | File |
|------|--------|------|
| Security Settings | ✅ | settings.py |
| Environment Config | ✅ | .env.production |
| Database Backups | ✅ | backup_database.sh |
| Gunicorn Server | ✅ | gunicorn_config.py |
| Logging Config | ✅ | settings.py |
| Email Setup | ✅ | .env.production |
| Static Files | ✅ | settings.py |
| HTTPS/SSL | ⏳ | Deploy guide |
| Nginx Reverse Proxy | ⏳ | Deploy guide |
| Monitoring | ✅ | settings.py |
| Backup Automation | ✅ | backup_database.sh |

---

## 🚀 Quick Production Launch

```bash
# 1. Navigate to project
cd /path/to/heartfl

# 2. Activate virtual environment
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# 3. Use production environment
export DJANGO_SETTINGS_MODULE=heartfl.settings

# 4. Run migrations
python manage.py migrate

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Security check
python manage.py check --deploy

# 7. Start Gunicorn
gunicorn -c gunicorn_config.py heartfl.wsgi

# Server runs on 127.0.0.1:8000
# Configure Nginx to proxy requests to this port
```

---

## 📞 Support & Troubleshooting

### Common Issues

#### 1. Static Files Not Loading
```bash
python manage.py collectstatic --noinput --clear
```

#### 2. Permission Errors
```bash
sudo chown -R www-data:www-data /path/to/heartfl
```

#### 3. Database Locked
```bash
# SQLite locks - only one process should access
# If using multiple workers, migrate to PostgreSQL
```

#### 4. Email Not Sending
```bash
# Test email configuration
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Body', 'from@example.com', ['to@example.com'])
```

---

**Last Updated:** February 26, 2026  
**Version:** 1.0.0 Production Ready

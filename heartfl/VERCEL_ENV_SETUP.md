# ============================================================================
# VERCEL ENVIRONMENT VARIABLES SETUP GUIDE
# ============================================================================
#
# IMPORTANT: This file documents which environment variables are needed
# in Vercel's Project Settings > Environment Variables section.
#
# DO NOT commit the actual .env file with real values to GitHub!
# Use this as a reference to set variables in Vercel dashboard.
#
# ============================================================================
# HOW TO SET ENVIRONMENT VARIABLES IN VERCEL
# ============================================================================
#
# 1. Go to: https://vercel.com/dashboard/projects/heartfl-django
# 2. Click on "Settings" tab
# 3. Go to "Environment Variables"
# 4. Add each variable below with Production, Preview, and Development scopes
# 5. Deploy again after adding variables
#
# ============================================================================
# REQUIRED ENVIRONMENT VARIABLES
# ============================================================================

# Django Core Configuration
DEBUG=False
DJANGO_SECRET_KEY=your-secret-key-here-generate-with-secrets-module
ALLOWED_HOSTS=heart-fl-django.vercel.app,www.heart-fl-django.vercel.app,localhost,127.0.0.1

# HTTPS/Security Configuration
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True

# Database Configuration (SQLite for Vercel - writes to /tmp or ephemeral storage)
DATABASE_URL=sqlite:///db.sqlite3

# CSRF & CORS Configuration
CSRF_TRUSTED_ORIGINS=https://heart-fl-django.vercel.app,https://www.heart-fl-django.vercel.app
CORS_ALLOWED_ORIGINS=https://heart-fl-django.vercel.app,https://www.heart-fl-django.vercel.app

# Email Configuration (Optional - using Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# ============================================================================
# OPTIONAL ENVIRONMENT VARIABLES
# ============================================================================

# Static Files (WhiteNoise)
STATIC_ROOT=/vercel/path0/staticfiles
STATIC_URL=/static/

# Media Files Location
MEDIA_ROOT=/vercel/path0/media
MEDIA_URL=/media/

# Logging Configuration
LOG_LEVEL=INFO

# ============================================================================
# ALTERNATIVE: LOCAL .env FILE (For local development only)
# ============================================================================
#
# Save the section below as .env in the heartfl/ directory
# for local development (do NOT commit to GitHub)
#
# DEBUG=True
# DJANGO_SECRET_KEY=qdVwn6JsgQJEBR0kBIc3IbpGFTbuo3rKE-EqL9MIK6ev0aP-XCzypJ1QhSlQ55HKU3U
# ALLOWED_HOSTS=localhost,127.0.0.1
# SECURE_SSL_REDIRECT=False
# CSRF_TRUSTED_ORIGINS=http://localhost:8000
# CORS_ALLOWED_ORIGINS=http://localhost:8000
# EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
#

# ============================================================================
# VERCEL DEPLOYMENT CHECKLIST
# ============================================================================
#
# Before redeploying on Vercel, ensure:
#
# ✅ Created vercel.json with build/start commands
# ✅ Created runtime.txt with Python 3.12
# ✅ Created Procfile with web process
# ✅ Ensured requirements.txt has gunicorn and whitenoise
# ✅ Set all environment variables in Vercel dashboard
# ✅ Verified Django is allowed to serve from heart-fl-django.vercel.app
# ✅ Committed all configuration files to GitHub
# ✅ Redeployed through Vercel dashboard (import project -> select heartfl as root)
#

# ============================================================================
# VERCEL SPECIFIC NOTES
# ============================================================================
#
# - File System: Vercel is read-only except /tmp/ directory
# - Database: SQLite files will be stored in /tmp/ (ephemeral)
# - Recommendations: 
#   * Consider using PostgreSQL for production persistence
#   * Use S3/Cloud Storage for media files
#   * Use managed email service (SendGrid, Mailgun) for emails
#
# - Deployment Logs: Check Vercel dashboard > Deployments for build logs
# - Function Logs: Check Vercel dashboard > Logs for runtime errors
#

# ============================================================================
# STEP-BY-STEP VERCEL SETUP (From Scratch)
# ============================================================================
#
# 1. Push all configuration files to GitHub:
#    - vercel.json
#    - runtime.txt
#    - Procfile
#    - requirements.txt (in heartfl/ directory)
#    - heartfl/heartfl/settings.py (updated with environment variables)
#
# 2. Go to https://vercel.com and sign in with GitHub
#
# 3. Click "Add New Project" or "Import Project"
#
# 4. Select the HeartFL-Django repository
#
# 5. Configure Project Settings:
#    - Framework Preset: Other
#    - Root Directory: heartfl/
#    - Build Command: Default (will use vercel.json)
#    - Output Directory: (leave blank)
#    - Environment Variables: (see above section)
#
# 6. Set Environment Variables:
#    - DJANGO_SECRET_KEY
#    - ALLOWED_HOSTS
#    - CSRF_TRUSTED_ORIGINS
#    - CORS_ALLOWED_ORIGINS
#    - EMAIL_HOST_USER
#    - EMAIL_HOST_PASSWORD
#    - All other variables from "REQUIRED" section above
#
# 7. Click "Deploy"
#
# 8. Wait for build to complete (5-10 minutes)
#
# 9. Once deployed, visit:
#    https://heart-fl-django.vercel.app/
#
# 10. Check Vercel Logs if you see 404 or 500 errors
#


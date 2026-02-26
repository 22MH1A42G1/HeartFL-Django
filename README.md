# 🩺 HeartFL-Django

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/django-5.2.11-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-Educational-orange.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen.svg)](https://github.com/22MH1A42G1/HeartFL-Django)

A comprehensive Django-based web application for heart disease risk prediction using federated learning principles. The platform enables hospitals to upload datasets and doctors to make patient-level predictions while maintaining data privacy through distributed model training.

## 📑 Quick Links

- [🔗 GitHub Repository](https://github.com/22MH1A42G1/HeartFL-Django)
- [🌿 Main Branch](https://github.com/22MH1A42G1/HeartFL-Django/tree/main)
- [📖 Full Documentation](heartfl/README.md)
- [🐛 Report Issues](https://github.com/22MH1A42G1/HeartFL-Django/issues)

---

## 🎯 Project Overview

**HeartFL** is a federated learning application designed to:
- ✅ Enable hospitals to securely contribute patient data through CSV uploads
- ✅ Support doctors in making accurate heart disease risk predictions
- ✅ Maintain data privacy by keeping sensitive information at hospital sites
- ✅ Provide real-time dashboards for monitoring federated learning progress
- ✅ Offer comprehensive reporting and analytics with PDF generation

**Version:** 1.0.0 (Production Ready)  
**Last Updated:** February 26, 2026  
**Status:** ✅ Fully Functional

---

## 🏗️ Architecture

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Django 5.2.11 |
| **Database** | SQLite3 |
| **Frontend** | Django Templates + Bootstrap 5.3 |
| **ML Framework** | scikit-learn |
| **Server** | Django Development Server (Port 8080) |
| **Python** | 3.12+ |

### System Architecture Diagram

<div align="center">
  <img src="heartfl/docs/system-architecture-diagram.gif" alt="System Architecture" width="800"/>
  <p><em>System Architecture showing the interaction between different components</em></p>
</div>

### Component Architecture

<div align="center">
  <img src="heartfl/docs/component-diagram.svg" alt="Component Diagram" width="800"/>
  <p><em>Detailed component structure of the HeartFL application</em></p>
</div>

### Use Case Diagram

<div align="center">
  <img src="heartfl/docs/usecase-diagram.gif" alt="Use Case Diagram" width="800"/>
  <p><em>User interactions and system use cases</em></p>
</div>

### Activity Workflow

<div align="center">
  <img src="heartfl/docs/activity-diagram.gif" alt="Activity Diagram" width="800"/>
  <p><em>Activity flow for prediction and federated learning processes</em></p>
</div>

---

## ✨ Key Features

### 🔐 User Management
- **Role-based authentication** (Hospital Admin, Doctor, System Admin)
- Hospital registration with email verification
- Doctor association with hospitals
- Secure password reset via OTP
- User profile management with theme preferences

### 📊 Hospital Dashboard
- Hospital profile management
- CSV dataset upload interface
- Dataset processing and validation
- Hospital statistics and analytics
- Doctor management interface
- Dataset history tracking

### 🎯 Prediction System
- Patient data entry form with clinical features
- Real-time heart disease risk prediction
- Probability scoring (0-100%)
- Prediction history with full records
- **PDF report generation** for each prediction
- Doctor-level prediction analytics

### 📈 Federated Learning
- Global FL progress visualization
- Training rounds tracking
- Model performance metrics
- Hospital participation overview
- Dataset contribution statistics
- Real-time synchronization status

### 🎨 Modern UI/UX
- **Dual Theme System** (Light Blue & Dark Green)
- Animated heartbeat background
- Glass morphism cards with backdrop blur
- Responsive Bootstrap 5.3 design
- WCAG AA accessibility compliant
- Smooth transitions and animations

---

## 🚀 Quick Start

### Prerequisites

- **OS:** Linux / Windows / macOS
- **Python:** 3.12 or higher
- **pip:** Python package manager
- **Git:** Version control

### Installation

```bash
# Clone the repository
git clone https://github.com/22MH1A42G1/HeartFL-Django.git
cd HeartFL-Django

# Install dependencies
pip install -r requirements.txt

# Navigate to project folder
cd heartfl

# Apply migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Start the server
python manage.py runserver 8080
```

### Access the Application

- **Homepage:** http://127.0.0.1:8080/
- **Admin Panel:** http://127.0.0.1:8080/admin/
- **API Documentation:** See [Full Documentation](heartfl/README.md)

---

## 📁 Project Structure

```
HeartFL-Django/
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── LICENSE                    # License information
│
└── heartfl/                   # Main Django project
    ├── manage.py              # Django CLI
    ├── db.sqlite3             # SQLite database
    ├── README.md              # Detailed documentation
    │
    ├── heartfl/               # Core project settings
    │   ├── settings.py        # Django configuration
    │   ├── urls.py            # URL routing
    │   └── wsgi.py            # WSGI configuration
    │
    ├── accounts/              # User authentication
    ├── core/                  # Core functionality
    ├── hospitals/             # Hospital management
    ├── prediction/            # ML prediction engine
    ├── federated/             # Federated learning
    │
    ├── static/                # Static assets (CSS, JS, Images)
    ├── templates/             # HTML templates
    ├── media/                 # Uploaded files
    └── docs/                  # Architecture diagrams
```

---

## 🔧 Configuration

### Database

This project uses **SQLite3** for simplicity and portability. The database file is located at `heartfl/db.sqlite3`.

### Environment Variables

Create a `.env` file in the `heartfl/` directory:

```env
# Django Settings
DEBUG=True
DJANGO_SECRET_KEY=your-secret-key-here

# Email Configuration (Optional - for OTP)
EMAIL_BACKEND=console
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 👥 User Roles & Workflows

### Hospital Admin Workflow
1. Register hospital account
2. Wait for admin verification
3. Upload patient datasets (CSV)
4. Manage doctor accounts
5. View hospital statistics

### Doctor Workflow
1. Register doctor account
2. Associate with hospital
3. Enter patient data
4. Get heart disease risk prediction
5. Download PDF reports
6. View prediction history

### System Admin Workflow
1. Access admin panel
2. Verify hospital registrations
3. Manage users and permissions
4. Monitor system statistics
5. Review contact messages

---

## 📊 Database Models

### Core Entities

- **User** - Django built-in authentication
- **UserProfile** - Extended user information
- **Hospital** - Hospital information and verification
- **Doctor** - Doctor profiles linked to hospitals
- **PatientData** - Patient clinical information
- **PredictionResult** - ML prediction outcomes
- **HospitalDataset** - Uploaded CSV datasets
- **ContactMessage** - User inquiries

For detailed model schemas, see [Full Documentation](heartfl/README.md#database-models).

---

## 🔗 API Routes

### Core Routes
```
GET  /                              # Homepage
GET  /about/                        # About page
GET  /contact/                      # Contact form
POST /api/contact/                  # Submit contact
```

### Authentication
```
GET  /accounts/login/               # Login page
GET  /accounts/register/            # Registration
GET  /accounts/register/hospital/   # Hospital signup
GET  /accounts/register/doctor/     # Doctor signup
GET  /accounts/logout/              # Logout
```

### Prediction
```
GET  /predict/                      # Prediction form
POST /predict/                      # Submit for prediction
GET  /predict/history/              # Prediction history
GET  /predict/download-report/<id>/ # Download PDF report
```

### Admin
```
GET  /admin/                        # Admin panel
```

For complete API documentation, see [Full Documentation](heartfl/README.md#api-routes--urls).

---

## 🎨 Theme System

HeartFL features a **dual theme system** with:

- **Light Blue Mode** - Professional medical interface
- **Dark Green Mode** - Easy on the eyes for extended use

Themes persist across sessions using localStorage and include:
- Animated heartbeat GIF background
- Glass morphism cards
- Smooth 0.5s transitions
- WCAG AA accessibility compliance

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test prediction

# Check system
python manage.py check
```

---

## 🛠️ Development Commands

```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver 8080

# Database shell
python manage.py dbshell
```

---

## 📝 Contributing

This is an educational project. For contributions:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is part of an educational initiative for heart disease prediction using federated learning.

**For academic/research use only.**

---

## 👥 Development Team

### Contributors

- **[Indana Aditya](https://github.com/22MH1A42G1/)**
- **[Pulagam Suresh Reddy](https://github.com/sureshreddy777)** 
- **[Mundru Jnanadeep](https://github.com/jnanadeep-2003)**
- **[Penubothu Hemanth Kumar](https://github.com/HemanthKumarPenubothu)** 

### Institution

**ADITYA COLLEGE OF ENGINEERING AND TECHNOLOGY**  
Department: Computer Science & Engineering - AI & Machine Learning  
Date Created: 2025  
Last Updated: February 26, 2026

---

## 📞 Support

For issues, questions, or contributions:

- 📧 **Email:** [admin@heartfl.local](mailto:adityaindana@gmail.com)
- 🐛 **Issues:** [GitHub Issues](https://github.com/22MH1A42G1/HeartFL-Django/issues)
- 📝 **Contact Form:** http://127.0.0.1:8080/contact/

---

## 🙏 Acknowledgments

- Django Software Foundation for the excellent web framework
- scikit-learn team for machine learning tools
- Bootstrap team for responsive UI components
- All contributors and testers

---

<div align="center">
  <p>Made with ❤️ for advancing healthcare through federated learning</p>
  <p>⭐ Star this repo if you find it helpful!</p>
</div>

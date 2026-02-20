# HeartFL v1.0

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2.28-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3.2-orange.svg)](https://scikit-learn.org/)

## 🏥 Overview

**HeartFL** is a comprehensive Django-based web application for **heart disease risk prediction** using **Federated Learning (FL)** principles. The platform enables multiple hospitals to collaboratively train machine learning models while maintaining data privacy and security. Doctors can make patient-level predictions using the globally trained model without exposing sensitive patient data.

### 🎯 Key Features

- **🔐 Privacy-Preserving**: Data never leaves hospital premises - only model weights are shared
- **🤝 Collaborative Learning**: Multiple hospitals train together for better model accuracy
- **👥 Multi-Role System**: Support for Super Admin, Hospital Admin, and Doctor roles
- **📊 Real-Time Dashboard**: Monitor federated learning rounds and prediction statistics
- **🔮 Risk Prediction**: Classify heart disease risk as Low, Medium, or High
- **📈 Model Performance Tracking**: Track accuracy across training rounds
- **🏥 Hospital Management**: Manage multiple hospitals and their datasets
- **📁 Dataset Upload**: Support for CSV dataset uploads with validation

---

## 📋 Table of Contents

- [System Architecture](#-system-architecture)
- [Database Schema](#-database-schema)
- [Use Cases](#-use-cases)
- [Activity Diagrams](#-activity-diagrams)
- [Federated Learning Flow](#-federated-learning-flow)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Usage Guide](#-usage-guide)
- [User Roles](#-user-roles)
- [Output Screenshots](#-output-screenshots)
- [API Endpoints](#-api-endpoints)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🏗️ System Architecture

The HeartFL system follows a layered architecture pattern with clear separation of concerns:

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Web Interface<br/>Django Templates]
    end
    
    subgraph "Application Layer"
        Auth[Authentication Module]
        Dashboard[Dashboard Module]
        Hospital[Hospital Management]
        Federation[Federated Learning Engine]
        Prediction[Prediction Module]
    end
    
    subgraph "Business Logic"
        FL_Train[Local Model Training]
        FL_Agg[Model Aggregation]
        FL_Pred[Risk Prediction]
        Data_Val[Data Validation]
    end
    
    subgraph "Data Layer"
        DB[(SQLite Database)]
        Media[Media Storage<br/>CSV Files]
    end
    
    subgraph "ML Framework"
        SKLearn[Scikit-Learn<br/>LogisticRegression]
        Numpy[NumPy]
        Pandas[Pandas]
    end
    
    UI --> Auth
    UI --> Dashboard
    UI --> Hospital
    UI --> Federation
    UI --> Prediction
    
    Auth --> DB
    Dashboard --> DB
    Hospital --> DB
    Hospital --> Media
    Hospital --> Data_Val
    Federation --> FL_Train
    Federation --> FL_Agg
    Federation --> DB
    Prediction --> FL_Pred
    Prediction --> DB
    
    FL_Train --> SKLearn
    FL_Train --> Pandas
    FL_Train --> Media
    FL_Agg --> Numpy
    FL_Pred --> SKLearn
    FL_Pred --> Numpy
    
    Data_Val --> Pandas
    
    style UI fill:#e1f5ff
    style Auth fill:#fff9c4
    style Dashboard fill:#fff9c4
    style Hospital fill:#fff9c4
    style Federation fill:#c8e6c9
    style Prediction fill:#c8e6c9
    style DB fill:#ffccbc
    style Media fill:#ffccbc
    style SKLearn fill:#f8bbd0
    style Numpy fill:#f8bbd0
    style Pandas fill:#f8bbd0
```

### Architecture Components

- **Frontend Layer**: Django templates with Bootstrap for responsive UI
- **Application Layer**: Five core modules handling different business domains
- **Business Logic**: Federated learning algorithms and data processing
- **Data Layer**: SQLite database and file storage for datasets
- **ML Framework**: Scikit-learn for model training and predictions

---

## 🗄️ Database Schema

```mermaid
erDiagram
    USER ||--o{ HOSPITAL : "manages (admin)"
    USER ||--o{ PREDICTION : "creates"
    HOSPITAL ||--o{ DATASET : "has"
    HOSPITAL ||--o{ HOSPITAL_MODEL : "participates"
    FL_ROUND ||--o{ HOSPITAL_MODEL : "contains"
    FL_ROUND ||--o{ GLOBAL_MODEL : "produces"
    
    USER {
        int id PK
        string username
        string email
        string password
        string role
        datetime date_joined
    }
    
    HOSPITAL {
        int id PK
        string name
        text address
        int hospital_admin_id FK
        datetime created_at
    }
    
    DATASET {
        int id PK
        int hospital_id FK
        file csv_file
        datetime uploaded_at
        int rows_count
        string status
        text error_message
    }
    
    FL_ROUND {
        int id PK
        int round_number
        string status
        datetime started_at
        datetime completed_at
        float accuracy
        int participants_count
    }
    
    HOSPITAL_MODEL {
        int id PK
        int fl_round_id FK
        int hospital_id FK
        float local_accuracy
        datetime trained_at
        json model_weights
    }
    
    GLOBAL_MODEL {
        int id PK
        int fl_round_id FK
        float global_accuracy
        json model_weights
        datetime created_at
    }
    
    PREDICTION {
        int id PK
        int doctor_id FK
        float age
        float sex
        float cp
        float trestbps
        float chol
        float fbs
        float restecg
        float thalach
        float exang
        float oldpeak
        float slope
        float ca
        float thal
        float risk_score
        int prediction
        datetime created_at
    }
```

---

## 👥 Use Cases

```mermaid
graph LR
    subgraph Actors
        SA[Super Admin]
        HA[Hospital Admin]
        DOC[Doctor]
    end
    
    subgraph "User Management"
        UC1[Register User]
        UC2[Login/Logout]
        UC3[Manage User Roles]
    end
    
    subgraph "Hospital Management"
        UC4[Create Hospital]
        UC5[View Hospitals]
        UC6[Upload Dataset]
        UC7[View Dataset Details]
    end
    
    subgraph "Federated Learning"
        UC8[Start FL Round]
        UC9[Train Local Models]
        UC10[Aggregate Models]
        UC11[View Round Results]
    end
    
    subgraph "Predictions"
        UC12[Create Prediction]
        UC13[View Predictions]
        UC14[View Risk Analysis]
    end
    
    subgraph "Dashboard"
        UC15[View Dashboard]
        UC16[View Statistics]
    end
    
    SA --> UC1
    SA --> UC3
    SA --> UC4
    SA --> UC8
    SA --> UC10
    SA --> UC15
    
    HA --> UC2
    HA --> UC5
    HA --> UC6
    HA --> UC7
    HA --> UC15
    
    DOC --> UC2
    DOC --> UC11
    DOC --> UC12
    DOC --> UC13
    DOC --> UC14
    DOC --> UC15
    
    UC8 --> UC9
    UC9 --> UC10
    
    style SA fill:#ff6b6b
    style HA fill:#4ecdc4
    style DOC fill:#95e1d3
    style UC8 fill:#ffe66d
    style UC9 fill:#ffe66d
    style UC10 fill:#ffe66d
```

---

## 🔄 Activity Diagrams

### 1. Federated Learning Round Process

```mermaid
graph TD
    Start([Start]) --> Login[Super Admin Login]
    Login --> InitRound[Initialize FL Round]
    InitRound --> CheckHospitals{Hospitals with<br/>Datasets Available?}
    
    CheckHospitals -->|No| Error1[Display Error:<br/>No Data Available]
    CheckHospitals -->|Yes| CreateRound[Create New FL Round]
    
    CreateRound --> FetchDatasets[Fetch Datasets from<br/>All Hospitals]
    FetchDatasets --> TrainLocal[Train Local Models<br/>on Each Hospital Data]
    
    TrainLocal --> ValidateModels{All Models<br/>Trained?}
    ValidateModels -->|No| Error2[Mark Round as Failed]
    ValidateModels -->|Yes| AggregateWeights[Aggregate Model Weights<br/>using Federated Averaging]
    
    AggregateWeights --> CalculateAccuracy[Calculate Global<br/>Model Accuracy]
    CalculateAccuracy --> SaveGlobal[Save Global Model<br/>Weights to Database]
    
    SaveGlobal --> UpdateRound[Update Round Status<br/>to Completed]
    UpdateRound --> NotifyUsers[Notify Participants<br/>of Completion]
    
    NotifyUsers --> End([End])
    Error1 --> End
    Error2 --> End
    
    style Start fill:#90EE90
    style End fill:#FFB6C1
    style TrainLocal fill:#FFD700
    style AggregateWeights fill:#87CEEB
    style SaveGlobal fill:#DDA0DD
    style Error1 fill:#FF6347
    style Error2 fill:#FF6347
```

### 2. Patient Risk Prediction Process

```mermaid
graph TD
    Start([Start]) --> Login[Doctor Login]
    Login --> Dashboard[Access Dashboard]
    Dashboard --> NewPred[Navigate to New Prediction]
    
    NewPred --> CheckGlobal{Global Model<br/>Available?}
    CheckGlobal -->|No| Error[Display Error:<br/>Train Model First]
    CheckGlobal -->|Yes| EnterData[Enter Patient Data:<br/>Age, Sex, CP, BP, etc.]
    
    EnterData --> ValidateForm{Form Data<br/>Valid?}
    ValidateForm -->|No| ShowErrors[Show Validation Errors]
    ShowErrors --> EnterData
    
    ValidateForm -->|Yes| PreprocessData[Preprocess Features:<br/>Standardization]
    PreprocessData --> LoadModel[Load Latest<br/>Global Model]
    
    LoadModel --> Predict[Apply Model:<br/>Calculate Risk Score]
    Predict --> InterpretResult{Risk Score<br/>Analysis}
    
    InterpretResult -->|>= 0.7| HighRisk[Classify as<br/>HIGH RISK]
    InterpretResult -->|0.4-0.69| MediumRisk[Classify as<br/>MEDIUM RISK]
    InterpretResult -->|< 0.4| LowRisk[Classify as<br/>LOW RISK]
    
    HighRisk --> SavePred[Save Prediction<br/>to Database]
    MediumRisk --> SavePred
    LowRisk --> SavePred
    
    SavePred --> DisplayResult[Display Risk Analysis<br/>& Recommendations]
    DisplayResult --> End([End])
    Error --> End
    
    style Start fill:#90EE90
    style End fill:#FFB6C1
    style HighRisk fill:#FF6347
    style MediumRisk fill:#FFA500
    style LowRisk fill:#32CD32
    style Predict fill:#87CEEB
    style SavePred fill:#DDA0DD
```

### 3. Hospital Dataset Upload Process

```mermaid
graph TD
    Start([Start]) --> Login[Hospital Admin Login]
    Login --> ViewHosp[View Hospital Details]
    ViewHosp --> UploadPage[Navigate to Upload Dataset]
    
    UploadPage --> SelectFile[Select CSV File]
    SelectFile --> ValidateFile{File Format<br/>Valid?}
    
    ValidateFile -->|No| Error1[Display Error:<br/>Invalid File Type]
    ValidateFile -->|Yes| UploadFile[Upload File to Server]
    
    UploadFile --> ParseCSV[Parse CSV File]
    ParseCSV --> ValidateColumns{Required Columns<br/>Present?}
    
    ValidateColumns -->|No| Error2[Display Error:<br/>Missing Columns]
    ValidateColumns -->|Yes| ValidateData{Data Quality<br/>Check}
    
    ValidateData -->|Invalid| Error3[Display Error:<br/>Invalid Data Values]
    ValidateData -->|Valid| CountRows[Count Data Rows]
    
    CountRows --> SaveMetadata[Save Dataset Metadata<br/>to Database]
    SaveMetadata --> UpdateStatus[Update Status to 'Ready']
    
    UpdateStatus --> IncrementCount[Increment Hospital<br/>Dataset Count]
    IncrementCount --> ShowSuccess[Display Success Message<br/>with Row Count]
    
    ShowSuccess --> End([End])
    Error1 --> End
    Error2 --> End
    Error3 --> End
    
    style Start fill:#90EE90
    style End fill:#FFB6C1
    style UploadFile fill:#FFD700
    style ParseCSV fill:#87CEEB
    style SaveMetadata fill:#DDA0DD
    style Error1 fill:#FF6347
    style Error2 fill:#FF6347
    style Error3 fill:#FF6347
    style ShowSuccess fill:#32CD32
```

---

## 🔁 Federated Learning Flow

```mermaid
flowchart LR
    subgraph H1[Hospital 1]
        D1[(Local Dataset 1<br/>CSV File)]
        M1[Local Model 1<br/>LogisticRegression]
        W1[Model Weights 1<br/>coef + intercept]
    end
    
    subgraph H2[Hospital 2]
        D2[(Local Dataset 2<br/>CSV File)]
        M2[Local Model 2<br/>LogisticRegression]
        W2[Model Weights 2<br/>coef + intercept]
    end
    
    subgraph H3[Hospital 3]
        D3[(Local Dataset 3<br/>CSV File)]
        M3[Local Model 3<br/>LogisticRegression]
        W3[Model Weights 3<br/>coef + intercept]
    end
    
    subgraph Central[Central FL Server]
        AGG[Federated Averaging<br/>Weighted by Sample Size]
        GM[Global Model<br/>Aggregated Weights]
        DB[(Database<br/>Store Rounds & Models)]
    end
    
    D1 -->|Train| M1
    D2 -->|Train| M2
    D3 -->|Train| M3
    
    M1 -->|Extract| W1
    M2 -->|Extract| W2
    M3 -->|Extract| W3
    
    W1 -->|Upload| AGG
    W2 -->|Upload| AGG
    W3 -->|Upload| AGG
    
    AGG -->|Aggregate| GM
    GM -->|Save| DB
    
    DB -.->|Download for<br/>Predictions| PRED[Doctor Predictions]
    
    style D1 fill:#e3f2fd
    style D2 fill:#e3f2fd
    style D3 fill:#e3f2fd
    style M1 fill:#fff9c4
    style M2 fill:#fff9c4
    style M3 fill:#fff9c4
    style AGG fill:#c8e6c9
    style GM fill:#f8bbd0
    style DB fill:#ffccbc
    style PRED fill:#ce93d8
```

### Federated Learning Algorithm

The system implements **Federated Averaging (FedAvg)** algorithm:

1. **Local Training**: Each hospital trains a Logistic Regression model on its local dataset
2. **Weight Extraction**: Model coefficients and intercepts are extracted
3. **Secure Aggregation**: Weights are aggregated on the central server using weighted averaging
4. **Global Model**: A global model is created from aggregated weights
5. **Distribution**: Global model is used for predictions by all doctors

**Privacy Guarantee**: Raw patient data never leaves hospital premises - only model parameters are shared.

---

## ✨ Features

### For Super Admins
- 👤 Create and manage user accounts
- 🏥 Add and configure hospitals
- 🚀 Initiate federated learning rounds
- 📊 Monitor training progress and accuracies
- 📈 View system-wide statistics

### For Hospital Admins
- 📁 Upload CSV datasets for training
- 📋 View hospital information and dataset details
- 📊 Monitor dataset statistics
- ✅ Verify data upload status

### For Doctors
- 🔮 Create patient risk predictions
- 📝 Input 13 clinical features
- 📊 View risk classifications (Low/Medium/High)
- 📈 Access prediction history
- 💡 Get risk percentage scores

### System Features
- 🔐 Role-based access control (RBAC)
- 🔒 Secure authentication and authorization
- 📊 Interactive dashboard with statistics
- 🎨 Responsive design (mobile-friendly)
- 🔄 Real-time model training status
- 📁 CSV file validation and processing
- 🧮 Automated feature standardization
- 💾 Persistent model storage

---

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 4.2.28
- **Language**: Python 3.8+
- **Database**: SQLite3
- **Authentication**: Django Auth System

### Machine Learning
- **Library**: Scikit-learn 1.3.2
- **Algorithm**: Logistic Regression
- **Data Processing**: Pandas 2.1.4, NumPy 1.26.4

### Frontend
- **Templates**: Django Templates
- **CSS Framework**: Bootstrap 5
- **JavaScript**: Vanilla JS

### Deployment
- **Server**: Django Development Server
- **Static Files**: Django Static Files Handler
- **Media Storage**: Local File System

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/HeartFL-v1.0.git
cd HeartFL-v1.0
```

### Step 2: Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Database Migrations
```bash
python manage.py migrate
```

### Step 5: Create Sample Data (Optional)
```bash
python manage.py create_sample_data
```

This creates:
- Super Admin: `admin` / `admin123`
- Hospital Admins: `admin_city`, `admin_memorial`, `admin_uni` / `City@123`, `Memorial@123`, `Uni@123`
- Doctor: `doctor1` / `Doctor@123`
- 3 Hospitals with sample datasets

### Step 6: Run the Development Server
```bash
python manage.py runserver
```

Visit **http://localhost:8000** in your browser.

---

## 📖 Usage Guide

### 1. Super Admin Workflow

**Login**: Use credentials `admin` / `admin123`

**Create Hospital**:
1. Navigate to Hospitals → Create New
2. Enter hospital name and address
3. Assign a hospital admin user
4. Save

**Start FL Round**:
1. Ensure hospitals have uploaded datasets
2. Navigate to Federation → Start New Round
3. System automatically:
   - Trains local models on each hospital's data
   - Aggregates model weights
   - Creates global model
4. View results in Round Details

### 2. Hospital Admin Workflow

**Login**: Use credentials like `admin_city` / `City@123`

**Upload Dataset**:
1. Navigate to Hospitals → Upload Dataset
2. Select CSV file with required columns:
   - age, sex, cp, trestbps, chol, fbs, restecg
   - thalach, exang, oldpeak, slope, ca, thal, target
3. System validates and processes the file
4. View dataset details and row count

### 3. Doctor Workflow

**Login**: Use credentials `doctor1` / `Doctor@123`

**Make Prediction**:
1. Navigate to Predictions → New Prediction
2. Enter patient data:
   - **Age**: Age in years
   - **Sex**: 0 = Female, 1 = Male
   - **CP**: Chest pain type (0-3)
   - **Trestbps**: Resting blood pressure
   - **Chol**: Serum cholesterol
   - **Fbs**: Fasting blood sugar > 120 mg/dl (0/1)
   - **Restecg**: Resting ECG results (0-2)
   - **Thalach**: Max heart rate achieved
   - **Exang**: Exercise induced angina (0/1)
   - **Oldpeak**: ST depression
   - **Slope**: Slope of peak exercise ST segment (0-2)
   - **Ca**: Number of major vessels (0-3)
   - **Thal**: Thalassemia (1-3)
3. Submit form
4. View risk score, classification, and recommendations

---

## 👤 User Roles

| Role | Permissions |
|------|-------------|
| **Super Admin** | Full system access, create hospitals, manage users, start FL rounds |
| **Hospital Admin** | Upload datasets, view hospital details, manage hospital data |
| **Doctor** | Create predictions, view prediction history, access dashboard |

---

## 📸 Output Screenshots

### 1. Login Page
The authentication page where users log in with their credentials based on their role.
- Clean, professional interface
- Role-based redirection after login
- Password reset functionality

### 2. Dashboard (Super Admin View)
Comprehensive overview showing:
- Total hospitals, datasets, FL rounds, and predictions
- System-wide statistics
- Quick access to all modules
- Recent activity feed

### 3. Hospital Management
**Hospital List Page**:
- Display all registered hospitals
- Hospital name, address, and admin
- Dataset count per hospital
- Quick actions (View, Edit)

**Hospital Details Page**:
- Hospital information
- List of uploaded datasets
- Dataset statistics
- Upload new dataset button

### 4. Dataset Upload
**Upload Form**:
- File selection interface
- CSV format requirements
- Real-time validation
- Progress indicator

**Upload Success**:
- Confirmation message
- Dataset row count
- Status indicator
- View dataset option

### 5. Federation Learning Rounds
**Round List Page**:
- List of all FL rounds
- Round number, status, and accuracy
- Participant count
- Start date and completion date

**Start New Round Page**:
- Initialize new training round
- Select participating hospitals (auto-selected)
- Training configuration
- Start button

**Round Detail Page**:
- Round status and progress
- Local model accuracies per hospital
- Global model accuracy
- Model weights information
- Aggregation details

### 6. Predictions
**New Prediction Form**:
- 13 input fields for patient features
- Field validation and hints
- Clear labels and placeholders
- Submit button

**Prediction Result Page**:
- Risk score with percentage
- Risk classification with color coding:
  - 🔴 **High Risk** (≥70%): Red badge
  - 🟡 **Medium Risk** (40-69%): Orange badge
  - 🟢 **Low Risk** (<40%): Green badge
- Patient feature summary
- Recommendations based on risk level
- Save to history option

**Prediction History**:
- List of all past predictions
- Date and time of prediction
- Risk score and classification
- Quick view and details
- Filter and search options

### 7. Dashboard Statistics
Visual representations including:
- Bar charts for FL round accuracies
- Pie charts for risk distribution
- Line graphs for prediction trends
- Hospital participation metrics

---

## 🔌 API Endpoints

### Authentication
- `GET /accounts/login/` - Login page
- `POST /accounts/login/` - Authenticate user
- `GET /accounts/logout/` - Logout user
- `GET /accounts/register/` - Registration page
- `POST /accounts/register/` - Create new user

### Dashboard
- `GET /dashboard/` - Main dashboard

### Hospitals
- `GET /hospitals/` - List all hospitals
- `GET /hospitals/<id>/` - Hospital details
- `GET /hospitals/upload/` - Upload dataset form
- `POST /hospitals/upload/` - Process dataset upload

### Federation
- `GET /federation/rounds/` - List FL rounds
- `GET /federation/rounds/<id>/` - Round details
- `GET /federation/start/` - Start new round form
- `POST /federation/start/` - Initiate FL round

### Predictions
- `GET /predictions/` - List predictions
- `GET /predictions/<id>/` - Prediction details
- `GET /predictions/new/` - New prediction form
- `POST /predictions/new/` - Create prediction

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards
- Follow PEP 8 for Python code
- Write docstrings for functions and classes
- Add unit tests for new features
- Update documentation as needed

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Heart Disease UCI Dataset for inspiration
- Django Community for excellent documentation
- Scikit-learn for ML capabilities
- Bootstrap for UI components


---

## 📊 Project Statistics

- **Lines of Code**: ~2,500+
- **Number of Models**: 7 Django models
- **Number of Views**: 15+ views
- **Number of Templates**: 12 templates
- **Test Coverage**: (To be implemented)

---

**Made with ❤️ for advancing healthcare through privacy-preserving AI**

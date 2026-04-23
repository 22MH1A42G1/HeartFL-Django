@echo off
REM Quick Start Script for Heart Disease Model Training
REM This script installs requirements and launches Jupyter Notebook

echo ========================================
echo Heart Disease Model Training Setup
echo ========================================
echo.

echo [1/3] Checking virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run this from the project root directory.
    pause
    exit /b 1
)

echo [2/3] Installing notebook requirements...
call venv\Scripts\activate.bat
pip install -r notebook_requirements.txt
echo.

echo [3/3] Launching Jupyter Notebook...
echo.
echo Your browser will open automatically.
echo Navigate to: Heart_Disease_Model_Training.ipynb
echo.
echo To stop the notebook server, press Ctrl+C in this window.
echo.
cd heartfl
jupyter notebook Heart_Disease_Model_Training.ipynb

pause

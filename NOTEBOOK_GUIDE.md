# Heart Disease Model Training - Quick Start Guide

## 📋 Prerequisites

1. Make sure your virtual environment is activated
2. Install notebook dependencies

## 🚀 Installation Steps

### Step 1: Install Required Packages
```bash
# Navigate to project root
cd c:\Users\LENOVO\Desktop\Final_year_projects\Heart-Disase-Prediction-FL\FL-v3

# Install notebook requirements
pip install -r notebook_requirements.txt
```

### Step 2: Launch Jupyter Notebook
```bash
# Navigate to heartfl directory
cd heartfl

# Start Jupyter Notebook
jupyter notebook
```

### Step 3: Open the Notebook
- Your browser will open automatically
- Navigate to: `Heart_Disease_Model_Training.ipynb`
- Click to open the notebook

## 📊 Using the Notebook

### Running All Cells
1. Click `Kernel` → `Restart & Run All`
2. Wait for all cells to execute (may take 5-10 minutes)
3. Scroll through to see results

### Running Cell by Cell
1. Click on a cell
2. Press `Shift + Enter` to run and move to next cell
3. Or press `Ctrl + Enter` to run and stay on current cell

## 📁 Output Files

After running the notebook, these files will be created in `ml_models/` directory:

1. **heart_disease_model.pkl** - Trained model (best performing)
2. **scaler.pkl** - Feature scaler for preprocessing
3. **label_encoders.pkl** - Encoders for categorical variables
4. **feature_names.pkl** - List of feature names
5. **model_metadata.pkl** - Model information and metrics

## 🎯 What the Notebook Does

### 1. Data Loading & Exploration
- Loads: `media/datasets/MH-HOSP-2024-001_1769405831_Hospital_A.csv`
- Displays dataset statistics
- Shows missing values and data types

### 2. Data Visualization
- Target distribution (Disease vs No Disease)
- Feature distributions
- Correlation heatmap
- Categorical features analysis

### 3. Data Preprocessing
- Encodes categorical variables:
  - Sex (M/F → 1/0)
  - ChestPainType (ASY, NAP, TA, ATA)
  - RestingECG (Normal, ST, LVH)
  - ExerciseAngina (Y/N → 1/0)
  - ST_Slope (Up, Flat, Down)
- Handles missing/zero values
- Scales features using StandardScaler

### 4. Model Training (9 Algorithms)
Trains and compares:
- ✓ Logistic Regression
- ✓ Decision Tree
- ✓ Random Forest
- ✓ Gradient Boosting
- ✓ XGBoost
- ✓ SVM (Support Vector Machine)
- ✓ K-Nearest Neighbors
- ✓ Naive Bayes
- ✓ AdaBoost

### 5. Model Evaluation
For each model, calculates:
- **Accuracy**: Overall correctness
- **Precision**: True positives / Predicted positives
- **Recall**: True positives / Actual positives
- **F1-Score**: Harmonic mean of precision and recall
- **ROC-AUC**: Area under ROC curve
- **MCC**: Matthews Correlation Coefficient
- **Cross-Validation**: 5-fold CV scores

### 6. Best Model Analysis
- Detailed confusion matrix
- ROC curve visualization
- Feature importance (for tree-based models)
- Sample predictions

### 7. Hyperparameter Tuning
- Grid search for optimal parameters
- Compares tuned vs original model
- Selects best performing version

### 8. Model Saving
- Saves best model for production use
- Compatible with Django application
- Includes all necessary preprocessing artifacts

## 📈 Expected Results

You should see:
- **Accuracy**: 80-95% (depending on data quality)
- **Best Model**: Usually Random Forest, XGBoost, or Gradient Boosting
- **Training Time**: 5-10 minutes for all models
- **Visualizations**: 10+ charts and plots

## 🔧 Troubleshooting

### Issue: Module not found error
**Solution**: Install missing package
```bash
pip install <package-name>
```

### Issue: Kernel not found
**Solution**: Install ipykernel
```bash
pip install ipykernel
python -m ipykernel install --user
```

### Issue: Jupyter won't start
**Solution**: Try these commands
```bash
# Update Jupyter
pip install --upgrade jupyter notebook

# Start with specific browser
jupyter notebook --browser=chrome
```

### Issue: Dataset not found
**Solution**: Check file path in Cell 2
- Make sure you're running from `heartfl/` directory
- Or update path to: `../heartfl/media/datasets/...`

### Issue: Memory error
**Solution**: if dataset is too large
- Reduce GridSearch parameters in hyperparameter tuning
- Use fewer models
- Sample the dataset

## 📝 Customization

### Change Test Set Size
In "Train-Test Split" cell:
```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3,  # Change from 0.2 to 0.3 (30%)
    random_state=42, stratify=y
)
```

### Add More Models
In "Model Training" cell, add to models dict:
```python
models = {
    'Logistic Regression': LogisticRegression(...),
    'Your Model': YourModelClass(...)
}
```

### Modify Hyperparameter Grid
In "Hyperparameter Tuning" cell, adjust param_grid:
```python
param_grid = {
    'n_estimators': [50, 100, 200],  # Fewer values = faster
    'max_depth': [5, 10, 20]
}
```

## 🎓 Understanding the Results

### Confusion Matrix
```
                Predicted
              No    Yes
Actual  No   [TN]  [FP]
        Yes  [FN]  [TP]
```
- **TN**: Correctly predicted No Disease
- **TP**: Correctly predicted Disease
- **FP**: False alarm (predicted disease when healthy)
- **FN**: Missed diagnosis (predicted healthy when diseased)

### Which Metric to Focus On?
- **Accuracy**: Good overall metric when classes are balanced
- **Recall**: Important for medical diagnosis (catch all diseases)
- **Precision**: Important to avoid false alarms
- **F1-Score**: Balance between precision and recall
- **ROC-AUC**: Overall model discrimination ability

### Feature Importance
Shows which features contribute most to predictions:
- High importance: Strong predictor
- Low importance: Weak predictor, could remove

## 💡 Tips

1. **Run cells in order** - Don't skip cells
2. **Check for errors** - Read error messages carefully
3. **Save frequently** - Ctrl+S to save notebook
4. **Restart kernel if stuck** - Kernel → Restart
5. **Clear output before sharing** - Cell → All Output → Clear

## 📞 Integration with Django

After training, the model files in `ml_models/` are automatically used by:
- `prediction/ml_model.py` - Prediction logic
- `prediction/views.py` - Web interface
- Simply restart the Django server to use new model

## 🎉 Success Indicators

You've successfully completed training when you see:
- ✓ All cells executed without errors
- ✓ Model comparison table displayed
- ✓ Best model identified (🏆 icon)
- ✓ Files saved in ml_models/ directory
- ✓ Final summary report displayed

## 📚 Next Steps

1. Review all evaluation metrics
2. Check if accuracy meets requirements (>80%)
3. Verify model files are saved
4. Test model through Django web interface
5. Monitor predictions in production
6. Retrain periodically with new data

---

**Happy Training! 🚀**

For questions or issues, check the Django application documentation or review the notebook comments.

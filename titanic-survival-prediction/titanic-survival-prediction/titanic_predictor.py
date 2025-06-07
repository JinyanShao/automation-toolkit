# -*- coding: utf-8 -*-
# Titanic Survival Prediction: A Machine Learning Project (Ultimate Version)

# --- 1. Import necessary libraries ---
import pandas as pd         # For data manipulation and analysis
import numpy as np          # For numerical operations
import matplotlib.pyplot as plt # For plotting
import seaborn as sns       # For enhanced plotting
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV # For splitting, cross-validation, and hyperparameter tuning
from sklearn.preprocessing import LabelEncoder, StandardScaler # For data preprocessing
from sklearn.impute import SimpleImputer # For handling missing values
from sklearn.linear_model import LogisticRegression # Model 1: Logistic Regression
from sklearn.tree import DecisionTreeClassifier # Model 2: Decision Tree
from sklearn.ensemble import RandomForestClassifier # Model 3: Random Forest
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_curve, auc # For model evaluation and ROC curve
import joblib # For saving and loading models

# --- Configuration for plotting (for better visualization) ---
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] # For Chinese display on Mac
plt.rcParams['axes.unicode_minus'] = False # For negative sign display
sns.set_style("whitegrid")

# --- 2. Load the dataset ---
print("--- Loading Titanic dataset ---")
file_path = 'train.csv'
try:
    df = pd.read_csv(file_path)
    print("Dataset loaded successfully!")
    print(f"Initial shape: {df.shape} (rows, columns)")
    print("\nFirst 5 rows of the dataset:")
    print(df.head())
except FileNotFoundError:
    print(f"Error: '{file_path}' not found. Please ensure 'train.csv' is in the correct directory.")
    exit()
except Exception as e:
    print(f"An error occurred while loading the dataset: {e}")
    exit()

# --- 3. Initial Data Exploration (EDA) - Enhanced ---
print("\n--- Enhanced Initial Data Exploration (EDA) ---")

# Survival Rate by Sex
print("\nSurvival Rate by Sex:")
print(df.groupby('Sex')['Survived'].mean())
plt.figure(figsize=(6, 4))
sns.barplot(x='Sex', y='Survived', data=df, palette='viridis')
plt.title('生存率按性别')
plt.ylabel('生存率')
plt.savefig('survival_rate_by_sex.png') # Save
plt.show()
print("Survival Rate by Sex chart generated and saved!")

# Survival Rate by Pclass
print("\nSurvival Rate by Pclass:")
print(df.groupby('Pclass')['Survived'].mean())
plt.figure(figsize=(6, 4))
sns.barplot(x='Pclass', y='Survived', data=df, palette='viridis')
plt.title('生存率按客舱等级')
plt.ylabel('生存率')
plt.savefig('survival_rate_by_pclass.png') # Save
plt.show()
print("Survival Rate by Pclass chart generated and saved!")

print("\nMissing values before imputation:")
print(df.isnull().sum())

# --- 4. Data Preprocessing ---
print("\n--- Starting Data Preprocessing ---")

# Handle missing values
imputer_median = SimpleImputer(strategy='median')
df['Age'] = imputer_median.fit_transform(df[['Age']]).ravel()
df['Fare'] = imputer_median.fit_transform(df[['Fare']]).ravel()
imputer_mode = SimpleImputer(strategy='most_frequent')
df['Embarked'] = imputer_mode.fit_transform(df[['Embarked']]).ravel()

df.drop('Cabin', axis=1, inplace=True) # Drop 'Cabin' column

# Encode categorical features
df['Sex'] = df['Sex'].map({'male': 0, 'female': 1})
df = pd.get_dummies(df, columns=['Embarked'], drop_first=True, dtype=int)

# Feature Engineering
df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
df['IsAlone'] = (df['FamilySize'] == 1).astype(int)

# Drop unnecessary columns
df.drop(['PassengerId', 'Name', 'Ticket', 'SibSp', 'Parch'], axis=1, inplace=True)

# Scale numerical features
scaler = StandardScaler()
numerical_cols = ['Age', 'Fare', 'FamilySize']
df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

print("\nData Preprocessing completed!")
print("Cleaned data sample (first 5 rows):")
print(df.head())

# --- 5. Prepare Data for Model Training ---
print("\n--- Preparing Data for Model Training ---")
X = df.drop('Survived', axis=1) # Features
y = df['Survived'] # Target variable

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"\nData split into training (80%) and testing (20%) sets.")
print(f"Training set shape: {X_train.shape}")
print(f"Testing set shape: {X_test.shape}")

# --- 6. Model Training & Evaluation (Advanced) ---
print("\n--- Starting Model Training & Evaluation (Advanced) ---")

models = {
    'Logistic Regression': LogisticRegression(random_state=42, solver='liblinear'),
    'Decision Tree': DecisionTreeClassifier(random_state=42),
    'Random Forest': RandomForestClassifier(random_state=42)
}

results = {}
best_overall_model = None
best_overall_score = 0.0

for name, model in models.items():
    print(f"\n--- Training and evaluating {name} ---")

    # --- Cross-Validation ---
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    print(f"  Cross-Validation Accuracy Scores: {cv_scores}")
    print(f"  Average Cross-Validation Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

    # --- Train on full training set and evaluate on test set ---
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"  Test Set Accuracy: {accuracy:.4f}")
    print("  Classification Report:\n", classification_report(y_test, y_pred))

    results[name] = {
        'Cross-Validation Accuracy': cv_scores.mean(),
        'Test Set Accuracy': accuracy,
        'Model': model # Store the model instance
    }
    
    # Track the best model based on average CV accuracy
    if cv_scores.mean() > best_overall_score:
        best_overall_score = cv_scores.mean()
        best_overall_model = model
        best_overall_model_name = name

print(f"\n--- Best performing model based on Average CV Accuracy: {best_overall_model_name} ---")


# --- Hyperparameter Tuning for Random Forest (Example using GridSearchCV) ---
print("\n--- Starting Hyperparameter Tuning for Random Forest (GridSearchCV) ---")

param_grid_rf = {
    'n_estimators': [50, 100, 150],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5]
}

grid_search_rf = GridSearchCV(RandomForestClassifier(random_state=42), param_grid_rf, cv=5, scoring='accuracy', n_jobs=-1)
grid_search_rf.fit(X_train, y_train)

best_rf_model = grid_search_rf.best_estimator_
print(f"\nBest Random Forest Model Parameters: {grid_search_rf.best_params_}")
print(f"Best Random Forest Model Cross-Validation Accuracy: {grid_search_rf.best_score_:.4f}")

# Evaluate best Random Forest model on test set
y_pred_best_rf = best_rf_model.predict(X_test)
accuracy_best_rf = accuracy_score(y_test, y_pred_best_rf)
print(f"Best Random Forest Model Test Set Accuracy: {accuracy_best_rf:.4f}")
print("Classification Report for Best Random Forest:\n", classification_report(y_test, y_pred_best_rf))

# --- Visualize Confusion Matrix for the best performing model (e.g., Best Random Forest) ---
print("\n--- Generating Confusion Matrix for Best Random Forest Model ---")
cm_best_rf = confusion_matrix(y_test, y_pred_best_rf)
plt.figure(figsize=(8, 6))
sns.heatmap(cm_best_rf, annot=True, fmt='d', cmap='Blues', cbar=False,
            xticklabels=['Predicted Not Survived', 'Predicted Survived'],
            yticklabels=['Actual Not Survived', 'Actual Survived'])
plt.title('Confusion Matrix for Best Random Forest Model')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.savefig('confusion_matrix_best_rf.png') # Save confusion matrix for best model
plt.show()
print("Confusion Matrix plot for Best Random Forest generated and saved!")


# --- New Feature: Feature Importance Analysis (for Tree-based models) ---
print("\n--- Starting Feature Importance Analysis ---")
# Use the best_rf_model as it's a tree-based model and provides feature importances
if hasattr(best_rf_model, 'feature_importances_'):
    importances = best_rf_model.feature_importances_
    features = X.columns
    feature_importance_df = pd.DataFrame({'Feature': features, 'Importance': importances})
    feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

    print("\nFeature Importances (Top 10):")
    print(feature_importance_df.head(10))

    # Visualize Feature Importances
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Importance', y='Feature', data=feature_importance_df.head(10), palette='viridis')
    plt.title('特征重要性 (Top 10)')
    plt.xlabel('重要性')
    plt.ylabel('特征')
    plt.tight_layout()
    plt.savefig('feature_importances.png') # Save feature importance plot
    plt.show()
    print("Feature Importances plot generated and saved!")
else:
    print("Selected model does not have feature importances attribute.")

# --- New Feature: ROC Curve (Receiver Operating Characteristic Curve) ---
print("\n--- Generating ROC Curve for Best Random Forest Model ---")
from sklearn.metrics import roc_curve, auc

y_pred_proba_rf = best_rf_model.predict_proba(X_test)[:, 1] # Probability of positive class (survival)
fpr_rf, tpr_rf, _ = roc_curve(y_test, y_pred_proba_rf)
roc_auc_rf = auc(fpr_rf, tpr_rf)

plt.figure(figsize=(8, 6))
plt.plot(fpr_rf, tpr_rf, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc_rf:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve for Best Random Forest Model')
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig('roc_curve_best_rf.png') # Save ROC curve
plt.show()
print("ROC Curve generated and saved!")


# --- New Feature: Model Saving and Loading ---
print("\n--- Saving and Loading Best Model ---")
model_filename = 'best_titanic_rf_model.joblib'
joblib.dump(best_rf_model, model_filename)
print(f"Best Random Forest model saved to {model_filename}")

# Load the model back (for demonstration)
loaded_model = joblib.load(model_filename)
print(f"Model loaded successfully from {model_filename}")

# Test loaded model
loaded_model_accuracy = accuracy_score(y_test, loaded_model.predict(X_test))
print(f"Accuracy of loaded model: {loaded_model_accuracy:.4f} (should match best RF test accuracy)")
print("\nModel saving and loading demonstrated!")


# --- 9. Final Project Summary ---
print("\n--- Project Execution Completed ---")
print("\n--- Model Performance Summary ---")
for name, res in results.items():
    print(f"{name}: Avg CV Acc: {res['Cross-Validation Accuracy']:.4f}, Test Acc: {res['Test Set Accuracy']:.4f}")
print(f"Best Tuned Random Forest Test Acc: {accuracy_best_rf:.4f}")

# Personal Goal Statement (from previous version)
goal = "我的目标是在IT领域不断学习和成长，未来成为一名优秀的软件工程师或数据科学家。"
print(f"\n我的目标是：{goal}")
print("--- End of Project ---")
# -*- coding: utf-8 -*-
# Titanic Survival Prediction: A Machine Learning Project

# --- 1. Import necessary libraries ---
import pandas as pd         # For data manipulation and analysis
import numpy as np          # For numerical operations
import matplotlib.pyplot as plt # For plotting (optional, but good for EDA)
import seaborn as sns       # For enhanced plotting (optional, but good for EDA)
from sklearn.model_selection import train_test_split # For splitting data into training and testing sets
from sklearn.preprocessing import LabelEncoder, StandardScaler # For data preprocessing (encoding categorical, scaling numerical)
from sklearn.impute import SimpleImputer # For handling missing values
from sklearn.linear_model import LogisticRegression # Our first machine learning model
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix # For model evaluation

# --- Configuration for plotting (for better visualization) ---
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] # For Chinese display on Mac
plt.rcParams['axes.unicode_minus'] = False # For negative sign display
sns.set_style("whitegrid")

# --- 2. Load the dataset ---
print("--- Loading Titanic dataset ---")
# Ensure 'train.csv' is in the same directory as this script
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

# --- 3. Initial Data Exploration (EDA) ---
print("\n--- Initial Data Exploration (EDA) ---")
print("\nMissing values before imputation:")
print(df.isnull().sum()) # Check for missing values

# --- 4. Data Preprocessing ---
print("\n--- Starting Data Preprocessing ---")

# 4.1 Handle missing values
# 'Age' and 'Fare': Impute with median
imputer_median = SimpleImputer(strategy='median')
df['Age'] = imputer_median.fit_transform(df[['Age']])
df['Fare'] = imputer_median.fit_transform(df[['Fare']])

# 'Embarked': Impute with most frequent (mode)
imputer_mode = SimpleImputer(strategy='most_frequent')
df['Embarked'] = imputer_mode.fit_transform(df[['Embarked']])

# 'Cabin': Too many missing values, and complex for basic model. Drop this column.
df.drop('Cabin', axis=1, inplace=True)
print("\nMissing values after imputation and dropping 'Cabin':")
print(df.isnull().sum())

# 4.2 Encode categorical features
# 'Sex' (Male/Female): Convert to numerical (0/1)
df['Sex'] = df['Sex'].map({'male': 0, 'female': 1})
print("\n'Sex' column encoded (male:0, female:1).")

# 'Embarked' (S/C/Q): One-Hot Encoding
# This creates new columns for each category (e.g., Embarked_S, Embarked_C, Embarked_Q)
df = pd.get_dummies(df, columns=['Embarked'], drop_first=True, dtype=int) # drop_first avoids multicollinearity
print("\n'Embarked' column one-hot encoded.")

# 4.3 Feature Engineering (Create new features)
# 'FamilySize': Sum of 'SibSp' (siblings/spouses) and 'Parch' (parents/children) + 1 (for self)
df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
print("\n'FamilySize' (SibSp + Parch + 1) created.")

# 'IsAlone': If FamilySize is 1, then IsAlone = 1, else 0
df['IsAlone'] = (df['FamilySize'] == 1).astype(int)
print("'IsAlone' (if FamilySize == 1) created.")

# 4.4 Drop unnecessary columns for the model
# 'PassengerId', 'Name', 'Ticket', 'SibSp', 'Parch' are not directly used in this basic model
df.drop(['PassengerId', 'Name', 'Ticket', 'SibSp', 'Parch'], axis=1, inplace=True)
print("\nUnnecessary columns (PassengerId, Name, Ticket, SibSp, Parch) dropped.")

# 4.5 Scale numerical features
# 'Age', 'Fare', 'FamilySize': Standardize these features
scaler = StandardScaler()
numerical_cols = ['Age', 'Fare', 'FamilySize']
df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
print("\nNumerical features (Age, Fare, FamilySize) scaled.")

print("\nData Preprocessing completed!")
print("Cleaned data sample (first 5 rows):")
print(df.head())

# --- 5. Prepare Data for Model Training ---
print("\n--- Preparing Data for Model Training ---")

# Define features (X) and target (y)
# 'Survived' is our target variable, all other columns are features
X = df.drop('Survived', axis=1) # Features
y = df['Survived'] # Target variable

# Split data into training and testing sets
# test_size=0.2 means 20% of data for testing, 80% for training
# random_state ensures reproducibility of the split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"\nData split into training (80%) and testing (20%) sets.")
print(f"Training set shape: {X_train.shape}")
print(f"Testing set shape: {X_test.shape}")

# --- 6. Model Training ---
print("\n--- Starting Model Training (Logistic Regression) ---")

# Initialize the Logistic Regression model
model = LogisticRegression(random_state=42, solver='liblinear') # 'liblinear' solver good for small datasets

# Train the model using the training data
model.fit(X_train, y_train)

print("\nModel training completed!")

# --- 7. Model Evaluation ---
print("\n--- Starting Model Evaluation ---")

# Make predictions on the test set
y_pred = model.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {accuracy:.4f}") # Display accuracy with 4 decimal places

# Display classification report (precision, recall, f1-score)
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Display confusion matrix
print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(cm)

# Optional: Visualize Confusion Matrix (requires matplotlib/seaborn)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
            xticklabels=['Predicted Not Survived', 'Predicted Survived'],
            yticklabels=['Actual Not Survived', 'Actual Survived'])
plt.title('Confusion Matrix')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.savefig('confusion_matrix.png') # Save confusion matrix
plt.show()
print("Confusion Matrix plot generated and saved!")

print("\nModel Evaluation completed!")

# --- 8. Make Predictions (Example) ---
print("\n--- Example Prediction ---")

# Let's predict for a hypothetical new passenger
# Example: A 30-year-old female, 1st class, 0 siblings/spouses, 0 parents/children, embarked from S
# Features: Pclass, Sex, Age, Fare, FamilySize, IsAlone, Embarked_Q, Embarked_S
# Note: For prediction, new data MUST be preprocessed (scaled, encoded) exactly like training data.

# Create a DataFrame for hypothetical new data (ensure column order matches X_train)
# For simplicity, we use random data here, but in a real scenario, you'd collect actual new passenger data
# We get the first row of X_test as an example for structure and scale
example_passenger_features = X_test.iloc[0:1] # Take the first test passenger as an example
example_passenger_prediction = model.predict(example_passenger_features)
example_passenger_proba = model.predict_proba(example_passenger_features)

print(f"\nPrediction for example passenger (features of 1st test sample): {example_passenger_prediction[0]}")
print(f"Probability of Not Survived: {example_passenger_proba[0][0]:.4f}")
print(f"Probability of Survived: {example_passenger_proba[0][1]:.4f}")
print("0 means Not Survived, 1 means Survived")
print("\n--- Project Execution Completed ---")
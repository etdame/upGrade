#!/usr/bin/env python3
"""
train_model.py

Train a LinearRegression model on the student performance dataset
and serialize the fitted model to `model.joblib`.
"""

import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import joblib

# Paths (adjust DATA_PATH if your CSV is located elsewhere)
BASE_DIR    = os.path.dirname(__file__)
DATA_PATH   = os.path.join(BASE_DIR, '..', 'research', 'data', 'student_habits_performance.csv')
MODEL_PATH  = os.path.join(BASE_DIR, 'model.joblib')

def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    """Map categorical columns to numeric codes."""
    gender_map = {'Female': 0, 'Male': 1, 'Other': 2}
    binary_map = {'No': 0, 'Yes': 1}
    diet_map   = {'Poor': 0, 'Fair': 1, 'Good': 2}
    internet_map = {'Poor': 0, 'Average': 1, 'Good': 2}

    df['gender'] = df['gender'].map(gender_map)
    df['part_time_job'] = df['part_time_job'].map(binary_map)
    df['extracurricular_participation'] = df['extracurricular_participation'].map(binary_map)
    df['diet_quality'] = df['diet_quality'].map(diet_map)
    df['internet_quality'] = df['internet_quality'].map(internet_map)
    return df

def main():
    print(f"Loading data from {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    df = encode_features(df)
    X = df.drop(columns=['exam_score'])
    y = df['exam_score']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 5. Train 
    model = LinearRegression()
    model.fit(X_train, y_train)

    # 6. Evaluate
    train_r2 = model.score(X_train, y_train)
    test_r2  = model.score(X_test, y_test)
    print(f"Training R²: {train_r2:.3f}")
    print(f"Test     R²: {test_r2:.3f}")

    # 7. Serialize
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    main()
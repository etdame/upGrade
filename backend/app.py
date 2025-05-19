from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

# 1) Define the input schema
class StudentFeatures(BaseModel):
    age: int # 0,1
    gender: int # 0,1
    study_hours_per_day: float #0-24
    social_media_hours: float #0-24
    netflix_hours: float #0-24
    part_time_job: int # 0,1
    attendance_percentage: float # 99.9
    sleep_hours: float # 0-24
    diet_quality: int # 0,1,2
    exercise_frequency: int # 0,1,2
    internet_quality: int # 0,1,2
    mental_health_rating: int # 0-10
    extracurricular_participation: int # 0,1

# 2) Load your frozen model
model = joblib.load("model.joblib")

# 3) Spin up FastAPI
app = FastAPI(title="UpGrade Exam Score Predictor")

@app.post("/predict")
def predict(student: StudentFeatures):
    # Assemble feature vector in same order used for training
    X = np.array([[
        student.age,
        student.gender,
        student.study_hours_per_day,
        student.social_media_hours,
        student.netflix_hours,
        student.part_time_job,
        student.attendance_percentage,
        student.sleep_hours,
        student.diet_quality,
        student.exercise_frequency,
        student.internet_quality,
        student.mental_health_rating,
        student.extracurricular_participation,
    ]])
    y_hat = model.predict(X)[0]
    return {"predicted_exam_score": round(float(y_hat), 2)}

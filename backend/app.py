from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
from typing import List, Dict

# 1) Create a single FastAPI instance
app = FastAPI(title="UpGrade Exam Score Predictor")

# 2) Enable CORS so your frontend (likely on port 5173) can talk to it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # tighten this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3) Health check
@app.get("/health")
def health():
    return {"message": "connected"}

# Input schema
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

# Load model
model = joblib.load("model.joblib")

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

class RecommendRequest(StudentFeatures):
    desired_score: float

class RecommendResponse(BaseModel):
    updated_features: Dict[str, float]
    predicted_score: float

@app.post("/recommend",response_model=RecommendResponse)
def recommend(rq:RecommendRequest):
    feat_names=[
        "age","gender","study_hours_per_day","social_media_hours","netflix_hours",
        "part_time_job","attendance_percentage","sleep_hours","diet_quality",
        "exercise_frequency","internet_quality","mental_health_rating",
        "extracurricular_participation"
    ]
    X_curr=np.array([[
        rq.age,rq.gender,rq.study_hours_per_day,
        rq.social_media_hours,rq.netflix_hours,
        rq.part_time_job,rq.attendance_percentage,
        rq.sleep_hours,rq.diet_quality,
        rq.exercise_frequency,
        rq.internet_quality,rq.mental_health_rating,
        rq.extracurricular_participation
    ]],dtype=float).flatten().tolist()

    beta=dict(zip(feat_names,model.coef_))
    targets={
        "sleep_hours":8.0,
        "diet_quality":1.0,
        "exercise_frequency":1.0,
        "mental_health_rating":6.0,
        "study_hours_per_day":6.0,
        "attendance_percentage":90.0,
        "extracurricular_participation":1.0,
        "part_time_job":1.0,
        "social_media_hours":1.0,
        "netflix_hours":2.0
    }
    priority=[
        "sleep_hours","diet_quality","exercise_frequency",
        "mental_health_rating","study_hours_per_day",
        "attendance_percentage","extracurricular_participation",
        "part_time_job","social_media_hours","netflix_hours"
    ]

    idx_map={n:i for i,n in enumerate(feat_names)}
    time_idxs={feat:idx_map[feat] for feat in
               ("sleep_hours","study_hours_per_day",
                "social_media_hours","netflix_hours")}

    X_mod=X_curr.copy()
    # 1) hard minima for core health
    for feat in priority[:4]:
        X_mod[idx_map[feat]]=targets[feat]
    # 2) enforce entertainment minima
    for ent,val in (("social_media_hours",1.0),("netflix_hours",2.0)):
        i=idx_map[ent]
        if X_curr[i]>0:
            X_mod[i]=val
    # 3) check 24h budget
    if sum(X_mod[i] for i in time_idxs.values())>24:
        raise ValueError("Hard minima exceed 24h")

    # 4) baseline & gap
    y_hat=float(model.predict([X_mod])[0])
    remaining=rq.desired_score-y_hat

    # 5) greedy adjust the rest
    for feat in priority[4:]:
        if remaining<=0:break
        coef=beta[feat]
        if coef<=0:continue
        idx=idx_map[feat]
        curr=X_mod[idx]
        max_step=targets[feat]-curr
        if max_step<=0:continue
        needed=remaining/coef
        if feat in ("diet_quality","exercise_frequency",
                    "extracurricular_participation","part_time_job"):
            step=min(max_step,max(1,int(round(needed))))
        else:
            step=min(max_step,needed)
        if feat in time_idxs:
            old=curr
            X_mod[idx]=old+step
            if sum(X_mod[i] for i in time_idxs.values())>24:
                X_mod[idx]=old
                continue
        else:
            X_mod[idx]=curr+step
        remaining-=coef*step

    y_new=float(model.predict([X_mod])[0])
    return{
        "updated_features":dict(zip(feat_names,X_mod)),
        "predicted_score":round(y_new,2)
    }

# 🎓 UpGrade

**UpGrade** helps students predict their exam scores based on current habits and, if desired, recommends habit adjustments to reach a target score, while keeping health and daily time constraints in mind.

## 🔍 Overview

- **Predict Mode**  
  - Enter your current habits (study hours, sleep, diet, etc.)  
  - Instantly see a predicted exam score via a trained linear regression model  
  - Animated “count-up” percentage for a polished user experience

- **Optimize Mode**  
  - Specify a desired exam score  
  - UpGrade analyzes your habits and suggests which to tweak (sleep, study, diet, exercise, attendance, etc.)  
  - Honors a 24 h daily budget and enforces healthy minimums (sleep ≥ 8 h, diet ≥ “Fair,” exercise ≥ once/week, mental health ≥ 6)  
  - Color-coded, animated adjustments so you know exactly what to improve

## 🛠 Tech Stack

- **Frontend**:  
  • Svelte (component-based UI)  
  • Tailwind CSS (dark-mode theme + utility-style classes)  
  • Svelte Motion (`tweened`) for smooth number animations  
  • Fetch API to call backend endpoints

- **Backend**:  
  • FastAPI (Python) with CORS enabled  
  • scikit-learn LinearRegression model stored as `model.joblib`  
  • joblib for serialization  
  • Uvicorn as the ASGI server

- **Data & Model Training**:  
  • Pandas & NumPy for data loading and preprocessing  
  • A Jupyter notebook in `research/` for initial exploration and training  
  • `train_model.py` to retrain and dump the serialized model

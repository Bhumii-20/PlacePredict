import os
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib


# =========================================================
# 1. CREATE PROJECT DIRECTORIES
# =========================================================

os.makedirs("data", exist_ok=True)
os.makedirs("model", exist_ok=True)


# =========================================================
# 2. GENERATE TRAINING DATA
# =========================================================

np.random.seed(42)

number_of_students = 1000


# Branch values match preprocessing.py
# 1  = Computer Science
# 2  = Information Technology
# 3  = Electronics
# 4  = Mechanical
# 5  = Civil
# 6  = Electrical
# 7  = Data Science
# 8  = Artificial Intelligence
# 9  = Commerce / Business Administration
# 10 = Design / Architecture / Media / Other

branch_values = np.random.randint(
    1,
    11,
    number_of_students
)


data = {
    "cgpa": np.round(
        np.random.uniform(5.0, 10.0, number_of_students),
        2
    ),

    "tenth_percentage": np.round(
        np.random.uniform(50, 100, number_of_students),
        2
    ),

    "twelfth_percentage": np.round(
        np.random.uniform(50, 100, number_of_students),
        2
    ),

    "backlogs": np.random.randint(
        0,
        6,
        number_of_students
    ),

    # 0 is allowed because a student may enter no skills
    "technical_skills": np.random.randint(
        0,
        11,
        number_of_students
    ),

    # 0 is allowed because a student may enter no languages/tools
    "programming_languages": np.random.randint(
        0,
        6,
        number_of_students
    ),

    "projects": np.random.randint(
        0,
        6,
        number_of_students
    ),

    "internships": np.random.randint(
        0,
        4,
        number_of_students
    ),

    "certifications": np.random.randint(
        0,
        7,
        number_of_students
    ),

    "aptitude_score": np.round(
        np.random.uniform(30, 100, number_of_students),
        2
    ),

    "communication_score": np.round(
        np.random.uniform(30, 100, number_of_students),
        2
    ),

    "branch": branch_values,

    # Matches preprocessing.py:
    # First Year = 1
    # Second Year = 2
    # Third Year = 3
    # Fourth/Final Year = 4
    "year": np.random.randint(
        1,
        5,
        number_of_students
    )
}


df = pd.DataFrame(data)


# =========================================================
# 3. CREATE PLACEMENT TARGET
# =========================================================

score = (
    df["cgpa"] * 8
    + df["tenth_percentage"] * 0.15
    + df["twelfth_percentage"] * 0.15
    - df["backlogs"] * 5
    + df["technical_skills"] * 2
    + df["programming_languages"] * 2
    + df["projects"] * 3
    + df["internships"] * 4
    + df["certifications"] * 1.5
    + df["aptitude_score"] * 0.20
    + df["communication_score"] * 0.15
)


# Median score is used to divide the synthetic
# training records into placed / not placed classes.
threshold = score.median()

df["placed"] = (
    score >= threshold
).astype(int)


# =========================================================
# 4. SAVE TRAINING DATASET
# =========================================================

dataset_path = "data/placement_training_data.csv"

df.to_csv(
    dataset_path,
    index=False
)

print("Training dataset created successfully.")
print(f"Dataset saved at: {dataset_path}")
print(f"Total records: {len(df)}")


# =========================================================
# 5. PREPARE FEATURES
# =========================================================

features = [
    "cgpa",
    "tenth_percentage",
    "twelfth_percentage",
    "backlogs",
    "technical_skills",
    "programming_languages",
    "projects",
    "internships",
    "certifications",
    "aptitude_score",
    "communication_score",
    "branch",
    "year"
]


X = df[features]
y = df["placed"]


# =========================================================
# 6. TRAIN / TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# =========================================================
# 7. TRAIN RANDOM FOREST MODEL
# =========================================================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    max_depth=10
)

model.fit(
    X_train,
    y_train
)


# =========================================================
# 8. EVALUATE MODEL
# =========================================================

y_pred = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    y_pred
)


print()
print("==========================================")
print("MODEL TRAINING COMPLETED")
print("==========================================")

print(
    f"Model Accuracy: {accuracy * 100:.2f}%"
)

print()
print("Classification Report:")

print(
    classification_report(
        y_test,
        y_pred
    )
)


# =========================================================
# 9. FEATURE IMPORTANCE
# =========================================================

print()
print("Feature Importance:")
print("------------------------------------------")

feature_importance = pd.DataFrame({
    "Feature": features,
    "Importance": model.feature_importances_
})

feature_importance = feature_importance.sort_values(
    by="Importance",
    ascending=False
)

for _, row in feature_importance.iterrows():
    print(
        f"{row['Feature']:<25} "
        f"{row['Importance']:.4f}"
    )


# =========================================================
# 10. SAVE MODEL
# =========================================================

model_path = "model/placement_model.pkl"

joblib.dump(
    model,
    model_path
)

print()
print(
    f"Model saved successfully at: {model_path}"
)

print("==========================================")
import os
import joblib
import pandas as pd

from preprocessing import prepare_student_input


# ============================================================
# MODEL PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model",
    "placement_model.pkl"
)


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():
    """
    Load the trained Machine Learning model.
    """

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Trained model not found at: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


# ============================================================
# PREDICT PLACEMENT
# ============================================================

def predict_placement(
    cgpa,
    tenth_percentage,
    twelfth_percentage,
    backlogs,
    technical_skills,
    programming_languages,
    projects,
    internships,
    certifications,
    aptitude_score,
    communication_score,
    stream,
    year
):
    """
    Prepare manually entered student information
    and generate placement prediction.

    Returns:
        prediction  -> 0 or 1
        probability -> placement probability between 0 and 1
    """

    # --------------------------------------------------------
    # PREPARE STUDENT INPUT
    # --------------------------------------------------------

    student_data = prepare_student_input(
        cgpa=cgpa,
        tenth_percentage=tenth_percentage,
        twelfth_percentage=twelfth_percentage,
        backlogs=backlogs,
        technical_skills=technical_skills,
        programming_languages=programming_languages,
        projects=projects,
        internships=internships,
        certifications=certifications,
        aptitude_score=aptitude_score,
        communication_score=communication_score,
        stream=stream,
        year=year
    )


    # --------------------------------------------------------
    # CONVERT TO DATAFRAME
    # --------------------------------------------------------

    input_data = pd.DataFrame(
        [student_data]
    )


    # --------------------------------------------------------
    # LOAD TRAINED MODEL
    # --------------------------------------------------------

    model = load_model()


    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    prediction = model.predict(
        input_data
    )[0]


    # --------------------------------------------------------
    # PLACEMENT PROBABILITY
    # --------------------------------------------------------

    if hasattr(model, "predict_proba"):

        probability = model.predict_proba(
            input_data
        )[0][1]

    else:

        probability = float(
            prediction
        )


    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return prediction, probability
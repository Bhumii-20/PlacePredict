# preprocessing.py

# Convert student's selected stream into a numeric value
BRANCH_MAPPING = {
    "Computer Science": 1,
    "Information Technology": 2,
    "Electronics": 3,
    "Mechanical": 4,
    "Civil": 5,
    "Electrical": 6,
    "Data Science": 7,
    "Artificial Intelligence": 8,
    "Commerce": 9,
    "Business Administration": 9,
    "Fashion Design": 10,
    "Interior Design": 10,
    "Architecture": 10,
    "Graphic Design": 10,
    "Media & Journalism": 10,
    "Other": 10
}

# Convert year selection into a number
YEAR_MAPPING = {
    "First Year": 1,
    "Second Year": 2,
    "Third Year": 3,
    "Fourth Year": 4,
    "Final Year": 4
}


def convert_branch(stream):
    """
    Convert selected stream/course into
    the numeric branch value used by the ML model.
    """

    return BRANCH_MAPPING.get(stream, 10)


def convert_year(year):
    """
    Convert selected academic year into
    a numeric value.
    """

    return YEAR_MAPPING.get(year, 1)


def count_items(text):
    """
    Count comma-separated skills/languages.

    Example:
    Python, Java, SQL

    returns:
    3
    """

    if not text or not text.strip():
        return 0

    items = [
        item.strip()
        for item in text.split(",")
        if item.strip()
    ]

    return len(items)


def prepare_student_input(
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
    for the machine learning model.
    """

    branch = convert_branch(stream)
    year_number = convert_year(year)

    technical_skill_count = count_items(technical_skills)
    programming_language_count = count_items(
        programming_languages
    )

    return {
        "cgpa": cgpa,
        "tenth_percentage": tenth_percentage,
        "twelfth_percentage": twelfth_percentage,
        "backlogs": backlogs,
        "technical_skills": technical_skill_count,
        "programming_languages": programming_language_count,
        "projects": projects,
        "internships": internships,
        "certifications": certifications,
        "aptitude_score": aptitude_score,
        "communication_score": communication_score,
        "branch": branch,
        "year": year_number
    }
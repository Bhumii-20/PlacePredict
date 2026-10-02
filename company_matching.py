# company_matching.py

# ============================================================
# COMPANY RECOMMENDATIONS
# ============================================================

COMPANIES_BY_CAREER = {

    "Software Development": [
        "TCS",
        "Infosys",
        "Wipro",
        "Accenture",
        "Cognizant"
    ],

    "Data Analytics": [
        "Accenture",
        "Deloitte",
        "TCS",
        "Infosys",
        "Capgemini"
    ],

    "Data Science": [
        "TCS",
        "Accenture",
        "IBM",
        "Deloitte",
        "Infosys"
    ],

    "Machine Learning": [
        "Google",
        "Microsoft",
        "IBM",
        "Amazon",
        "Accenture"
    ],

    "Artificial Intelligence": [
        "Google",
        "Microsoft",
        "IBM",
        "Amazon",
        "Accenture"
    ],

    "Web Development": [
        "TCS",
        "Infosys",
        "Wipro",
        "Accenture",
        "Cognizant"
    ],

    "Cyber Security": [
        "IBM",
        "Accenture",
        "Deloitte",
        "TCS",
        "Wipro"
    ],

    "Cloud Computing": [
        "Amazon",
        "Microsoft",
        "Google",
        "IBM",
        "Accenture"
    ],

    "Business Analytics": [
        "Deloitte",
        "Accenture",
        "EY",
        "KPMG",
        "Capgemini"
    ],

    "Finance": [
        "Deloitte",
        "EY",
        "KPMG",
        "PwC",
        "ICICI Bank"
    ],

    "Marketing": [
        "Hindustan Unilever",
        "P&G",
        "Coca-Cola",
        "Deloitte",
        "Accenture"
    ],

    "Human Resources": [
        "Deloitte",
        "Accenture",
        "TCS",
        "Infosys",
        "Wipro"
    ],

    "Fashion & Design": [
        "Aditya Birla Fashion and Retail",
        "Reliance Brands",
        "Fabindia",
        "Raymond",
        "Myntra"
    ],

    "Architecture": [
        "HBA",
        "AECOM",
        "Gensler",
        "DLR Group",
        "Arcadis"
    ],

    "Graphic Design": [
        "Adobe",
        "Canva",
        "Accenture",
        "Deloitte",
        "TCS"
    ],

    "UI/UX Design": [
        "Adobe",
        "Microsoft",
        "Google",
        "IBM",
        "Accenture"
    ],

    "Media & Journalism": [
        "Times Group",
        "NDTV",
        "India Today Group",
        "Network18",
        "Zee Media"
    ],

    "Healthcare": [
        "Apollo Hospitals",
        "Fortis Healthcare",
        "Max Healthcare",
        "Tata Medical Center",
        "Manipal Hospitals"
    ],

    "Education": [
        "BYJU'S",
        "Unacademy",
        "upGrad",
        "Vedantu",
        "Simplilearn"
    ],

    "Hospitality & Tourism": [
        "Taj Hotels",
        "ITC Hotels",
        "Marriott",
        "Hyatt",
        "Oberoi Hotels"
    ],

    "Other": [
        "TCS",
        "Infosys",
        "Accenture",
        "Deloitte",
        "Wipro"
    ]
}


# ============================================================
# GET COMPANY RECOMMENDATIONS
# ============================================================

def get_company_recommendations(
    preferred_career,
    preferred_location=None
):
    """
    Return companies suitable for the selected career.

    preferred_location is accepted so the function can later
    be extended to provide location-specific recommendations.
    """

    companies = COMPANIES_BY_CAREER.get(
        preferred_career,
        COMPANIES_BY_CAREER["Other"]
    )

    return companies[:5]
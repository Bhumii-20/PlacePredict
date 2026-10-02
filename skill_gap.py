# skill_gap.py

# ============================================================
# CAREER SKILL REQUIREMENTS
# ============================================================

CAREER_SKILLS = {

    "Software Development": [
        "Python",
        "Java",
        "SQL",
        "Data Structures",
        "Git",
        "Problem Solving"
    ],

    "Data Analytics": [
        "Python",
        "SQL",
        "Excel",
        "Power BI",
        "Statistics",
        "Data Visualization"
    ],

    "Data Science": [
        "Python",
        "SQL",
        "Statistics",
        "Pandas",
        "Machine Learning",
        "Data Visualization"
    ],

    "Machine Learning": [
        "Python",
        "Statistics",
        "Pandas",
        "NumPy",
        "Machine Learning",
        "Scikit-learn"
    ],

    "Artificial Intelligence": [
        "Python",
        "Machine Learning",
        "Deep Learning",
        "Statistics",
        "Neural Networks",
        "Data Structures"
    ],

    "Web Development": [
        "HTML",
        "CSS",
        "JavaScript",
        "Git",
        "SQL",
        "Web Development"
    ],

    "Cyber Security": [
        "Networking",
        "Linux",
        "Python",
        "Cyber Security",
        "Cryptography",
        "Ethical Hacking"
    ],

    "Cloud Computing": [
        "Linux",
        "Networking",
        "Python",
        "Cloud Computing",
        "DevOps",
        "Git"
    ],

    "Business Analytics": [
        "Excel",
        "SQL",
        "Power BI",
        "Statistics",
        "Data Visualization",
        "Business Analysis"
    ],

    "Finance": [
        "Excel",
        "Financial Analysis",
        "Accounting",
        "Statistics",
        "Data Analysis",
        "Communication"
    ],

    "Marketing": [
        "Digital Marketing",
        "SEO",
        "Social Media Marketing",
        "Communication",
        "Analytics",
        "Content Creation"
    ],

    "Human Resources": [
        "Communication",
        "Recruitment",
        "HR Analytics",
        "Excel",
        "Leadership",
        "Interview Skills"
    ],

    "Fashion & Design": [
        "Fashion Design",
        "Illustration",
        "Textile Knowledge",
        "Design Software",
        "Creativity",
        "Portfolio Development"
    ],

    "Architecture": [
        "AutoCAD",
        "3D Modeling",
        "Architectural Design",
        "Sketching",
        "Building Materials",
        "Portfolio Development"
    ],

    "Graphic Design": [
        "Photoshop",
        "Illustrator",
        "Typography",
        "Color Theory",
        "Graphic Design",
        "Portfolio Development"
    ],

    "UI/UX Design": [
        "Figma",
        "UI Design",
        "UX Research",
        "Wireframing",
        "Prototyping",
        "User Testing"
    ],

    "Media & Journalism": [
        "Writing",
        "Communication",
        "Journalism",
        "Video Editing",
        "Research",
        "Digital Media"
    ],

    "Healthcare": [
        "Communication",
        "Healthcare Knowledge",
        "Patient Care",
        "Documentation",
        "Teamwork",
        "Medical Ethics"
    ],

    "Education": [
        "Communication",
        "Teaching",
        "Presentation",
        "Lesson Planning",
        "Leadership",
        "Classroom Management"
    ],

    "Hospitality & Tourism": [
        "Communication",
        "Customer Service",
        "Hospitality Management",
        "Event Management",
        "Teamwork",
        "Problem Solving"
    ]
}


# ============================================================
# SKILL ALIASES
# ============================================================
# Different words can represent the same career skill.

SKILL_ALIASES = {

    # ---------------- FASHION ----------------

    "fashion design": [
        "fashion",
        "fashion designing",
        "fashion designer",
        "fashion design"
    ],

    "illustration": [
        "fashion illustration",
        "illustration",
        "drawing",
        "sketching"
    ],

    "textile knowledge": [
        "textile",
        "textiles",
        "textile design",
        "textile knowledge",
        "fabric",
        "fabric knowledge"
    ],

    "design software": [
        "fashion cad",
        "cad",
        "fashion cad software",
        "design software",
        "adobe illustrator",
        "illustrator",
        "photoshop",
        "coreldraw"
    ],

    "creativity": [
        "creativity",
        "creative",
        "creative thinking",
        "design thinking"
    ],

    "portfolio development": [
        "portfolio",
        "portfolio development",
        "design portfolio",
        "fashion portfolio"
    ],


    # ---------------- DATA SCIENCE ----------------

    "python": [
        "python",
        "python programming",
        "python language"
    ],

    "sql": [
        "sql",
        "mysql",
        "postgresql",
        "database"
    ],

    "pandas": [
        "pandas",
        "python pandas"
    ],

    "numpy": [
        "numpy",
        "python numpy"
    ],

    "machine learning": [
        "machine learning",
        "ml",
        "machine-learning"
    ],

    "statistics": [
        "statistics",
        "statistical analysis",
        "statistical methods"
    ],

    "data visualization": [
        "data visualization",
        "data visualisation",
        "visualization",
        "visualisation",
        "charts",
        "matplotlib",
        "power bi",
        "tableau"
    ],


    # ---------------- SOFTWARE DEVELOPMENT ----------------

    "data structures": [
        "data structures",
        "dsa",
        "data structure"
    ],

    "problem solving": [
        "problem solving",
        "problem-solving",
        "logical thinking"
    ],

    "git": [
        "git",
        "github",
        "gitlab",
        "version control"
    ],


    # ---------------- WEB DEVELOPMENT ----------------

    "html": [
        "html",
        "html5"
    ],

    "css": [
        "css",
        "css3"
    ],

    "javascript": [
        "javascript",
        "js"
    ],


    # ---------------- DESIGN ----------------

    "photoshop": [
        "photoshop",
        "adobe photoshop"
    ],

    "illustrator": [
        "illustrator",
        "adobe illustrator"
    ],

    "figma": [
        "figma"
    ],

    "ui design": [
        "ui design",
        "user interface design",
        "ui"
    ],

    "ux research": [
        "ux research",
        "user research",
        "ux"
    ],

    "wireframing": [
        "wireframing",
        "wireframes",
        "wireframe"
    ],

    "prototyping": [
        "prototyping",
        "prototype",
        "prototypes"
    ],


    # ---------------- BUSINESS ----------------

    "excel": [
        "excel",
        "microsoft excel",
        "ms excel"
    ],

    "power bi": [
        "power bi",
        "powerbi"
    ],


    # ---------------- COMMUNICATION ----------------

    "communication": [
        "communication",
        "communication skills",
        "speaking",
        "public speaking"
    ]
}


# ============================================================
# NORMALIZE TEXT
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = str(text).lower().strip()

    text = text.replace("\n", ",")
    text = text.replace(";", ",")
    text = text.replace("|", ",")

    return text


# ============================================================
# NORMALIZE STUDENT SKILLS
# ============================================================

def normalize_skills(skill_text):

    if not skill_text:
        return set()

    skill_text = clean_text(skill_text)

    skills = set()

    for skill in skill_text.split(","):

        skill = skill.strip()

        if skill:
            skills.add(skill)

    return skills


# ============================================================
# CHECK WHETHER A REQUIRED SKILL IS PRESENT
# ============================================================

def skill_is_present(required_skill, student_skills):

    required_skill_clean = clean_text(
        required_skill
    )

    # Direct matching
    for student_skill in student_skills:

        student_skill_clean = clean_text(
            student_skill
        )

        # Exact match
        if required_skill_clean == student_skill_clean:
            return True

        # Student skill contains required skill
        if required_skill_clean in student_skill_clean:
            return True

        # Required skill contains student skill
        if student_skill_clean in required_skill_clean:
            return True

    # Alias matching
    aliases = SKILL_ALIASES.get(
        required_skill_clean,
        []
    )

    for alias in aliases:

        alias = clean_text(alias)

        for student_skill in student_skills:

            student_skill_clean = clean_text(
                student_skill
            )

            if alias == student_skill_clean:
                return True

            if alias in student_skill_clean:
                return True

            if student_skill_clean in alias:
                return True

    return False


# ============================================================
# SKILL GAP ANALYSIS
# ============================================================

def analyze_skill_gap(
    preferred_career,
    technical_skills,
    programming_languages
):

    required_skills = CAREER_SKILLS.get(
        preferred_career,
        []
    )

    technical_skill_set = normalize_skills(
        technical_skills
    )

    programming_skill_set = normalize_skills(
        programming_languages
    )

    all_student_skills = (
        technical_skill_set |
        programming_skill_set
    )


    matched_skills = []
    missing_skills = []


    # --------------------------------------------------------
    # CHECK EVERY REQUIRED SKILL
    # --------------------------------------------------------

    for skill in required_skills:

        if skill_is_present(
            skill,
            all_student_skills
        ):

            matched_skills.append(skill)

        else:

            missing_skills.append(skill)


    # --------------------------------------------------------
    # SKILL COVERAGE
    # --------------------------------------------------------

    total_skills = len(
        required_skills
    )

    if total_skills > 0:

        skill_coverage = (
            len(matched_skills)
            / total_skills
        ) * 100

    else:

        skill_coverage = 0


    # --------------------------------------------------------
    # PRIORITY LEVELS
    # --------------------------------------------------------

    priority_skills = []


    for index, skill in enumerate(
        missing_skills
    ):

        if index < 2:

            priority = "HIGH"

        elif index < 4:

            priority = "MEDIUM"

        else:

            priority = "LOW"


        priority_skills.append(
            {
                "skill": skill,
                "priority": priority
            }
        )


    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return {

        "career": preferred_career,

        "required_skills": required_skills,

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "priority_skills": priority_skills,

        "skill_coverage": skill_coverage
    }
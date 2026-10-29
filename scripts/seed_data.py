import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.models import AnswerOption, Challenge, Module, Project, ProjectMilestone, Question, Quiz, Resource, Roadmap, Skill, Lesson
from app.models import StudyMaterial
from app.study_materials_data import STUDY_MATERIALS
from extensions import db


SKILLS = [
    ("Python Programming", "Build a strong foundation in Python syntax and problem solving.", "Programming", "Beginner", 40),
    ("Web Development", "Learn the building blocks of modern web applications.", "Web Development", "Beginner", 60),
    ("SQL and Databases", "Query, model, and manage relational data.", "Databases", "Beginner", 35),
    ("Data Analysis", "Turn datasets into clear, useful insights.", "Data Analysis", "Intermediate", 45),
    ("Git and GitHub", "Collaborate confidently with version control.", "Developer Tools", "Beginner", 12),
    ("AI Fundamentals", "Understand core concepts behind practical AI systems.", "Artificial Intelligence", "Intermediate", 30),
]

ROADMAPS = [
    ("Python Programming Roadmap", "A practical path from Python basics to useful programs.", "Beginner", 40, "Python Programming"),
    ("Web Development Roadmap", "Build accessible websites with HTML, CSS, and JavaScript.", "Beginner", 60, "Web Development"),
    ("SQL and Databases Roadmap", "Learn relational thinking and reliable SQL workflows.", "Beginner", 35, "SQL and Databases"),
    ("Data Analysis Roadmap", "Explore, clean, and communicate insights from data.", "Intermediate", 45, "Data Analysis"),
    ("Git and GitHub Roadmap", "Develop a professional version-control workflow.", "Beginner", 12, "Git and GitHub"),
]

CHALLENGES = [
    ("Variables and types", "Identify Python's common built-in types.", "Python", "Beginner"),
    ("Conditions and loops", "Practice branching and repetition.", "Python", "Beginner"),
    ("Lists and dictionaries", "Organize related values in collections.", "Python", "Beginner"),
    ("Set operations", "Use sets to remove duplicates and compare groups.", "Python", "Beginner"),
    ("String manipulation", "Format and transform text safely.", "Python", "Beginner"),
    ("Basic SELECT query", "Retrieve selected columns from a table.", "SQL", "Beginner"),
    ("Filtering rows", "Use WHERE conditions to narrow results.", "SQL", "Beginner"),
    ("Sorting results", "Order query results for readability.", "SQL", "Beginner"),
    ("Counting records", "Summarize records with COUNT.", "SQL", "Beginner"),
    ("Semantic HTML", "Choose meaningful elements for a page.", "HTML/CSS", "Beginner"),
    ("CSS box model", "Control spacing and sizing with CSS.", "HTML/CSS", "Beginner"),
    ("Responsive layout", "Adapt a layout to smaller screens.", "HTML/CSS", "Intermediate"),
    ("Accessible forms", "Pair labels and controls for usability.", "HTML/CSS", "Beginner"),
    ("DOM events", "Respond to user interaction with JavaScript.", "JavaScript", "Beginner"),
    ("Debugging workflow", "Use a repeatable method to isolate a bug.", "Developer Tools", "Beginner"),
]

RESOURCES = [
    ("Python documentation", "Official Python language documentation.", "Python", "https://docs.python.org/3/", "Python.org"),
    ("Python tutorial", "A guided introduction to Python.", "Python", "https://docs.python.org/3/tutorial/", "Python.org"),
    ("MDN HTML", "Reference and guides for HTML.", "HTML/CSS/JavaScript", "https://developer.mozilla.org/en-US/docs/Web/HTML", "MDN"),
    ("MDN CSS", "Reference and guides for CSS.", "HTML/CSS/JavaScript", "https://developer.mozilla.org/en-US/docs/Web/CSS", "MDN"),
    ("MDN JavaScript", "Learn JavaScript for the web.", "HTML/CSS/JavaScript", "https://developer.mozilla.org/en-US/docs/Web/JavaScript", "MDN"),
    ("SQLite documentation", "Official SQLite language and reference docs.", "SQL", "https://www.sqlite.org/docs.html", "SQLite"),
    ("SQLBolt", "Interactive SQL lessons and exercises.", "SQL", "https://sqlbolt.com/", "SQLBolt"),
    ("Git documentation", "Official Git reference and book.", "Git and GitHub", "https://git-scm.com/doc", "Git"),
    ("GitHub Skills", "Hands-on GitHub learning exercises.", "Git and GitHub", "https://skills.github.com/", "GitHub"),
    ("pandas user guide", "Official guide to Python data analysis.", "Data Analysis", "https://pandas.pydata.org/docs/user_guide/", "pandas"),
    ("NumPy quickstart", "Fundamentals of numerical Python.", "Data Analysis", "https://numpy.org/doc/stable/user/quickstart.html", "NumPy"),
    ("Google ML Crash Course", "Practical introduction to machine learning.", "AI fundamentals", "https://developers.google.com/machine-learning/crash-course", "Google"),
    (" scikit-learn guide", "User guide for practical machine learning.", "AI fundamentals", "https://scikit-learn.org/stable/user_guide.html", "scikit-learn"),
    ("Flask documentation", "Official Flask web framework documentation.", "Python", "https://flask.palletsprojects.com/", "Flask"),
    ("Python packaging guide", "Guidance for Python project packaging.", "Python", "https://packaging.python.org/", "Python Packaging Authority"),
]

LESSONS = {
    "Python Programming Roadmap": [("Python foundations", ["Variables and data types", "Conditions and loops", "Functions and modules"]), ("Build with Python", ["Collections in practice", "Read and write files", "Build a command-line project"])],
    "Web Development Roadmap": [("Web foundations", ["Semantic HTML", "CSS layout", "Responsive design"]), ("Interactive pages", ["JavaScript basics", "DOM events", "Build an accessible page"])],
    "SQL and Databases Roadmap": [("Relational thinking", ["Tables and relationships", "SELECT and WHERE", "Sorting and grouping"]), ("Useful queries", ["Joins", "Aggregations", "Design a small database"])],
    "Data Analysis Roadmap": [("Working with data", ["Data questions", "Cleaning tabular data", "Exploratory analysis"]), ("Communicating insight", ["Charts and summaries", "Evaluate patterns", "Present a data story"])],
    "Git and GitHub Roadmap": [("Version control", ["Commits and history", "Branches", "Resolve conflicts"]), ("Collaboration", ["Pull requests", "Issue tracking", "Share a portfolio project"])],
}

PROJECTS = [
    ("Expense Tracker", "Track expenses and summarize spending.", "Beginner", "Python", "Create a small app that records expenses, validates input, and reports totals.", ["Define the data model", "Add and list expenses", "Add category summaries", "Write a clear README"]),
    ("Personal Portfolio", "Build an accessible portfolio that presents your work.", "Beginner", "HTML, CSS, JavaScript", "Create a responsive portfolio with semantic structure and a contact section.", ["Plan sections", "Build semantic HTML", "Style responsive layouts", "Test keyboard navigation"]),
    ("Library Management System", "Model books and borrowers with relational data.", "Intermediate", "Python, SQL", "Design a small database and build safe operations for library records.", ["Design tables", "Add CRUD queries", "Add search and filters", "Document the schema"]),
    ("Number Guessing Game", "Practice loops, conditions, and user feedback.", "Beginner", "Python", "Build a verified number game without executing arbitrary code.", ["Define game rules", "Handle valid input", "Track attempts", "Add replay behavior"]),
]


def seed():
    app = create_app()
    with app.app_context():
        skills = {}
        for title, description, category, difficulty, hours in SKILLS:
            skill = Skill.query.filter_by(title=title).first()
            if skill is None:
                skill = Skill(title=title, description=description, category=category, difficulty=difficulty, estimated_hours=hours)
                db.session.add(skill)
            skills[title] = skill
        db.session.flush()

        for title, description, difficulty, hours, skill_title in ROADMAPS:
            roadmap = Roadmap.query.filter_by(title=title).first()
            if roadmap is None:
                roadmap = Roadmap(title=title, description=description, difficulty=difficulty, estimated_hours=hours, skill=skills[skill_title])
                db.session.add(roadmap)
                db.session.flush()
            for module_index, (module_title, lesson_titles) in enumerate(LESSONS.get(title, []), 1):
                module = Module.query.filter_by(roadmap_id=roadmap.id, sequence_number=module_index).first()
                if module is None:
                    module = Module(roadmap_id=roadmap.id, title=module_title, description=f"Build confidence through {module_title.lower()}.", sequence_number=module_index)
                    db.session.add(module)
                    db.session.flush()
                for lesson_index, lesson_title in enumerate(lesson_titles, 1):
                    if Lesson.query.filter_by(module_id=module.id, sequence_number=lesson_index).first() is None:
                        db.session.add(Lesson(module_id=module.id, title=lesson_title, description=f"Learn and practice {lesson_title.lower()}.", content=f"Study the core ideas behind {lesson_title.lower()}, then apply them in a small practice activity.", sequence_number=lesson_index, estimated_minutes=25))

        for title, description, category, difficulty in CHALLENGES:
            if Challenge.query.filter_by(title=title).first() is None:
                db.session.add(Challenge(title=title, description=description, category=category, difficulty=difficulty, instructions=description))

        for title, description, category, url, source in RESOURCES:
            if Resource.query.filter_by(title=title).first() is None:
                db.session.add(Resource(title=title, description=description, category=category, url=url, source_name=source))

        for sequence, (subject, title, summary, concepts, example, output, mistakes, practice, revision) in enumerate(STUDY_MATERIALS, 1):
            if StudyMaterial.query.filter_by(subject=subject, title=title).first() is None:
                db.session.add(StudyMaterial(subject=subject, title=title, difficulty="Beginner", summary=summary, key_concepts=concepts, example=example, expected_output=output, common_mistakes=mistakes, practice_questions=practice, revision_summary=revision, sequence_number=sequence))

        for title, description, difficulty, stack, instructions, milestones in PROJECTS:
            project = Project.query.filter_by(title=title).first()
            if project is None:
                project = Project(title=title, description=description, difficulty=difficulty, technology_stack=stack, instructions=instructions)
                db.session.add(project)
                db.session.flush()
            for number, milestone_title in enumerate(milestones, 1):
                if ProjectMilestone.query.filter_by(project_id=project.id, sequence_number=number).first() is None:
                    db.session.add(ProjectMilestone(project_id=project.id, title=milestone_title, sequence_number=number))

        quiz = Quiz.query.filter_by(title="Python foundations check-in").first()
        if quiz is None:
            quiz = Quiz(title="Python foundations check-in", description="Check your understanding of Python basics.", category="Python")
            db.session.add(quiz)
            db.session.flush()
            questions = [
                ("Which keyword defines a function in Python?", "Functions are declared with def.", ["func", "def", "function"], 1),
                ("Which type stores an ordered collection?", "Lists preserve order and can be changed.", ["set", "list", "dict"], 1),
                ("Which statement repeats while a condition is true?", "A while loop repeats while its condition remains true.", ["while", "repeat", "loop"], 0),
            ]
            for number, (text, explanation, options, correct) in enumerate(questions, 1):
                question = Question(quiz_id=quiz.id, question_text=text, explanation=explanation, sequence_number=number)
                db.session.add(question)
                db.session.flush()
                for index, option_text in enumerate(options):
                    db.session.add(AnswerOption(question_id=question.id, option_text=option_text, is_correct=index == correct))

        db.session.commit()
        print("Seed complete: existing records were preserved and missing starter content was added.")


if __name__ == "__main__":
    seed()

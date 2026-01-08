from app.db import db
from app.models import Category, Question

def seed_data():
    if Category.query.count() > 0:
        print("Seed skipped: data already exists.")
        return

    categories = [
        Category(name="Python"),
        Category(name="SQL"),
        Category(name="HTML/CSS"),
    ]
    db.session.add_all(categories)
    db.session.commit()

    # Helper to add questions quickly
    def add_q(cat_name, prompt, a, b, c, d, correct):
        cat = Category.query.filter_by(name=cat_name).first()
        q = Question(
            category_id=cat.id,
            prompt=prompt,
            option_a=a, option_b=b, option_c=c, option_d=d,
            correct_option=correct
        )
        db.session.add(q)

    # --- Python (10) ---
    add_q("Python", "What does `len([1,2,3])` return?", "2", "3", "4", "Error", "B")
    add_q("Python", "Which keyword creates a function?", "def", "func", "lambda", "function", "A")
    add_q("Python", "What is the output of `print(type(5))`?", "<class 'int'>", "<class 'str'>", "<int>", "int", "A")
    add_q("Python", "Which data type is immutable?", "list", "dict", "set", "tuple", "D")
    add_q("Python", "What does `break` do in a loop?", "skips iteration", "ends loop", "restarts loop", "does nothing", "B")
    add_q("Python", "What does `continue` do in a loop?", "ends loop", "skips to next iteration", "exits program", "pauses loop", "B")
    add_q("Python", "Which is a valid dictionary literal?", "{a:1}", "{'a':1}", "('a':1)", "['a':1]", "B")
    add_q("Python", "What does `range(3)` produce?", "1,2,3", "0,1,2", "0,1,2,3", "2,3,4", "B")
    add_q("Python", "What is `None` in Python?", "0", "empty string", "null value", "false", "C")
    add_q("Python", "Which operator is used for integer division?", "/", "//", "%", "**", "B")

    # --- SQL (10) ---
    add_q("SQL", "Which clause filters rows before grouping?", "HAVING", "WHERE", "ORDER BY", "GROUP BY", "B")
    add_q("SQL", "Which keyword sorts results?", "GROUP BY", "ORDER BY", "SORT", "FILTER", "B")
    add_q("SQL", "What does COUNT(*) do?", "counts non-null values", "counts rows", "counts columns", "counts distinct", "B")
    add_q("SQL", "Which join returns only matching rows?", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "FULL JOIN", "C")
    add_q("SQL", "Which is used to remove duplicates?", "DISTINCT", "UNIQUE", "REMOVE", "CLEAN", "A")
    add_q("SQL", "Which command changes table structure?", "UPDATE", "ALTER", "INSERT", "DELETE", "B")
    add_q("SQL", "Which function returns max value?", "MAX()", "TOP()", "HIGH()", "GREATEST()", "A")
    add_q("SQL", "What does `PRIMARY KEY` ensure?", "nullable", "uniqueness + not null", "only not null", "only uniqueness", "B")
    add_q("SQL", "Which clause filters groups?", "WHERE", "HAVING", "ORDER BY", "LIMIT", "B")
    add_q("SQL", "Which statement creates a table?", "NEW TABLE", "MAKE TABLE", "CREATE TABLE", "BUILD TABLE", "C")

    # --- HTML/CSS (10) ---
    add_q("HTML/CSS", "Which tag creates a hyperlink?", "<a>", "<p>", "<div>", "<link>", "A")
    add_q("HTML/CSS", "Which CSS property changes text color?", "font-color", "text-color", "color", "fgcolor", "C")
    add_q("HTML/CSS", "Which tag is for the largest heading?", "<h6>", "<h4>", "<h1>", "<head>", "C")
    add_q("HTML/CSS", "Which property controls spacing inside an element?", "margin", "padding", "border", "gap", "B")
    add_q("HTML/CSS", "Which property controls spacing outside an element?", "padding", "margin", "border", "outline", "B")
    add_q("HTML/CSS", "Which display makes items align in a row easily?", "block", "inline", "flex", "grid", "C")
    add_q("HTML/CSS", "Which selector targets an id?", ".idname", "#idname", "id(idname)", "*idname", "B")
    add_q("HTML/CSS", "Which tag is used for an image?", "<img>", "<image>", "<pic>", "<src>", "A")
    add_q("HTML/CSS", "Which HTML is correct for a checkbox?", "<input type='checkbox'>", "<checkbox>", "<check>", "<input checkbox>", "A")
    add_q("HTML/CSS", "Which CSS property changes font size?", "font-size", "text-size", "size", "font-weight", "A")

    db.session.commit()
    print("Seed completed: 3 categories, 30 questions.")

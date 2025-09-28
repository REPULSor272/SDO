from app.db.db import get_student_tasks

user_id = 2
user_labs = get_student_tasks(user_id)
print(list(user_labs))
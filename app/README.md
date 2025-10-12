# Postgres database methods

## База данных для сайта с проверкой лабораторных работ по программированию

Применение функций для доступа к БД можно посмотреть в файле test.py

Функции изменения БД:

 - delete_tables():
    Удаление всех сущностей

 - create_tables():
    Создание всех сущностей

 - add_user(username, password, role_type='student', study_group=None):
    Добавляет нового пользователя в базу данных.

 - add_subject(name):
    Добавляет новый предмет в базу данных.

 - reg_user_in_subject(user_id, subject_identifier):
    Зачисляет пользователя на дисциплину по ID пользователя и ID или имени дисциплины.

 - add_task(name, subject_identifier, description=None, max_symbols_count=None, max_strings_count=None, construction=None):
    Добавляет задачу к предмету. Идентификатором предмета может быть его ID или имя.

 - add_test_case(input_data, output_data, task_id):
    Добавляет новый тестовый случай для задачи в базу данных.

 - add_test_result(passed, test_case_id, solution_id):
    Добавляет результат теста для решения.

 - add_solution(code, user_id, task_id, mark=None, length_test_result=None, formula_test_result=None, auto_test_result=None):
    Добавляет решение в базу данных.

 - evaluate_solution(solution_id, new_mark):
    Оценка решения пользователя для заданного решения.
  

Функции запросов к БД:

 - get_user_subjects(user_id):
    Возвращает все дисциплины, на которые зачислен пользователь по ID пользователя.
    
 - get_solutions_by_user(user_id):
    Возвращает все решения, связанные с пользователем по его ID.

 - get_subjects():
    Возвращает все предметы из базы данных.

 - get_tasks_by_subject(subject_identifier):
    Возвращает все задачи, связанные с предметом по его ID или имени.

 - get_test_cases_by_task(task_id):
    Возвращает все тестовые случаи, связанные с задачей по её ID.

 - get_user_testCase_results_by_solution(user_id, solution_id):
    Возвращает результаты тестов пользователя для указанного решения.

 - get_user_solutions_by_task(user_id, task_id):
    Возвращает все решения пользователя для конкретной задачи по ID.
    
 - get_users_by_group(study_group):
    Возвращает всех пользователей, которые принадлежат указанной учебной группе.

 - get_users_by_subject(subject_id):
    Возвращает всех пользователей, зачисленных на предмет с заданным subject_id.

 - get_users():
    Возвращает всех пользователей из базы данных.

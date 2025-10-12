import contextlib
import io
import threading
import time
import re
from typing import List, Dict

from app.db.task_methods import get_test_cases_by_task, update_solution_status
from  app.schemas.tests import TestCase


class TeacherList:
    variables = dict()
    input_variables = []
    formulas_teacher = dict()
    formulas_student = dict()
    check = []
    operations_in_math = ['+', '-', '/', '*', '=']

    def __int__(self, variables, formulas):
        self.variables = variables
        self.formulas = formulas

    def binding_variables(self, a, b):  # a - student variable, b - teacher variable
        buff = dict()
        for i in range(0, len(self.variables)):
            if b == list(self.variables.items())[i][1]:
                buff[a] = b
            else:
                buff[list(self.variables.items())[i][0]] = list(self.variables.items())[i][1]
        self.variables = buff

    def binding_formulas(self, a, b):  # a - student formula, b - teacher formula
        for i in range(0, len(self.formulas_teacher)):
            if b == list(self.formulas_teacher.items())[i][1]:
                self.formulas_student[i] = a

    def add_variable(self, a):
        flag = False
        for i in range(0, len(self.variables)):
            if a == self.variables[i]:
                flag = True
        if not flag:
            self.variables[len(self.variables)] = a

    def add_teacher_formula(self, a):
        buff = []
        for char1 in a:
            for char2 in self.operations_in_math:
                if char1 == char2:
                    buff.append(a[:a.find(char2)])
                    self.add_variable(a[:a.find(char2)])
                    buff.append(char2)
                    a = a[a.find(char2) + 1:]
        buff.append(a)
        self.add_variable(a)
        self.formulas_teacher[len(self.formulas_teacher)] = buff
        self.check.append(False)

    def normalize_formula(self, formula: str) -> str:
        var_regex = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
        normalized = formula
        var_map: Dict[str, str] = {}
        var_count = 0

        for match in var_regex.finditer(formula):
            match_str = match.group()
            if match_str not in var_map:
                var_map[match_str] = f"VAR{var_count}"
                var_count += 1

        for original, replacement in var_map.items():
            normalized = re.sub(r'\b' + original + r'\b', replacement, normalized)

        normalized = normalized.replace(' ', '')
        if normalized.endswith(';'):
            normalized = normalized[:-1]

        return normalized

    def extract_expressions(self, line: str) -> List[str]:
        expr_regex = re.compile(r'([\w\s\+\-\*/\^\=()]+)')
        expressions = []

        for match in expr_regex.finditer(line):
            expr = match.group(1).strip()
            if any(op in expr for op in '+-*/=^'):
                expressions.append(expr)

        return expressions

    def add_student_formula(self, line):
        normalized_input = self.normalize_formula("".join(self.formulas_teacher[0]))
        found = False

        line = line.rstrip('\n')
        if line.endswith(';'):
            line = line[:-1]

        for i in self.formulas_teacher:
            expressions = self.extract_expressions(line)
            for expr in expressions:
                normalized_line = self.normalize_formula(expr)
                if normalized_input == normalized_line:
                    found = True
                    break

                if found:
                    break

            if found:
                self.binding_variables(line, self.formulas_teacher[i])
                self.binding_formulas(line, self.formulas_teacher[i])

async def check_formulas(teacher_formula_str, input_variables_str, code_str) -> tuple[str, bool]:
    teacher_list = TeacherList()
    for line in teacher_formula_str.splitlines():
        line = line.rstrip()
        teacher_list.add_teacher_formula(line)

    for line in input_variables_str.splitlines():
        line = line.rstrip()
        teacher_list.input_variables.append(line)

    input_count = 0
    for line in code_str.splitlines():
        line = line.rstrip()
        if 'input()' in line:
            char = line[:line.find('=')].strip()
            teacher_list.binding_variables(char, teacher_list.input_variables[input_count])
            input_count += 1
        else:
            teacher_list.add_student_formula(line)

    res = ""
    all_formulas_correct = True
    for i in range(len(teacher_list.formulas_teacher)):
        if i in teacher_list.formulas_student:
            student_formula = "".join(teacher_list.formulas_student[i])
            teacher_formula = "".join(teacher_list.formulas_teacher[i])
            if student_formula != teacher_formula:
                all_formulas_correct = False
            res += student_formula + '\n'
        else:
            all_formulas_correct = False

    return res, all_formulas_correct


async def run_tests(task_id: int, code_str: str) -> dict:
    test_cases = get_test_cases_by_task(task_id)
    if not test_cases:
        return {
            "test_case_number": -1,
            "input_data": "No test cases found.",
            "user_output": "",
            "expected_output": "",
            "status": "Failed"
        }

    total_execution_time = 0
    code_length = sum(1 for line in code_str.split('\n') if line.strip())

    for index, test_case in enumerate(test_cases):
        input_data = test_case.inp
        expected_output = test_case.out

        # Подготовка кода с входными данными
        code_with_input = f"import sys\ninput = lambda: '{input_data}'\n{code_str}"

        # Выполнение кода
        output = io.StringIO()
        start_time = time.time()
        execute_status = True

        def exec_code():
            try:
                with contextlib.redirect_stdout(output):
                    exec(code_with_input)
            except Exception as e:
                nonlocal execute_status
                execute_status = False
                output.write(f"Error executing code: {e}")

        thread = threading.Thread(target=exec_code)
        thread.start()
        thread.join(timeout=5)

        if thread.is_alive():
            output.write("Execution timed out.")
            thread.join()

        end_time = time.time()
        execution_time = round(end_time - start_time, 3)
        total_execution_time += execution_time
        result = output.getvalue()

        # Сравнение результата с ожидаемым выводом
        if result.strip() != expected_output.strip():
            return {
                "test_case_number": index + 1,
                "input_data": input_data,
                "user_output": result.strip(),
                "expected_output": expected_output.strip(),
                "status": "Failed"
            }

    return {
        "total_execution_time": round(total_execution_time, 3),
        "code_length": code_length,
        "execution_status": "Success",
        "status": "Success"
    }


# main testing function
async def check_file(task_id: int, teacher_formula: str, input_variables: str, student_code: str,
                     solution_id: int) -> TestCase:
    # Проверка формул
    formulas_output, formulas_correct = await check_formulas(teacher_formula, input_variables, student_code)

    # Выполнение тестов
    test_result = await run_tests(task_id, student_code)

    if test_result.get("status") == "Failed":
        update_solution_status(solution_id, "Failed")
        return TestCase(
            formulas_output=formulas_output,
            code_output=f"Test case {test_result['test_case_number']} failed.\n"
                        f"Input: {test_result['input_data']}\n"
                        f"Expected output: {test_result['expected_output']}\n"
                        f"User output: {test_result['user_output']}",
            execution_time=0.0,
            code_length=0,
            execution_status=test_result["status"]
        )

    update_solution_status(solution_id, "Success")
    return TestCase(
        formulas_output=formulas_output,
        code_output="All tests passed successfully.",
        execution_time=test_result['total_execution_time'],
        code_length=test_result['code_length'],
        execution_status=test_result["status"]
    )

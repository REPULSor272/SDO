import contextlib
import io
import threading
import time
import re
import json
import requests
from enum import IntEnum
from typing import List, Dict
from app.db.task_methods import get_test_cases_by_task, update_solution_status
from  app.schemas.tests import TestCase



class SubjectTypes(IntEnum):
    Python = 1
    CSharp = 4

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

async def run_c_sharp_tests(task_id: int, code_str: str, cfg: dict) -> dict: 
    cs_service_cfg = cfg.get('cs_service')
    
    test_cases = get_test_cases_by_task(task_id)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
   

    start_time = time.time()
    
    for index, test_case in enumerate(test_cases):
        data = {
            "StringCode": code_str,
            "Test": {
                "Input":test_case.inp,
                "ExpectedOutput": test_case.out
            }
        }
        response = requests.post(
            f'http://{cs_service_cfg.get('host')}:{str(cs_service_cfg.get('port'))}/CDiazCodeLab/CodeCheck/RunTestsFromString',
            data=json.dumps(data),
            headers=headers 
        )

        response_data = response.json()
        result_data = response_data.get('result')
        
        if not(result_data.get('passed')):
            return {
                "test_case_number": index + 1,
                "input_data": result_data.get('testCase').get('input'),
                "user_output": result_data.get('actualOutput'),
                "expected_output": result_data.get('testCase').get('expeexpectedOutput'),
                "status": "Failed"
            }
        index += 1
    
    end_time = time.time()
    execution_time = round(end_time - start_time, 3)

    return {
        "total_execution_time": round(execution_time, 3),
        "code_length": response_data.get('lineCount'),
        "execution_status": "Success",
        "status": "Success"
    }

# main testing function
async def check_file(task_id: int, subject_id: int, teacher_formula: str, input_variables: str, student_code: str,
                     solution_id: int, cfg: dict) -> TestCase:

    match subject_id:
        case SubjectTypes.Python.value:
            # Выполнение тестов
            test_result = await run_tests(task_id, student_code)
        case SubjectTypes.CSharp.value:
            # Выполнение тестов на C#
            test_result = await run_c_sharp_tests(task_id, student_code, cfg)

    if test_result.get("status") == "Failed":
        update_solution_status(solution_id, "Failed")
        return TestCase(
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
        code_output="All tests passed successfully.",
        execution_time=test_result['total_execution_time'],
        code_length=test_result['code_length'],
        execution_status=test_result["status"]
    )

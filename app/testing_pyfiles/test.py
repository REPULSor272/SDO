import contextlib
import io
import threading
import time
import re
from typing import List, Dict

from app.db.task_methods import get_test_cases_by_task, update_solution_status
from  app.schemas.tests import TestCase

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
async def check_file(task_id: int, student_code: str, solution_id: int) -> TestCase:
    # Выполнение тестов
    test_result = await run_tests(task_id, student_code)

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

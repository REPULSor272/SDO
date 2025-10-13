﻿using System.Drawing;
using CDiazCodeLab.Models;

namespace CDiazCodeLab.Services
{
    public class CodeCheckService
    {
        private readonly RoslynCodeRunner _runner;

        public CodeCheckService(RoslynCodeRunner runner)
        {
            _runner = runner;
        }

        /// <summary>
        /// Выполняет все тесты из переданной строки для данного кода.
        /// </summary>
        public async Task<CodeCheckResult?> RunTestsFromStringAsync(string path, string testCasesString)
        {

            // Читаем код как текст
            string code = await File.ReadAllTextAsync(path);
            var file = GetFileInfo(path, code);

            var testCases = TestCaseLoader.LoadFromString(testCasesString).ToList();

            if (!testCases.Any())
                return null;

            var results = new List<TestResult>();
            int passed = 0;

            foreach (var test in testCases)
            {
                var result = await _runner.RunAsync(code, test);
                results.Add(result);
                if (result.Passed) passed++;
            }

            return new CodeCheckResult
            {
                FileName = file.FileName,
                FileSizeBytes = file.Size,
                LineCount = file.LineCount,
                Total = testCases.Count,
                Passed = passed,
                Failed = testCases.Count - passed,
                Results = results
            };
        }
        static FileInfoModel GetFileInfo(string file, string code)
        {
            try
            {
                // Получаем информацию о файле
                FileInfo info = new FileInfo(file);
                long fileSize = info.Length; // размер в байтах

                // Разделяем на строки
                string[] allLines = code.Split(new[] { "\r\n", "\n", "\r" }, StringSplitOptions.None);

                // Подсчёт строк кода
                int totalLines = allLines.Length;
                int codeLines = allLines.Count(IsCodeLine);

                var File = new FileInfoModel();
                File.FileName = Path.GetFileName(file);
                File.Size = fileSize;
                File.LineCount = codeLines;
                return File;
            }
            catch (Exception ex)
            {
                var File = new FileInfoModel();
                File.Exception = ex.Message;
                return File;
            }
        }
        // Проверка строки на {, [, (, комментарии и пустые строки  
        static bool IsCodeLine(string line)
        {
            string trimmed = line.Trim();

            // Пустая строка
            if (string.IsNullOrWhiteSpace(trimmed))
                return false;

            // Только фигурные скобки
            if (trimmed == "{" || trimmed == "}" || trimmed == "("
            || trimmed == ")" || trimmed == "[" || trimmed == "]")
                return false;

            // Однострочный комментарий //
            if (trimmed.StartsWith("//"))
                return false;

            // Многострочный комментарий /* ... */
            if (trimmed.StartsWith("/*") || trimmed.StartsWith("*") || trimmed.EndsWith("*/"))
                return false;

            // Если ничего из выше перечисленного — считаем кодом
            return true;
        }
    }
}

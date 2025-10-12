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
        public async Task<CodeCheckResult?> RunTestsFromStringAsync(string code, string testCasesString)
        {
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
                Total = testCases.Count,
                Passed = passed,
                Failed = testCases.Count - passed,
                Results = results
            };
        }
    }
}

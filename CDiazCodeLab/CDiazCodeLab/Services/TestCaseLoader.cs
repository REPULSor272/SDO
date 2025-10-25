using CDiazCodeLab.Models;

namespace CDiazCodeLab.Services
{
    public static class TestCaseLoader
    {
        /// <summary>
        /// Загружает коллекцию тестов из текстовой строки.
        /// </summary>
        /// <remarks>
        /// Каждая строка должна содержать входные данные и ожидаемый результат, 
        /// разделённые символом <c>|</c>.  
        /// Пример строки: <c>2 3|5</c> означает, что входные данные — «2 3», а ожидаемый результат — «5».  
        /// Пустые строки и некорректные записи игнорируются.
        /// </remarks>
        /// <param name="text">
        /// Исходная строка, содержащая список тестов (по одному на строку).
        /// </param>
        /// <returns>
        /// Перечисление объектов <see cref="TestCase"/>, содержащих входные данные и ожидаемые результаты.
        /// </returns>
        public static IEnumerable<TestCase> LoadFromString(string text)
        {
            var lines = text.Split("\n", StringSplitOptions.RemoveEmptyEntries);
            foreach (var line in lines)
            {
                var parts = line.Trim().Split("|", StringSplitOptions.RemoveEmptyEntries);
                if (parts.Length < 2) continue;

                yield return new TestCase
                {
                    Input = parts[0].Trim(),
                    ExpectedOutput = parts[1].Trim()
                };
            }
        }
    }
}

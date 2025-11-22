using CDiazCodeLab.Models;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using System.Diagnostics;
using System.Reflection;

namespace CDiazCodeLab.Services
{
    /// <summary>
    /// Сервис для компиляции и выполнения пользовательского C# кода
    /// с помощью Roslyn, а также проверки результатов выполнения по тестам.
    /// </summary>
    public class RoslynCodeRunner
    {
        /// <summary>
        /// Асинхронно выполняет тест для данного кода и возвращает результат проверки.
        /// </summary>
        /// <param name="code">Исходный код на C# для выполнения.</param>
        /// <param name="test">Тестовый случай с входными и ожидаемыми данными.</param>
        /// <param name="timeoutMs">Таймаут выполнения кода (мс).</param>
        /// <returns>Результат теста <see cref="TestResult"/>.</returns>
        public async Task<TestResult> RunAsync(string code, TestCase test, int timeoutMs = 5000)
        {
            var result = new TestResult { TestCase = test };
            var outputWriter = new StringWriter();
            var inputReader = new StringReader(test.Input + Environment.NewLine);
            int countVariables;
            var prevOut = Console.Out;
            var prevIn = Console.In;

            using var cts = new CancellationTokenSource(timeoutMs);
            Console.SetOut(outputWriter);
            Console.SetIn(inputReader);

            try
            {
                var assembly = CompileCode(code, out countVariables);
                var sw = Stopwatch.StartNew();
                long memBefore = GC.GetTotalMemory(false);

                await ExecuteEntryPointAsync(assembly, cts.Token);

                sw.Stop();
                long memAfter = GC.GetTotalMemory(false);

                var actualOutput = NormalizeOutput(outputWriter.ToString());

                result.ExecutionTimeMs = sw.ElapsedMilliseconds;
                result.MemoryUsedBytes = memAfter - memBefore;
                result.CountVariables = countVariables;
                if (test.CountVariables != null)
                {
                    if (result.CountVariables > test.CountVariables)
                    {
                        result.ErrorMessage = $"Превышено число переменных: {result.CountVariables}";
                        result.Passed = false;
                    }
                }

                if (test.MaxExecutionTimeMs != null)
                {
                    if (result.ExecutionTimeMs > test.MaxExecutionTimeMs)
                    {
                        result.ErrorMessage = $"Превышено время: {result.ExecutionTimeMs} ms";
                        result.Passed = false;
                    }
                }

                if (test.MaxMemoryBytes != null)
                {
                    if (result.MemoryUsedBytes > test.MaxMemoryBytes)
                    {
                        result.ErrorMessage = $"Превышена память: {result.MemoryUsedBytes} bytes";
                        result.Passed = false;
                    }
                }

                if (result.Passed)
                {
                    result.Passed = CompareOutputs(actualOutput, test.ExpectedOutput);
                }
                result.ActualOutput = actualOutput;

            }
            catch (OperationCanceledException)
            {
                result.ErrorMessage = "Превышено время выполнения (timeout).";
            }
            catch (Exception ex)
            {
                result.ErrorMessage = ex.Message;
            }
            finally
            {
                Console.SetOut(prevOut);
                Console.SetIn(prevIn);
            }

            return result;
        }

        /// <summary>
        /// Компилирует исходный код в сборку.
        /// </summary>
        private static Assembly CompileCode(string code, out int varCount)
        {
            var syntaxTree = CSharpSyntaxTree.ParseText(code);
            var references = GetDefaultReferences().ToArray();

            var root = syntaxTree.GetRoot();
            varCount = root.DescendantNodes().OfType<VariableDeclaratorSyntax>().Count();

            var compilation = CSharpCompilation.Create(
                assemblyName: "UserCode",
                syntaxTrees: new[] { syntaxTree },
                references: references,
                options: new CSharpCompilationOptions(OutputKind.ConsoleApplication)
            );

            using var ms = new MemoryStream();
            var emitResult = compilation.Emit(ms);

            if (!emitResult.Success)
                throw new Exception(string.Join(
                    "\n",
                    emitResult.Diagnostics.Where(d => d.Severity == DiagnosticSeverity.Error)
                ));

            ms.Seek(0, SeekOrigin.Begin);
            return Assembly.Load(ms.ToArray());
        }

        /// <summary>
        /// Выполняет точку входа с учётом таймаута.
        /// </summary>
        private static async Task ExecuteEntryPointAsync(Assembly assembly, CancellationToken token)
        {
            var entry = assembly.EntryPoint
                ?? throw new Exception("Не найдена точка входа Main.");

            await Task.Run(() =>
                entry.Invoke(null, entry.GetParameters().Length == 0
                    ? null
                    : new object[] { Array.Empty<string>() }),
                token);
        }

        /// <summary>
        /// Упрощает и нормализует вывод программы.
        /// </summary>
        private static string NormalizeOutput(string output)
        {
            return output.Replace("\r", "").Replace("\n", " ").Trim();
        }

        /// <summary>
        /// Сравнивает вывод программы с ожидаемым результатом.
        /// </summary>
        private static bool CompareOutputs(string actual, string expected)
        {
            var actualParts = actual.Split(' ', StringSplitOptions.RemoveEmptyEntries);
            var expectedParts = expected.Split(' ', StringSplitOptions.RemoveEmptyEntries);
            return actualParts.SequenceEqual(expectedParts);
        }

        /// <summary>
        /// Возвращает список стандартных ссылок на сборки.
        /// </summary>
        private static IEnumerable<MetadataReference> GetDefaultReferences()
        {
            var assemblies = AppDomain.CurrentDomain.GetAssemblies()
                .Where(a => !a.IsDynamic && !string.IsNullOrEmpty(a.Location))
                .Select(a => a.Location)
                .Distinct();

            foreach (var path in assemblies)
                yield return MetadataReference.CreateFromFile(path);
        }
    }
}

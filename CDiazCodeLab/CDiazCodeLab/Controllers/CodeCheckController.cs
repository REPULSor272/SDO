using CDiazCodeLab.DTOs;
using CDiazCodeLab.Services;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.IO;
using System.Threading.Tasks;

namespace CDiazCodeLab.Controllers
{
    [ApiController]
    [Route("CDiazCodeLab/[controller]/[action]")]
    public class CodeCheckController : ControllerBase
    {
        private readonly CodeCheckService _codeCheck;

        public CodeCheckController(CodeCheckService codeCheck)
        {
            _codeCheck = codeCheck;
        }

        // Старый вариант, если код передаётся в теле запроса (например, JSON)
        [HttpPost]
        public async Task<IActionResult> RunTests([FromBody] CodeCheckFileDTO request)
        {
            var result = await _codeCheck.RunTestsFromStringAsync(request.Code, request.Tests);

            if (result == null)
                return BadRequest("No result or incorrect test execution.");

            return Ok(result);
        }

        // Новый вариант — приём файла через Swagger
        [HttpPost]
        public async Task<IActionResult> RunTestsFromFile(IFormFile file, [FromQuery] string tests)
        {
            Console.Write(tests);
            if (file == null || file.Length == 0)
                return BadRequest("No file uploaded.");

            // Сохраняем временно файл (если нужно)
            var tempPath = Path.Combine(Path.GetTempPath(), file.FileName);
            using (var stream = new FileStream(tempPath, FileMode.Create))
            {
                await file.CopyToAsync(stream);
            }

            // Исправляем формат тестов
            if (!string.IsNullOrEmpty(tests))
            {
                // Если тесты переданы с экранированными переносами строк (например, "\n"),
                // заменим их на реальные переводы строк, чтобы Split('\n') сработал корректно
                tests = tests
                    .Replace("\\r\\n", "\n")
                    .Replace("\\n", "\n")
                    .Replace("\\r", "\n"); 
            }

            // Передаём в сервис для проверки
            var result = await _codeCheck.RunTestsFromStringAsync(tempPath, tests);

            // Можно удалить временный файл
            System.IO.File.Delete(tempPath);

            if (result == null)
                return BadRequest("Code check failed or returned no result.");

            // Возвращаем результат в JSON
            return Ok(result);
        }
    }
}

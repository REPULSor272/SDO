using CDiazCodeLab.DTOs;
using CDiazCodeLab.Models;
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

        // Если код передаётся в теле запроса (например, JSON)
        [HttpPost]
        public async Task<IActionResult> RunTestsFromString([FromForm] CodeCheckTextDTO request)
        {
            var result = await _codeCheck.RunTestsFromStringAsync(request.StringCode, request.Test, "text");

            if (result == null)
                return BadRequest("No result or incorrect test execution.");

            return Ok(result);
        }

        // Новый вариант — приём файла через Swagger
        [HttpPost]
        public async Task<IActionResult> RunTestsFromFile([FromForm] CodeCheckFileDTO testCase)
        {
            Console.Write(testCase);
            if (testCase.File == null || testCase.File.Length == 0)
                return BadRequest("No file uploaded.");

            // Сохраняем временно файл (если нужно)
            var tempPath = Path.Combine(Path.GetTempPath(), testCase.File.FileName);
            using (var stream = new FileStream(tempPath, FileMode.Create))
            {
                await testCase.File.CopyToAsync(stream);
            }


            // Передаём в сервис для проверки
            var result = await _codeCheck.RunTestsFromStringAsync(tempPath, testCase.Test, "");

            // Можно удалить временный файл
            System.IO.File.Delete(tempPath);

            if (result == null)
                return BadRequest("Code check failed or returned no result.");

            // Возвращаем результат в JSON
            return Ok(result);
        }
    }
}

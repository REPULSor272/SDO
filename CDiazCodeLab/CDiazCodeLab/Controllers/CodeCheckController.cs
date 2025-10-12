using CDiazCodeLab.DTOs;
using CDiazCodeLab.Services;
using Microsoft.AspNetCore.Mvc;

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

        [HttpPost]
        public async Task<IActionResult> RunTests(CodeCheckFileDTO request)
        {
            var result = await _codeCheck.RunTestsFromStringAsync(request.Code, request.Tests);

            if (result == null)
                return BadRequest("Нет тестов или они некорректно заполнены.");

            return Ok(result);
        }
    }
}

using CDiazCodeLab.Models;

namespace CDiazCodeLab.DTOs
{
    public class CodeCheckFileDTO
    {
        public IFormFile File { get; set; } = null!;
        public TestCase Test { get; set; } = null!;
    }
}

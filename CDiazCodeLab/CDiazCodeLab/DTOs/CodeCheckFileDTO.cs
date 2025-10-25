using CDiazCodeLab.Models;

namespace CDiazCodeLab.DTOs
{
    public class CodeCheckFileDTO
    {
        public IFormFile File { get; set; }
        public TestCase Test { get; set; } = null!;
    }
}

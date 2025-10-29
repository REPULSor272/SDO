using CDiazCodeLab.Models;

namespace CDiazCodeLab.DTOs
{
    public class CodeCheckTextDTO
    {
        public string StringCode { get; set; } = null!;
        public TestCase Test { get; set; } = null!;
    }
}

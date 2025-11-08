namespace CDiazCodeLab.Models
{
    public class TestCase
    {
        public string Input { get; set; } = string.Empty;
        public string ExpectedOutput { get; set; } = string.Empty;

        public int MaxExecutionTimeMs { get; set; }
        public long MaxMemoryBytes { get; set; }
    }
}

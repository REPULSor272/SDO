namespace CDiazCodeLab.Models
{
    public class CodeCheckResult
    {
        public string? FileName { get; set; }
        public long FileSizeBytes { get; set; }
        public int LineCount { get; set; }
        public TestResult Result { get; set; } = new();
    }
}

namespace CDiazCodeLab.Models
{
    public class CodeCheckResult
    {
        public string? FileName { get; set; }
        public long FileSizeBytes { get; set; }
        public int LineCount { get; set; }
        public int Total { get; set; }
        public int Passed { get; set; }
        public int Failed { get; set; }
        public List<TestResult> Results { get; set; } = new();
    }
}

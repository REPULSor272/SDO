namespace CDiazCodeLab.Models
{
    public class CodeCheckResult
    {
        public int Total { get; set; }
        public int Passed { get; set; }
        public int Failed { get; set; }
        public List<TestResult> Results { get; set; } = new();
    }
}

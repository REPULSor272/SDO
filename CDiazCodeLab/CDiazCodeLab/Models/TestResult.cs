namespace CDiazCodeLab.Models
{
    public class TestResult
    {
        public TestCase TestCase { get; set; } = new();
        public string ActualOutput { get; set; } = string.Empty;
        public bool Passed { get; set; } = true;
        public string ErrorMessage { get; set; } = string.Empty;
        public long? ExecutionTimeMs { get; set; }
        public long? MemoryUsedBytes { get; set; }
        public int? CountVariables { get; set; }
    }

}

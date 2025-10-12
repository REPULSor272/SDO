namespace CDiazCodeLab.Models
{
    public class TestResult
    {
        public TestCase TestCase { get; set; } = new();
        public string ActualOutput { get; set; } = string.Empty;
        public bool Passed { get; set; }
        public string ErrorMessage { get; set; } = string.Empty;
    }

}

using System.Drawing;

namespace CDiazCodeLab.Models
{
    public class FileInfoModel
    {

        public string FileName { get; set; } = string.Empty;
        public long Size { get; set; } = 0;
        public int LineCount { get; set; } = 0;
        public string Exception { get; set; } = string.Empty;
    }
}
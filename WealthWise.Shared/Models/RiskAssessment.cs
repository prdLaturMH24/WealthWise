using System.Text.Json.Serialization;

namespace WealthWise.Shared.Models
{
    public class RiskAssessment
    {
        [JsonPropertyName("overall_risk_level")]
        public string OverallRiskLevel { get; set; } = string.Empty;

        [JsonPropertyName("risk_factors")]
        public List<string> RiskFactors { get; set; } = new();

        [JsonPropertyName("mitigation_strategies")]
        public List<string> MitigationStrategies { get; set; } = new();

        [JsonPropertyName("risk_tolerance_alignment")]
        public bool RiskToleranceAlignment { get; set; }

        [JsonPropertyName("stress_test_results")]
        public Dictionary<string, string>? StressTestResults { get; set; }
    }
}

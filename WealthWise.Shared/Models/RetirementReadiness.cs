using System.Text.Json.Serialization;

namespace WealthWise.Shared.Models
{
    public class RetirementReadiness
    {
        [JsonPropertyName("current_retirement_score")]
        public int CurrentRetirementScore { get; set; }

        [JsonPropertyName("target_retirement_age")]
        public int TargetRetirementAge { get; set; }

        [JsonPropertyName("projected_retirement_corpus")]
        public decimal ProjectedRetirementCorpus { get; set; }

        [JsonPropertyName("monthly_retirement_income")]
        public decimal MonthlyRetirementIncome { get; set; }

        [JsonPropertyName("gap_analysis")]
        public string? GapAnalysis { get; set; }

        [JsonPropertyName("recommendations")]
        public List<string> Recommendations { get; set; } = new();
    }
}

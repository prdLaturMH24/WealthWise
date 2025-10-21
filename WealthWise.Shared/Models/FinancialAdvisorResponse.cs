using System.Text.Json.Serialization;

namespace WealthWise.Shared.Models
{
    public class FinancialAdvisorResponse
    {
        [JsonPropertyName("request_id")]
        public string? RequestId { get; set; }

        [JsonPropertyName("success")]
        public bool Success { get; set; }

        [JsonPropertyName("timestamp")]
        public DateTime Timestamp { get; set; }

        [JsonPropertyName("processing_time_ms")]
        public decimal ProcessingTimeMs { get; set; }

        [JsonPropertyName("model_used")]
        public string? ModelUsed { get; set; }

        [JsonPropertyName("advice_summary")]
        public string AdviceSummary { get; set; } = string.Empty;

        [JsonPropertyName("detailed_analysis")]
        public string DetailedAnalysis { get; set; } = string.Empty;

        [JsonPropertyName("action_items")]
        public List<ActionItem> ActionItems { get; set; } = new();

        [JsonPropertyName("risk_assessment")]
        public RiskAssessment RiskAssessment { get; set; } = new();

        [JsonPropertyName("portfolio_analysis")]
        public PortfolioAnalysis? PortfolioAnalysis { get; set; }

        [JsonPropertyName("confidence_level")]
        public string ConfidenceLevel { get; set; } = string.Empty;

        [JsonPropertyName("follow_up_timeline")]
        public string FollowUpTimeline { get; set; } = string.Empty;

        [JsonPropertyName("additional_resources")]
        public List<string> AdditionalResources { get; set; } = new();

        [JsonPropertyName("projected_net_worth")]
        public Dictionary<string, decimal>? ProjectedNetWorth { get; set; }

        [JsonPropertyName("savings_projections")]
        public Dictionary<string, decimal>? SavingsProjections { get; set; }

        [JsonPropertyName("retirement_readiness")]
        public RetirementReadiness? RetirementReadiness { get; set; }
    }
}

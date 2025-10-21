using System.Text.Json.Serialization;

namespace WealthWise.Shared.Models
{
    public class PortfolioAnalysis
    {
        [JsonPropertyName("current_allocation")]
        public Dictionary<string, decimal> CurrentAllocation { get; set; } = new();

        [JsonPropertyName("recommended_allocation")]
        public Dictionary<string, decimal> RecommendedAllocation { get; set; } = new();

        [JsonPropertyName("diversification_score")]
        public int DiversificationScore { get; set; }

        [JsonPropertyName("performance_metrics")]
        public Dictionary<string, decimal> PerformanceMetrics { get; set; } = new();

        [JsonPropertyName("rebalancing_needed")]
        public bool RebalancingNeeded { get; set; }

        [JsonPropertyName("underperforming_assets")]
        public List<string> UnderperformingAssets { get; set; } = new();

        [JsonPropertyName("optimization_opportunities")]
        public List<string> OptimizationOpportunities { get; set; } = new();
    }
}

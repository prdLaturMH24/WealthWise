using System.Text.Json.Serialization;

namespace WealthWise.Shared.Models
{
    public class ActionItem
    {
        [JsonPropertyName("title")]
        public string Title { get; set; } = string.Empty;

        [JsonPropertyName("description")]
        public string Description { get; set; } = string.Empty;

        [JsonPropertyName("priority")]
        [JsonConverter(typeof(JsonStringEnumConverter))]
        public ActionPriority Priority { get; set; }

        [JsonPropertyName("category")]
        public string Category { get; set; } = string.Empty;

        [JsonPropertyName("timeline")]
        public string Timeline { get; set; } = string.Empty;

        [JsonPropertyName("estimated_impact")]
        public string? EstimatedImpact { get; set; }

        [JsonPropertyName("resources_needed")]
        public List<string> ResourcesNeeded { get; set; } = new();

        [JsonPropertyName("success_metrics")]
        public List<string> SuccessMetrics { get; set; } = new();
    }
}

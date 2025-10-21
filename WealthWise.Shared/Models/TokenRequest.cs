using System.Text.Json.Serialization;

namespace WealthWise.Shared.Models
{
    public class TokenRequest
    {
        [JsonPropertyName("username")]
        public string UserName { get; set; } = "demo_user_123";
        [JsonPropertyName("password")]
        public string Password { get; set; } = "demo";
    }
}

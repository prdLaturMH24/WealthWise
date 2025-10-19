using System.Net.Http.Json;

namespace WealthWise.UI.Services;

/// <summary>
/// Client-side AI chat service for the Blazor WebAssembly app.
/// Posts the user's message to the API endpoint and returns the response string.
/// </summary>
public class AiChatService
{
    private readonly HttpClient _http;

    public AiChatService(HttpClient http)
    {
        _http = http;
    }

    public async Task<string> GetAIReply(string userMessage)
    {
        var request = new { message = userMessage };
        var response = await _http.PostAsJsonAsync("api/ai/chat", request);
        response.EnsureSuccessStatusCode();

        var result = await response.Content.ReadAsStringAsync();
        return result;
    }
}
using System.Net.Http.Json;
namespace WealthWise.API.Services;
using System.Net.Http.Json;

public class AiChatService
{
    private readonly HttpClient _http;

    public AiChatService(HttpClient http)
    {
        _http = http;
    }

    public async Task<string> GetAIReply(string userMessage)
    {
        // 👇 For testing: simulate AI response
        // return await Task.FromResult($"You said: {userMessage}");

        // ✅ If you have a backend API (e.g., /api/ai/chat):
        var request = new { message = userMessage };
        var response = await _http.PostAsJsonAsync("https://your-backend/api/ai/chat", request);
        response.EnsureSuccessStatusCode();

        var result = await response.Content.ReadAsStringAsync();
        return result;
    }
}

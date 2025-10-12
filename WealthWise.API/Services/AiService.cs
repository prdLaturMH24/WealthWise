using Newtonsoft.Json;
using System.Text;
using WealthWise.Shared.Models;
namespace WealthWise.API.Services
{
    public class AiService
    {
        private readonly HttpClient _httpClient; 
        private readonly ILogger<AiService> _logger;
        public AiService(HttpClient httpClient, ILogger<AiService> logger)
        {
            _httpClient = httpClient ?? throw new ArgumentNullException(nameof(httpClient));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }

        /// <summary>
        /// Sends the user profile to the AI service and returns generated financial advice.
        /// </summary>
        /// <param name="userProfile">User profile payload.</param>
        /// <param name="cancellationToken">Cancellation token.</param>
        /// <returns>FinancialAdvice or null if not returned by the service.</returns>
        public async Task<FinancialAdvice?> GenerateAdviceAsync(UserProfile userProfile, CancellationToken cancellationToken = default)
        {
            ArgumentNullException.ThrowIfNull(userProfile);

            try
            {
                // Ensure we have a configured base address from DI. Combine base address with relative path to form an absolute URI.
                if (_httpClient.BaseAddress is null)
                {
                    _logger.LogError("AI HttpClient.BaseAddress is not configured. Set the AI_SERVICE_URL environment variable or configure the client in Program.cs.");
                    throw new InvalidOperationException("AI service base address is not configured. Set AI_SERVICE_URL environment variable or configure HttpClient in DI.");
                }

                var requestUri = new Uri(_httpClient.BaseAddress, "generate-advice");
                var requestPayload = new StringContent(JsonConvert.SerializeObject(userProfile), Encoding.UTF8, "application/json");
                var response = await _httpClient.PostAsync(requestUri, requestPayload, cancellationToken);
                var responsePayload = await response.Content.ReadAsStringAsync(cancellationToken);
                if (!response.IsSuccessStatusCode)
                {
                    var status = (int)response.StatusCode;
                    _logger.LogWarning("AI service returned non-success status {Status}. Response content: {Content}", status, JsonConvert.SerializeObject(responsePayload));
                    throw new HttpRequestException($"AI service returned status {status}.");
                }

                var advice = JsonConvert.DeserializeObject<FinancialAdvice>(responsePayload);
                if (advice is null)
                {
                    _logger.LogWarning("AI service returned an empty payload for GenerateAdviceAsync.");
                }

                return advice;
            }
            catch (OperationCanceledException)
            {
                _logger.LogInformation("GenerateAdviceAsync was canceled.");
                throw;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error calling AI service to generate advice.");
                throw;
            }
        }
    }
}


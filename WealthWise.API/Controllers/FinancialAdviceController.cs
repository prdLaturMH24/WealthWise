using Microsoft.AspNetCore.Mvc;
using WealthWise.API.Services;
using WealthWise.Shared.Models;

namespace WealthWise.API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class FinancialAdviceController : ControllerBase
{
    private readonly AiService _aiService;
    private readonly ILogger<FinancialAdviceController> _logger;

    public FinancialAdviceController(
        AiService aiService,
        ILogger<FinancialAdviceController> logger)
    {
        _aiService = aiService;
        _logger = logger;
    }

    [HttpPost("generate")]
    public async Task<ActionResult<FinancialAdvice>> GenerateAdvice(UserProfile userProfile)
    {
        try
        {
            if (userProfile is null) return BadRequest("Request Payload is Invalid.");
            var user = new UserProfile(
                userProfile.Name,
                userProfile.Email,
                userProfile.Age,
                userProfile.MonthlyIncome,
                userProfile.MonthlySavings,
                userProfile.RiskToleranceLevel,
                userProfile.CurrentInvestments,
                userProfile.FinancialGoals
                );
            
            var advice = await _aiService.GenerateAdviceAsync(userProfile);
            return Ok(advice);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating financial advice");
            return StatusCode(500, "Error generating financial advice");
        }
    }
}
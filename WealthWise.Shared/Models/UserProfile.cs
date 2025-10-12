using System.ComponentModel.DataAnnotations;

namespace WealthWise.Shared.Models;

public class UserProfile
{
    public UserProfile(string name, string email, int age, decimal monthlyIncome, decimal monthlySavings, RiskToleranceLevel riskToleranceLevel, List<Investment> currentInvestments, List<FinancialGoal> financialGoals)
    {
        Name = name;
        Email = email;
        Age = age;
        MonthlyIncome = monthlyIncome;
        MonthlySavings = monthlySavings;
        RiskTolerance = riskToleranceLevel.ToString();
        CurrentInvestments = currentInvestments ?? [];
        FinancialGoals = financialGoals ?? [];
    }

    public Guid Id { get; set; }
    [Required]
    public string Name { get; set; } = string.Empty;
    [Required]
    [EmailAddress]
    public string Email { get; set; } = string.Empty;

    [Required]
    [Range(18, 100)]
    public int Age { get; set; }
    public decimal MonthlyIncome { get; set; }
    public decimal MonthlySavings { get; set; }
    public RiskToleranceLevel RiskToleranceLevel { get; set; }
    public string RiskTolerance { get; set; } = string.Empty;
    public List<Investment> CurrentInvestments { get; set; } = new();
    public List<FinancialGoal> FinancialGoals { get; set; } = new();

    public UserProfile() { }
}

public enum RiskToleranceLevel
{
    Conservative,
    Moderate,
    Aggressive
}
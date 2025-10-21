using System.Text.Json.Serialization;

namespace WealthWise.Shared.Models
{
    public class FinancialAdvisorRequest
    {
        [JsonPropertyName("user_id")]
        public string UserId { get; set; } = string.Empty;

        [JsonPropertyName("age")]
        public int Age { get; set; }

        [JsonPropertyName("employment_status")]
        [JsonConverter(typeof(JsonStringEnumConverter))]
        public EmploymentStatus EmploymentStatus { get; set; }

        [JsonPropertyName("annual_income")]
        public decimal AnnualIncome { get; set; }

        [JsonPropertyName("monthly_expenses")]
        public decimal MonthlyExpenses { get; set; }

        [JsonPropertyName("current_savings")]
        public decimal CurrentSavings { get; set; }

        [JsonPropertyName("monthly_savings_capacity")]
        public decimal MonthlySavingsCapacity { get; set; }

        [JsonPropertyName("risk_tolerance")]
        [JsonConverter(typeof(JsonStringEnumConverter))]
        public RiskToleranceLevel RiskTolerance { get; set; }

        [JsonPropertyName("location")]
        public string? Location { get; set; }

        [JsonPropertyName("current_investments")]
        public decimal CurrentInvestments { get; set; }

        [JsonPropertyName("total_debt")]
        public decimal TotalDebt { get; set; }

        [JsonPropertyName("monthly_debt_payments")]
        public decimal MonthlyDebtPayments { get; set; }

        [JsonPropertyName("investment_experience")]
        public int InvestmentExperience { get; set; }

        [JsonPropertyName("short_term_horizon")]
        public int? ShortTermHorizon { get; set; }

        [JsonPropertyName("medium_term_horizon")]
        public int? MediumTermHorizon { get; set; }

        [JsonPropertyName("long_term_horizon")]
        public int? LongTermHorizon { get; set; }

        [JsonPropertyName("family_dependents")]
        public int FamilyDependents { get; set; }

        [JsonPropertyName("has_emergency_fund")]
        public bool HasEmergencyFund { get; set; }

        [JsonPropertyName("retirement_contributions")]
        public decimal RetirementContributions { get; set; }

        [JsonPropertyName("esg_preference")]
        public bool EsgPreference { get; set; }

        [JsonPropertyName("crypto_tolerance")]
        public bool CryptoTolerance { get; set; }
    }
}

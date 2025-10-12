namespace WealthWise.Shared.Models;

public class FinancialAdvice
{
    public Guid Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public AdviceCategory Category { get; set; }
    public decimal? ProjectedImpact { get; set; }
    public List<string> ActionItems { get; set; } = new();
    public DateTime GeneratedDate { get; set; }
}

public enum AdviceCategory
{
    Savings,
    Investment,
    Budgeting,
    DebtManagement,
    RetirementPlanning,
    TaxOptimization
}
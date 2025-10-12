namespace WealthWise.Shared.Models;

public class FinancialGoal
{
    public Guid Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public decimal TargetAmount { get; set; }
    public DateTime TargetDate { get; set; }
    public GoalPriority Priority { get; set; }
    public GoalStatus Status { get; set; }
}

public enum GoalPriority
{
    Low,
    Medium,
    High
}

public enum GoalStatus
{
    NotStarted,
    InProgress,
    Completed
}
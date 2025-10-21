namespace WealthWise.Shared.Models;

public class Investment
{
    public Guid Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public InvestmentType Type { get; set; }
    public decimal Amount { get; set; }
    public DateTime PurchaseDate { get; set; }
    public decimal CurrentValue { get; set; }
}

public enum InvestmentType
{
    Stocks,
    Bonds,
    MutualFunds,
    RealEstate,
    Cryptocurrency,
    BankDeposits,
    Other
}
using Microsoft.EntityFrameworkCore;
using WealthWise.Shared.Models;

namespace WealthWise.API.Data;

public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options)
    {
    }

    public DbSet<UserProfile> UserProfiles { get; set; }
    public DbSet<FinancialAdvice> FinancialAdvices { get; set; }
}

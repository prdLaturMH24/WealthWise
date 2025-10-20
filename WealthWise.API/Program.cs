using Microsoft.EntityFrameworkCore;
using WealthWise.API.Data;
using WealthWise.API.Services;

namespace WealthWise.API;

public class Program
{
    public static void Main(string[] args)
    {
        var builder = WebApplication.CreateBuilder(args);

        // Optional extension that configures defaults for services (keep as-is)
        builder.AddServiceDefaults();

        // Read environment variable early for HttpClient configuration
        var aiServiceUrl = Environment.GetEnvironmentVariable("AI_SERVICE_URL");

        // Configure EF Core
        var connectionString = builder.Configuration.GetConnectionString("DefaultConnection")
                               ?? "Server=(localdb)\\mssqllocaldb;Database=WealthWiseDb;Trusted_Connection=True;MultipleActiveResultSets=true";
        builder.Services.AddDbContext<ApplicationDbContext>(options =>
            options.UseSqlServer(connectionString));

        // Add services to the container.
        builder.Services.AddControllers();

        // Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
        builder.Services.AddEndpointsApiExplorer();
        builder.Services.AddSwaggerGen();

        // Add CORS for Blazor client
        builder.Services.AddCors(options =>
        {
            options.AddDefaultPolicy(policy =>
            {
                policy.AllowAnyOrigin()
                      .AllowAnyHeader()
                      .AllowAnyMethod();
            });
        });

        // Configure typed HttpClient for AiService (registers AiService for DI)
        // If running in Development and calling a local AI service with a self-signed certificate,
        // allow invalid certificates for this named client only. In Production the default handler is used.
        builder.Services.AddHttpClient<AiService>(client =>
        {
            if (!string.IsNullOrWhiteSpace(aiServiceUrl))
            {
                client.BaseAddress = new Uri(aiServiceUrl);
            }
            client.DefaultRequestHeaders.Add("Accept", "application/json");
        })
        .ConfigurePrimaryHttpMessageHandler(() =>
        {
            // In Development accept any server certificate to avoid SSL issues with self-signed certs.
            if (builder.Environment.IsDevelopment())
            {
                return new HttpClientHandler
                {
                    ServerCertificateCustomValidationCallback = HttpClientHandler.DangerousAcceptAnyServerCertificateValidator
                };
            }

            // In non-development environments use the default handler (strict validation).
            return new HttpClientHandler();
        });
        //Added chat service
        builder.Services.AddScoped<AiChatService>();

        // Do NOT add a separate AddScoped<AiService>() - the AddHttpClient above registers the typed client.

        var app = builder.Build();

        // Configure the HTTP request pipeline.
        if (app.Environment.IsDevelopment())
        {
            app.UseSwagger();
            app.UseSwaggerUI();
        }

        app.UseHttpsRedirection();

        // Use the named/default CORS policy registered earlier
        app.UseCors();

        app.UseAuthorization();

        // Map controllers after middleware configuration
        app.MapControllers();

        app.Run();
    }
}

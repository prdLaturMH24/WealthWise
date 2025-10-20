// Set defaults for required environment variables to allow AppHost to run in local/dev environments
// These can be overridden by actual environment variables in production or CI
Environment.SetEnvironmentVariable("ASPNETCORE_URLS", Environment.GetEnvironmentVariable("ASPNETCORE_URLS") ?? "http://localhost:5000");
Environment.SetEnvironmentVariable("ASPIRE_DASHBOARD_OTLP_HTTP_ENDPOINT_URL", Environment.GetEnvironmentVariable("ASPIRE_DASHBOARD_OTLP_HTTP_ENDPOINT_URL") ?? "http://localhost:4318");
// Allow unsecured transport for local development to avoid requiring HTTPS in launch profiles
Environment.SetEnvironmentVariable("ASPIRE_ALLOW_UNSECURED_TRANSPORT", Environment.GetEnvironmentVariable("ASPIRE_ALLOW_UNSECURED_TRANSPORT") ?? "true");

var builder = DistributedApplication.CreateBuilder(args);

var appHostDir = Environment.CurrentDirectory;
var solutionRoot = Directory.GetParent(appHostDir)?.FullName;
var aiWorkingDirectory = Path.Combine(solutionRoot!, "WealthWise.AI");
var aiScriptPath = Path.Combine(aiWorkingDirectory, "main.py");

//Execute the AI service using Python
builder.AddExecutable(
     name: "wealthwise-ai",
        command: "python",
        workingDirectory: aiWorkingDirectory)
    .WithArgs(aiScriptPath)
    .WithHttpEndpoint(port: 8000, targetPort: 8000, isProxied: false);

// Add the API project
builder.AddProject<Projects.WealthWise_API>("wealthwise-api")
    .WithEnvironment("AI_SERVICE_URL", "http://localhost:8000");

// Add the UI project
var uiWorkingDirectory = Path.Combine(solutionRoot!, "WealthWise.UI");
builder.AddExecutable("wealthwise-ui", "dotnet", uiWorkingDirectory)
    .WithArgs("run")
    .WithHttpsEndpoint(port: 7034, targetPort: 7034, isProxied: false);


builder.Build().Run();

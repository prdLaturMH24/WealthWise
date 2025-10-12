var builder = DistributedApplication.CreateBuilder(args);

var appHostDir = Environment.CurrentDirectory;
var solutionRoot = Directory.GetParent(appHostDir)?.FullName;
var aiWorkingDirectory = Path.Combine(solutionRoot!, "WealthWise.AI");
var aiScriptPath = Path.Combine(aiWorkingDirectory, "app.py");

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

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["WealthWise.UI/WealthWise.UI.csproj", "WealthWise.UI/"]
COPY ["WealthWise.Shared/WealthWise.Shared.csproj", "WealthWise.Shared/"]
RUN dotnet restore "WealthWise.UI/WealthWise.UI.csproj"
COPY . .
WORKDIR "/src/WealthWise.UI"
RUN dotnet publish "WealthWise.UI.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "WealthWise.UI.dll"]

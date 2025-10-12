FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["WealthWise.API/WealthWise.API.csproj", "WealthWise.API/"]
COPY ["WealthWise.Shared/WealthWise.Shared.csproj", "WealthWise.Shared/"]
COPY ["WealthWise.ServiceDefaults/WealthWise.ServiceDefaults.csproj", "WealthWise.ServiceDefaults/"]
RUN dotnet restore "WealthWise.API/WealthWise.API.csproj"
COPY . .
WORKDIR "/src/WealthWise.API"
RUN dotnet publish "WealthWise.API.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "WealthWise.API.dll"]

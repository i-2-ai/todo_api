# API base URL
$baseUrl = "https://todo-api-1-cab5djhbevacahdm.westeurope-01.azurewebsites.net"

function New-Todo {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Title,
        
        [Parameter(Mandatory=$false)]
        [string]$Description = "",
        
        [Parameter(Mandatory=$false)]
        [bool]$Completed = $false,
        
        [Parameter(Mandatory=$false)]
        [string]$DueDate = $null
    )
    
    $body = @{
        title = $Title
        description = $Description
        completed = $Completed
    }
    
    if ($DueDate) {
        $body.due_date = $DueDate
    }
    
    $jsonBody = $body | ConvertTo-Json
    
    Write-Host "Creating new todo..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Method Post -Uri "$baseUrl/todos/" -Body $jsonBody -ContentType "application/json"
    Write-Host "Todo created successfully!" -ForegroundColor Green
    return $response
}

function Get-Todos {
    Write-Host "Fetching all todos..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Method Get -Uri "$baseUrl/todos/" -ContentType "application/json"
    
    if ($response.Count -eq 0) {
        Write-Host "No todos found." -ForegroundColor Yellow
        return
    }
    
    Write-Host "`nFound $($response.Count) todos:" -ForegroundColor Green
    foreach ($todo in $response) {
        Write-Host "`nID: $($todo.id)" -ForegroundColor Cyan
        Write-Host "Title: $($todo.title)"
        Write-Host "Description: $($todo.description)"
        Write-Host "Completed: $($todo.completed)"
        Write-Host "Due Date: $($todo.due_date)"
        Write-Host "Created At: $($todo.created_at)"
    }
}

# Example usage:
Write-Host "Todo API Test Script" -ForegroundColor Magenta
Write-Host "===================" -ForegroundColor Magenta

Write-Host "`nExample commands:" -ForegroundColor Yellow
Write-Host "1. Create a new todo:" -ForegroundColor Cyan
Write-Host '   New-Todo -Title "Buy groceries" -Description "Get milk and bread" -DueDate "2024-12-31T23:59:59Z"'
Write-Host "2. List all todos:" -ForegroundColor Cyan
Write-Host "   Get-Todos" 
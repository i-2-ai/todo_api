# API base URL
$baseUrl = "https://todo-api-1-cab5djhbevacahdm.westeurope-01.azurewebsites.net"

# Create a web session to maintain cookies
$webSession = $null

# Get CSRF token from the server
function Get-CSRFToken {
    try {
        # Create a new web session if one doesn't exist
        if (-not $script:webSession) {
            $script:webSession = New-Object Microsoft.PowerShell.Commands.WebRequestSession
        }

        $response = Invoke-WebRequest -Method Get -Uri "$baseUrl/todos/" -ContentType "application/json" -WebSession $script:webSession
        $csrfToken = $response.Headers["X-CSRF-Token"]
        Write-Host "CSRF Token from response: $csrfToken" -ForegroundColor Yellow
        if (-not $csrfToken) {
            throw "CSRF token not found in response headers"
        }
        return $csrfToken[0]  # Get first token if multiple
    }
    catch {
        Write-Host "Error getting CSRF token: $_" -ForegroundColor Red
        throw
    }
}

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
    
    try {
        Write-Host "Getting CSRF token..." -ForegroundColor Yellow
        $csrfToken = Get-CSRFToken
        
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
        $headers = @{
            "X-CSRF-Token" = $csrfToken
            "Content-Type" = "application/json"
        }
        
        Write-Host "Sending request with headers:" -ForegroundColor Yellow
        $headers.GetEnumerator() | ForEach-Object {
            Write-Host "$($_.Key): $($_.Value)" -ForegroundColor Yellow
        }
        
        $response = Invoke-WebRequest -Method Post -Uri "$baseUrl/todos/" -Body $jsonBody -Headers $headers -WebSession $script:webSession
        Write-Host "Todo created successfully!" -ForegroundColor Green
        return $response.Content | ConvertFrom-Json
    }
    catch {
        Write-Host "Error creating todo: $_" -ForegroundColor Red
        throw
    }
}

function Get-Todos {
    try {
        Write-Host "Getting CSRF token..." -ForegroundColor Yellow
        $csrfToken = Get-CSRFToken
        
        Write-Host "Fetching all todos..." -ForegroundColor Yellow
        $headers = @{
            "X-CSRF-Token" = $csrfToken
            "Content-Type" = "application/json"
        }
        
        Write-Host "Sending request with headers:" -ForegroundColor Yellow
        $headers.GetEnumerator() | ForEach-Object {
            Write-Host "$($_.Key): $($_.Value)" -ForegroundColor Yellow
        }
        
        $response = Invoke-WebRequest -Method Get -Uri "$baseUrl/todos/" -Headers $headers -WebSession $script:webSession
        $todos = $response.Content | ConvertFrom-Json
        
        if ($todos.Count -eq 0) {
            Write-Host "No todos found." -ForegroundColor Yellow
            return
        }
        
        Write-Host "`nFound $($todos.Count) todos:" -ForegroundColor Green
        foreach ($todo in $todos) {
            Write-Host "`nID: $($todo.id)" -ForegroundColor Cyan
            Write-Host "Title: $($todo.title)"
            Write-Host "Description: $($todo.description)"
            Write-Host "Completed: $($todo.completed)"
            Write-Host "Due Date: $($todo.due_date)"
            Write-Host "Created At: $($todo.created_at)"
        }
    }
    catch {
        Write-Host "Error fetching todos: $_" -ForegroundColor Red
        throw
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
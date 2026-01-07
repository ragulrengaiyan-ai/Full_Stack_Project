$body = @{
    email    = "test@admin.com"
    password = "test123"
} | ConvertTo-Json

Write-Host "Testing NEW admin login to live API..."
Write-Host "URL: https://full-stack-project-iota-lime.vercel.app/api/users/login"
Write-Host "Credentials: test@admin.com / test123"
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "https://full-stack-project-iota-lime.vercel.app/api/users/login" -Method Post -Body $body -ContentType "application/json" -ErrorAction Stop
    Write-Host "SUCCESS! Login worked!" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
}
catch {
    Write-Host "FAILED! Login did not work" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

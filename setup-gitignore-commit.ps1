$ErrorActionPreference = "Stop"

Write-Host "=== Checking .gitignore ===" -ForegroundColor Cyan
$gitignorePath = ".gitignore"
$linesToAdd = @(
    "webapp/db.sqlite3",
    "webapp/**/__pycache__/",
    "webapp/*.pyc",
    ".venv/"
)

$existing = Get-Content $gitignorePath -ErrorAction SilentlyContinue
$added = @()

foreach ($line in $linesToAdd) {
    if ($existing -notcontains $line) {
        Add-Content $gitignorePath $line
        $added += $line
    }
}

if ($added.Count -gt 0) {
    Write-Host "Added to .gitignore:" -ForegroundColor Green
    $added | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
} else {
    Write-Host "Nothing to add, .gitignore already covers this." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Git status ===" -ForegroundColor Cyan
git status --short

Write-Host ""
Write-Host "=== Staging and committing ===" -ForegroundColor Cyan
git add .
git commit -m "Add Django project scaffold in webapp/"

Write-Host ""
Write-Host "=== Pushing to origin ===" -ForegroundColor Cyan
git push

Write-Host ""
Write-Host "Done." -ForegroundColor Green

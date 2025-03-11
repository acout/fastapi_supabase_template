# Ce script installe et configure l'environnement de développement sur Windows
# Il doit être exécuté depuis la racine du projet

$ErrorActionPreference = "Stop"

Write-Host "Installation de l'environnement de développement..."

# Vérifier si Python est installé
try {
    python --version | Out-Null
} catch {
    Write-Host "Python n'est pas installé ou n'est pas dans le PATH. Veuillez l'installer avant de continuer." -ForegroundColor Red
    exit 1
}

# Installer pre-commit si nécessaire
try {
    pre-commit --version | Out-Null
    Write-Host "pre-commit est déjà installé" -ForegroundColor Green
} catch {
    Write-Host "Installation de pre-commit..." -ForegroundColor Yellow
    pip install pre-commit
}

# Installer les hooks pre-commit
Write-Host "Installation des hooks pre-commit..." -ForegroundColor Yellow
pre-commit install

# Vérifier si uv est installé et l'installer si nécessaire
try {
    uv --version | Out-Null
    Write-Host "uv est déjà installé" -ForegroundColor Green
} catch {
    Write-Host "Installation de uv..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 -OutFile .\install-uv.ps1
    .\install-uv.ps1
    Remove-Item .\install-uv.ps1
    # Après l'installation, nous devons rafraîchir le PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "Machine")
}

# Installer les dépendances du projet
Write-Host "Installation des dépendances du projet..." -ForegroundColor Yellow
Push-Location backend
uv sync --all-groups --dev
Pop-Location

Write-Host "L'environnement de développement a été configuré avec succès!" -ForegroundColor Green
Write-Host "Vous pouvez maintenant développer avec les outils suivants:" -ForegroundColor Cyan
Write-Host " - pre-commit: pour vérifier automatiquement la qualité du code avant chaque commit" -ForegroundColor Cyan
Write-Host " - uv: pour gérer les dépendances Python" -ForegroundColor Cyan
Write-Host " - tests: exécutez 'cd backend && pytest' pour lancer les tests" -ForegroundColor Cyan

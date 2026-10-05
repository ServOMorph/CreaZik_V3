# Script de lancement rapide de la génération des playlists CreaZik

Write-Host "🎵 CreaZik Playlists Launcher" -ForegroundColor Magenta
Write-Host "================================`n" -ForegroundColor Magenta

$menu = @{
    "1" = "Générer une playlist"
    "2" = "Lister les modèles disponibles"
    "3" = "Mettre à jour le registre des modèles"
    "4" = "Ouvrir l'interface explorer"
    "5" = "Vérifier configuration"
    "6" = "Quitter"
}

while ($true) {
    Write-Host "`nOptions:" -ForegroundColor Cyan
    $menu.GetEnumerator() | Sort-Object Key | ForEach-Object {
        Write-Host "  $($_.Key) - $($_.Value)"
    }

    $choice = Read-Host "`nChoisir"

    switch ($choice) {
        "1" {
            Write-Host "`n▶️  Génération de la playlist..." -ForegroundColor Green
            $id = Read-Host "Identifiant de la playlist (ex: perso)"
            python run_queue.py "playlists/$id/config.json"
            Write-Host "`n✅ Génération terminée!" -ForegroundColor Green
            Write-Host "Ouvrez ui.html pour explorer les playlists" -ForegroundColor Yellow
        }
        "2" {
            Write-Host "`n📋 Modèles disponibles..." -ForegroundColor Green
            python model_updater.py list
        }
        "3" {
            Write-Host "`n🔄 Mise à jour des modèles..." -ForegroundColor Green
            python model_updater.py update
        }
        "4" {
            Write-Host "`n🌐 Ouverture de l'interface..." -ForegroundColor Green
            Start-Process "ui.html"
        }
        "5" {
            Write-Host "`n✓ Configuration:" -ForegroundColor Green

            if (Test-Path "playlists/perso/config.json") {
                $config = Get-Content "playlists/perso/config.json" | ConvertFrom-Json
                Write-Host "  ACE-Step: $(if (Test-Path $config.ace_step_path) { '✓ Trouvé' } else { '✗ Non trouvé' })" -ForegroundColor $(if (Test-Path $config.ace_step_path) { 'Green' } else { 'Red' })
                Write-Host "  Output Dir: $($config.output_dir)"
                Write-Host "  Test Cases: $($config.test_cases.Count)"
            }
        }
        "6" {
            Write-Host "`nAu revoir! 👋" -ForegroundColor Cyan
            break
        }
        default {
            Write-Host "Option invalide" -ForegroundColor Red
        }
    }
}

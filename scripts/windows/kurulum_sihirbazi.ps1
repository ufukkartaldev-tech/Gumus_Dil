<#
.SYNOPSIS
GümüşDil Kurulum Sihirbazı (Windows)
#>

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  GÜMÜŞDİL - YERLİ KOMPAKT İDE KURULUMU" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tavsiye Edilen: Milli Zeka Motoru, kod yazarken size hatalarınızı"
Write-Host "Türkçe açıklar ve örnekler verir. İnternetsiz çalışır."
Write-Host ""

$installAI = Read-Host "🤖 Milli Zeka Motoru (Ollama + gumus_zeka) kurulsun mu? (E/H)"

if ($installAI -match '^[eE]$') {
    Write-Host ""
    Write-Host "📦 [1/2] Milli Zeka Motoru Arka Planda İndiriliyor (Bu işlem internet hızınıza göre sürebilir)..." -ForegroundColor Yellow
    
    $ollamaExe = "$env:TEMP\OllamaSetup.exe"
    Invoke-WebRequest -Uri "https://ollama.com/download/OllamaSetup.exe" -OutFile $ollamaExe
    
    Write-Host "⚙️ Kurulum yapılıyor (Sessiz Mod)..." -ForegroundColor Yellow
    Start-Process -FilePath $ollamaExe -ArgumentList "/silent" -Wait
    
    Write-Host "🧠 [2/2] gumus_zeka Modeli Sisteme Entegre Ediliyor..." -ForegroundColor Yellow
    
    # Ollama servisinin ayağa kalkması için kısa bir süre bekle
    Start-Sleep -Seconds 5
    
    # Kendi modelimizi Modelfile üzerinden üretelim
    if (Test-Path "$PSScriptRoot\Modelfile") {
        Write-Host "   -> Yerel Modelfile bulundu, model oluşturuluyor..."
        Start-Process -FilePath "ollama" -ArgumentList "create gumus_zeka -f ""$PSScriptRoot\Modelfile""" -Wait
    } else {
        # Eğer Modelfile yoksa, varsayılan llama3 ya da önceden yüklenmiş bir repodan çekebilir (temsili)
        Start-Process -FilePath "ollama" -ArgumentList "pull llama3" -Wait
        Start-Process -FilePath "ollama" -ArgumentList "run llama3 --keepalive -1" -WindowStyle Hidden
    }

    Write-Host "✅ Milli Zeka başarıyla kuruldu ve arka planda çalışıyor!" -ForegroundColor Green

} else {
    Write-Host ""
    Write-Host "⚡ Seçim Kaydedildi: GümüşDil sadece 'Hafif Editör' (Lightweight) olarak ayarlandı." -ForegroundColor Blue
    Write-Host "   - Yapay Zeka özellikleri kapalıdır."
    Write-Host "   - Çevrimdışı hazır veri seti ile sadece temel sorulara yanıt verebilir."
}

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "🎉 GÜMÜŞDİL KURULUMU TAMAMLANDI! Başlatılıyor..." -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Start-Sleep -Seconds 2

# IDE'yi başlat
python -m src.ide.main

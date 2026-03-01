<#
.SYNOPSIS
GümüşDil Kurulum Sihirbazı (Windows)
#>

# 1. YÖNETİCİ Ayrıcalığı Kontrolü (Admin Check)
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (!$isAdmin) {
    Write-Host "❌ GEÇİŞ ENGELLENDİ: Yeğenim bu kurulum için Yönetici (Administrator) yetkisi lazım." -ForegroundColor Red
    Write-Host "Lütfen bu dosyaya sağ tıklayıp 'PowerShell ile Yönetici Olarak Çalıştır' seçeneğini kullan." -ForegroundColor Yellow
    Write-Host "Program kapatılıyor..."
    Start-Sleep -Seconds 5
    exit
}

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  GÜMÜŞDİL - YERLİ KOMPAKT İDE KURULUMU" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tavsiye Edilen: Milli Zeka Motoru, kod yazarken size hatalarınızı"
Write-Host "Türkçe açıklar ve örnekler verir. İnternetsiz çalışır."
Write-Host ""

# 2. PYTHON ve PIP Kontrolü
Write-Host "🔍 [1/3] Python Bağımlılıkları ve Sistem Kontrolü Yapılıyor..." -ForegroundColor Yellow
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ HATA: Python kurulu değil veya PATH'e ekli değil!" -ForegroundColor Red
    Write-Host "Lütfen python.org adresinden Python 3 yükleyip 'Add to PATH' seçeneğini işaretleyin." -ForegroundColor Red
    Start-Sleep -Seconds 7
    exit
}

$projectRoot = (Resolve-Path "$PSScriptRoot\..\..").Path
$reqPath = "$projectRoot\requirements.txt"

if (Test-Path $reqPath) {
    Write-Host "📦 Özel kütüphaneler kuruluyor (pip install -r requirements.txt)..." -ForegroundColor Yellow
    try {
        python -m pip install -r "$reqPath" | Out-Null
        Write-Host "✅ Kütüphaneler başarıyla kuruldu veya zaten güncel." -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ Kütüphaneler kurulurken ufak bir pürüz oldu ama devam ediyoruz." -ForegroundColor DarkYellow
    }
}
else {
    Write-Host "📦 requirements.txt bulunamadı, standart bileşenlerle devam ediliyor." -ForegroundColor DarkGray
    # Standart minimal kütüphanelerden emin olalım
    python -m pip install requests customtkinter | Out-Null
}

# 3. MİLLİ ZEKA Kurulumu (Try-Catch / Internet Kontrolü)
Write-Host ""
$installAI = Read-Host "🤖 [2/3] Milli Zeka Motoru (Ollama + gumus_zeka) kurulsun mu? (E/H)"

if ($installAI -match '^[eE]$') {
    Write-Host ""
    Write-Host "📦 Zeka Motoru İndiriliyor (Bu işlem internet hızınıza göre sürebilir)..." -ForegroundColor Yellow
    
    $ollamaExe = "$env:TEMP\OllamaSetup.exe"
    
    try {
        # İnternet yoksa Invoke-WebRequest hata fırlatır ve catch bloğuna düşer
        Invoke-WebRequest -Uri "https://ollama.com/download/OllamaSetup.exe" -OutFile $ollamaExe -ErrorAction Stop
        
        Write-Host "⚙️ Kurulum yapılıyor (Sessiz Mod)..." -ForegroundColor Yellow
        Start-Process -FilePath $ollamaExe -ArgumentList "/silent" -Wait
        
        Write-Host "🧠 [3/3] gumus_zeka Modeli Eğitiliyor..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        
        $modelPath = "$projectRoot\Modelfile"
        if (Test-Path $modelPath) {
            Start-Process -FilePath "ollama" -ArgumentList "create gumus_zeka -f ""$modelPath""" -Wait
            Write-Host "✅ Milli Zeka başarıyla eğitildi ve sisteme eklendi!" -ForegroundColor Green
        }
        else {
            Write-Host "⚠️ Modelfile bulunamadı! Varsayılan model internetten çekilecek." -ForegroundColor DarkYellow
            Start-Process -FilePath "ollama" -ArgumentList "pull llama3" -Wait
            Write-Host "✅ Alternatif Zeka (Llama3) kuruldu!" -ForegroundColor Green
        }

    }
    catch {
        Write-Host "⚠️ İNTERNET YOK YEĞENİM! Başlantı koptuğu için Milli Zeka Modülü indirilemedi." -ForegroundColor Red
        Write-Host "Endişe etme, GümüşDil'in [Çevrimdışı Belleği] ile hafif modda çalışmaya devam ediyoruz." -ForegroundColor DarkYellow
    }
}
else {
    Write-Host ""
    Write-Host "⚡ Seçim Kaydedildi: GümüşDil sadece 'Hafif Editör' (Lightweight) olarak ayarlandı." -ForegroundColor Blue
    Write-Host "   - Yapay Zeka özellikleri kapalıdır."
    Write-Host "   - Çevrimdışı hazır veri seti ile sadece temel sorulara yanıt verebilir."
}

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "🎉 GÜMÜŞDİL KURULUMU TAMAMLANDI! IDE Başlatılıyor..." -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Start-Sleep -Seconds 2

# IDE'yi başlat
Set-Location $projectRoot
python -m src.ide.main

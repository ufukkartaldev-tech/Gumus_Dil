# Nihai Turkce Guncelleme Script'i
# Kod, yorum satirlari ve metinler dahil her seyi pirlanta gibi Turkcelestirir.

$files = Get-ChildItem -Path "." -Filter "*.tr" -Recurse -File | Where-Object { 
    $_.FullName -notlike "*\build\*" -and $_.FullName -notlike "*\bin\*" 
}

$toplam = 0
foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $eskiContent = $content
    
    # Kelime listesi (Daha agresif degisim)
    $content = $content -replace '\b(e|E)ger\b', '$1ğer'
    $content = $content -replace '\b(d|D)ongu\b', '$1öngü'
    $content = $content -replace '\b(d|D)egisken\b', '$1eğişken'
    $content = $content -replace '\b(d|D)on\b', '$1ön'
    $content = $content -replace '\b(d|D)ogru\b', '$1oğru'
    $content = $content -replace '\b(y|Y)anlis\b', '$1anlış'
    $content = $content -replace '\b(y|Y)azdir\b', '$1azdır'
    $content = $content -replace '\b(b|B)os\b', '$1oş'
    $content = $content -replace '\b(d|D)eger\b', '$1eğer'
    $content = $content -replace '\bmat_us\b', 'mat_üs'
    $content = $content -replace '\bmat_mutlak_deger\b', 'mat_mutlak_değer'
    $content = $content -replace '\bkarekok\b', 'karekok' # Zaten oyleyse dokunma
    
    if ($content -ne $eskiContent) {
        Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
        Write-Host "Pirlanta gibi oldu: $($file.Name)"
        $toplam++
    }
}

Write-Host "`n[OPERASYON TAMAMLANDI]"
Write-Host "Toplam $toplam dosya modernize edildi."

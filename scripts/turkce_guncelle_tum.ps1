# Turkce Syntax Guncelleme Script'i - TUM DOSYALAR
# Tum .tr dosyalarindaki eski syntax'i yeni syntax'e cevir

$files = Get-ChildItem -Path "." -Filter "*.tr" -Recurse -File | Where-Object { 
    $_.FullName -notlike "*\node_modules\*" 
}

$toplam = 0
foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $eskiContent = $content
    
    # Eski syntax -> Yeni syntax (kelime sinirlariyla)
    $content = $content -replace '\beger\s*\(', 'eğer ('
    $content = $content -replace '\bdongu\s*\(', 'döngü ('
    $content = $content -replace '\bdegisken\s+', 'değişken '
    $content = $content -replace '\bdon\s+', 'dön '
    $content = $content -replace '\bdogru\b', 'doğru'
    $content = $content -replace '\byanlis\b', 'yanlış'
    $content = $content -replace '\byazdir\s*\(', 'yazdır('
    $content = $content -replace '\bbos\b', 'boş'
    $content = $content -replace 'deger', 'değer'
    $content = $content -replace 'mat_us\(', 'mat_üs('
    
    # Eger degisiklik varsa kaydet
    if ($content -ne $eskiContent) {
        Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
        Write-Host "Guncellendi: $($file.Name)"
        $toplam++
    }
}

Write-Host "`nToplam $toplam dosya guncellendi!"
Write-Host "Taranan dosya sayisi: $($files.Count)"

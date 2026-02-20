# Turkce Syntax Guncelleme Script'i
# Tum .tr dosyalarindaki eski syntax'i yeni syntax'e cevir

$files = Get-ChildItem -Path "lib","std_lib" -Filter "*.tr" -Recurse -File

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    
    # Eski syntax -> Yeni syntax
    $content = $content -replace '\beger\s*\(', 'eğer ('
    $content = $content -replace '\bdongu\s*\(', 'döngü ('
    $content = $content -replace '\bdegisken\s+', 'değişken '
    $content = $content -replace '\bdon\s+', 'dön '
    $content = $content -replace '\bdogru\b', 'doğru'
    $content = $content -replace '\byanlis\b', 'yanlış'
    $content = $content -replace '\byazdir\s*\(', 'yazdır('
    $content = $content -replace '\bbos\b', 'boş'
    $content = $content -replace '\bdeger', 'değer'
    $content = $content -replace 'mat_us\(', 'mat_üs('
    
    # Dosyayi kaydet
    Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
    Write-Host "Guncellendi: $($file.FullName)"
}

Write-Host "`nToplam $($files.Count) dosya guncellendi!"

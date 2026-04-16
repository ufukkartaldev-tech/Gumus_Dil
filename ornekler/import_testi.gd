// import_testi.gd - dahil_et sistemini test eder

// --- Test 1: Global scope'a aktarma ---
dahil_et "ornekler/matematik.gd"

yazdır topla(3, 5)       // 8
yazdır kare(7)           // 49
yazdır mutlak(-42)       // 42
yazdır PI                // 3.14159...

// --- Test 2: Alias ile modül namespace ---
dahil_et "ornekler/matematik.gd" olarak Mat

yazdır Mat::topla(10, 20)  // 30
yazdır Mat::PI             // 3.14159...

// --- Test 3: Döngüsel Bağımlılık ---
// Bu dosyanın kendini tekrar import etmeye çalışması sonsuz döngüye girmez
dahil_et "ornekler/import_testi.gd"  // İkinci kez -> sessizce atlanır

powershell -Command "Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile 'vcredist_x64.exe'"# -*- coding: utf-8 -*-
"""
GümüşDil Modern Syntax Unit Tests
Test-Driven Development: Önce test, sonra kod!

Test Kategorileri:
1. Noktalı virgül yasağı
2. String birleştirme
3. Fonksiyon tanımlama ve çağırma
4. Döngüler ve koşullar
5. Değişken tanımlama
"""

import subprocess
import sys
from pathlib import Path

# Proje kökü
PROJECT_ROOT = Path(__file__).parent.parent
SIMULATOR_PATH = PROJECT_ROOT / "src" / "ide" / "core" / "run_simulator.py"

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def run_code(self, code, expected_output=None, should_fail=False):
        """GümüşDil kodunu simülatörde çalıştır"""
        # Geçici dosya oluştur
        test_file = PROJECT_ROOT / "temp" / "unit_test.tr"
        test_file.parent.mkdir(exist_ok=True)
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        try:
            result = subprocess.run(
                [sys.executable, str(SIMULATOR_PATH), str(test_file)],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=5
            )
            
            output = result.stdout.strip()
            error = result.stderr.strip()
            
            if should_fail:
                # Hata bekliyoruz
                if result.returncode != 0 or error:
                    return True, f"Beklenen hata alındı: {error[:50]}"
                else:
                    return False, f"Hata bekliyorduk ama kod çalıştı!"
            else:
                # Başarı bekliyoruz
                if result.returncode == 0:
                    if expected_output is None:
                        return True, f"Kod başarıyla çalıştı"
                    elif expected_output in output:
                        return True, f"Beklenen çıktı alındı: {expected_output}"
                    else:
                        return False, f"Çıktı eşleşmedi. Beklenen: {expected_output}, Alınan: {output[:100]}"
                else:
                    return False, f"Kod hata verdi: {error[:100]}"
        
        except subprocess.TimeoutExpired:
            return False, "Timeout - kod çok uzun sürdü"
        except Exception as e:
            return False, f"Test hatası: {str(e)}"
    
    def test(self, name, code, expected_output=None, should_fail=False):
        """Tek bir test çalıştır"""
        print(f"\nTest: {name}")
        print(f"   Kod: {code[:60]}...")
        
        success, message = self.run_code(code, expected_output, should_fail)
        
        if success:
            self.passed += 1
            print(f"   {message}")
        else:
            self.failed += 1
            print(f"   {message}")
        
        self.tests.append({
            'name': name,
            'success': success,
            'message': message
        })
        
        return success
    
    def summary(self):
        """Test özeti"""
        print("\n" + "="*60)
        print(f"TEST SONUÇLARI")
        print("="*60)
        print(f"Başarılı: {self.passed}")
        print(f"Başarısız: {self.failed}")
        print(f"Toplam: {self.passed + self.failed}")
        print(f"Başarı Oranı: {(self.passed/(self.passed+self.failed)*100):.1f}%")
        print("="*60)
        
        if self.failed > 0:
            print("\nBAŞARISIZ TESTLER:")
            for test in self.tests:
                if not test['success']:
                    print(f"   - {test['name']}: {test['message']}")
        
        return self.failed == 0


def main():
    runner = TestRunner()
    
    print("GümüşDil Modern Syntax Unit Tests")
    print("="*60)
    
    # ============================================
    # 1. NOKTALΙ VΙRGÜL YASAĞI TESTLERİ
    # ============================================
    print("\nKategori 1: Noktalı Virgül Yasağı")
    
    runner.test(
        "Noktalı virgül kullanımı HATA vermeli",
        'yazdır("Test");',
        should_fail=True
    )
    
    runner.test(
        "Noktalı virgül olmadan çalışmalı",
        'yazdır("Test")',
        expected_output="Test"
    )
    
    runner.test(
        "Değişken tanımlama - noktalı virgül yasak",
        'değişken x = 5;',
        should_fail=True
    )
    
    runner.test(
        "Değişken tanımlama - modern sözdizimi",
        'değişken x = 5\nyazdır(x)',
        expected_output="5"
    )
    
    # ============================================
    # 2. STRING BİRLEŞTİRME TESTLERİ
    # ============================================
    print("\nKategori 2: String Birleştirme")
    
    runner.test(
        "Basit string birleştirme",
        'yazdır("Merhaba " + "Dünya")',
        expected_output="Merhaba Dünya"
    )
    
    runner.test(
        "Değişkenle string birleştirme",
        'değişken isim = "Ufuk"\nyazdır("Selam " + isim)',
        expected_output="Selam Ufuk"
    )
    
    runner.test(
        "Çoklu string birleştirme",
        'yazdır("A" + "B" + "C")',
        expected_output="ABC"
    )
    
    # ============================================
    # 3. FONKSİYON TESTLERİ
    # ============================================
    print("\nKategori 3: Fonksiyonlar")
    
    runner.test(
        "Basit fonksiyon tanımlama ve çağırma",
        '''fonksiyon selamla() {
    yazdır("Merhaba")
}
selamla()''',
        expected_output="Merhaba"
    )
    
    runner.test(
        "Parametreli fonksiyon",
        '''fonksiyon topla(a, b) {
    dön a + b
}
yazdır(topla(3, 5))''',
        expected_output="8"
    )
    
    # ============================================
    # 4. DÖNGÜ TESTLERİ
    # ============================================
    print("\nKategori 4: Döngüler")
    
    runner.test(
        "Basit döngü",
        '''değişken i = 0
döngü (i < 3) {
    yazdır(i)
    i = i + 1
}''',
        expected_output="0"
    )
    
    # ============================================
    # 5. KOŞUL TESTLERİ
    # ============================================
    print("\nKategori 5: Koşullar")
    
    runner.test(
        "Basit if koşulu",
        '''değişken x = 5
eğer (x > 3) {
    yazdır("Büyük")
}''',
        expected_output="Büyük"
    )
    
    runner.test(
        "If-else koşulu",
        '''değişken x = 2
eğer (x > 3) {
    yazdır("Büyük")
} değilse {
    yazdır("Küçük")
}''',
        expected_output="Küçük"
    )
    
    # ============================================
    # 6. KARMAŞIK SENARYOLAR
    # ============================================
    print("\nKategori 6: Karmaşık Senaryolar")
    
    runner.test(
        "Fibonacci (basit versiyon)",
        '''fonksiyon fib(n) {
    eğer (n <= 1) {
        dön n
    }
    dön fib(n - 1) + fib(n - 2)
}
yazdır(fib(5))''',
        expected_output="5"
    )
    
    # Özet
    success = runner.summary()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())


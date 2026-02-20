"""
🚨 GÜMÜŞ ZEKA - AI Error Interceptor
Otomatik hata yakalama, analiz ve çözüm önerisi sistemi
"""

import re
import json
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Callable, Dict, Any


class ErrorType(Enum):
    """Hata tipleri"""
    SYNTAX = "syntax"           # Sözdizimi hatası
    RUNTIME = "runtime"         # Çalışma zamanı hatası
    LINKER = "linker"          # Bağlayıcı hatası
    LOGIC = "logic"            # Mantık hatası (sonsuz döngü vb.)
    SEMANTIC = "semantic"      # Anlamsal hata
    UNKNOWN = "unknown"        # Bilinmeyen hata


class ErrorSeverity(Enum):
    """Hata şiddeti"""
    CRITICAL = "critical"      # Kritik - Program çalışmaz
    ERROR = "error"           # Hata - Düzeltilmeli
    WARNING = "warning"       # Uyarı - Dikkat edilmeli
    INFO = "info"            # Bilgi - İyileştirme önerisi


@dataclass
class ErrorInfo:
    """Hata bilgisi"""
    type: ErrorType
    severity: ErrorSeverity
    line: int
    column: int
    message: str
    code_snippet: str
    file_path: str
    
    # AI analizi
    ai_analysis: Optional[str] = None
    ai_suggestion: Optional[str] = None
    auto_fix_code: Optional[str] = None
    
    # Metadata
    timestamp: Optional[str] = None
    stack_trace: Optional[List[str]] = None


class ErrorInterceptor:
    """
    AI destekli hata yakalayıcı
    
    Görevler:
    1. Compiler/Interpreter çıktısını izle
    2. Hataları yakala ve sınıflandır
    3. AI ile analiz et
    4. Çözüm önerisi sun
    5. Auto-fix kodu üret
    """
    
    def __init__(self, ai_callback: Optional[Callable] = None):
        """
        Args:
            ai_callback: AI analizi için callback fonksiyonu
        """
        self.ai_callback = ai_callback
        self.error_history: List[ErrorInfo] = []
        
        # Hata pattern'leri (Regex)
        self.error_patterns = {
            ErrorType.SYNTAX: [
                (r"Parse Error: (.+) \(Satir: (\d+)\)", "Sözdizimi hatası"),
                (r"Syntax Error: (.+) at line (\d+)", "Syntax hatası"),
                (r"Expected (.+) but got (.+) at line (\d+)", "Beklenmeyen token"),
            ],
            ErrorType.RUNTIME: [
                (r"Runtime Error: (.+) \(Satir: (\d+)\)", "Çalışma zamanı hatası"),
                (r"Tanimlanmamis degisken: '(.+)'", "Tanımsız değişken"),
                (r"Division by zero at line (\d+)", "Sıfıra bölme"),
            ],
            ErrorType.LINKER: [
                (r"undefined reference to `(.+)'", "Tanımsız referans"),
                (r"LNK2019: unresolved external symbol (.+)", "Çözülmemiş sembol"),
                (r"ld returned (\d+) exit status", "Linker hatası"),
            ],
            ErrorType.LOGIC: [
                (r"Infinite loop detected at line (\d+)", "Sonsuz döngü"),
                (r"Stack overflow at line (\d+)", "Stack taşması"),
            ],
        }
        
        # Türkçe hata mesajları için pattern'ler
        self.turkish_patterns = {
            "degisken": "değişken",
            "dongu": "döngü",
            "eger": "eğer",
            "degilse": "değilse",
            "yazdir": "yazdır",
            "fonksiyon": "fonksiyon",
        }
        
    def intercept_compiler_output(self, output: str, file_path: str = "") -> Optional[ErrorInfo]:
        """
        Compiler çıktısını yakala ve hata analizi yap
        
        Args:
            output: Compiler/Interpreter çıktısı
            file_path: Hatalı dosya yolu
            
        Returns:
            ErrorInfo nesnesi veya None
        """
        # Hata tipini tespit et
        error_type, match = self._detect_error_type(output)
        
        if not match:
            return None
            
        # Hata bilgilerini çıkar
        error_info = self._extract_error_info(error_type, match, output, file_path)
        
        # AI analizi yap
        if self.ai_callback:
            error_info = self._analyze_with_ai(error_info)
            
        # Geçmişe ekle
        self.error_history.append(error_info)
        
        return error_info
        
    def _detect_error_type(self, output: str) -> tuple[ErrorType, Optional[re.Match]]:
        """Hata tipini tespit et"""
        for error_type, patterns in self.error_patterns.items():
            for pattern, _ in patterns:
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    return error_type, match
                    
        return ErrorType.UNKNOWN, None
        
    def _extract_error_info(self, error_type: ErrorType, match: re.Match, 
                           output: str, file_path: str) -> ErrorInfo:
        """Hata bilgilerini çıkar"""
        # Satır numarasını bul
        line = 0
        for group in match.groups():
            if isinstance(group, str) and group.isdigit():
                line = int(group)
                break
                
        # Hata mesajını al
        message = match.group(0)
        
        # Severity belirle
        severity = ErrorSeverity.ERROR
        if error_type == ErrorType.LINKER:
            severity = ErrorSeverity.CRITICAL
        elif error_type == ErrorType.LOGIC:
            severity = ErrorSeverity.WARNING
            
        return ErrorInfo(
            type=error_type,
            severity=severity,
            line=line,
            column=0,
            message=message,
            code_snippet="",
            file_path=file_path
        )
        
    def _analyze_with_ai(self, error_info: ErrorInfo) -> ErrorInfo:
        """AI ile hata analizi yap"""
        if not self.ai_callback:
            return error_info
            
        # AI'ya gönderilecek prompt
        prompt = self._create_ai_prompt(error_info)
        
        try:
            # AI callback'i çağır
            ai_response = self.ai_callback(prompt)
            
            # AI yanıtını parse et
            error_info.ai_analysis = ai_response.get("analysis", "")
            error_info.ai_suggestion = ai_response.get("suggestion", "")
            error_info.auto_fix_code = ai_response.get("fix_code", "")
            
        except Exception as e:
            error_info.ai_analysis = f"AI analizi başarısız: {str(e)}"
            
        return error_info
        
    def _create_ai_prompt(self, error_info: ErrorInfo) -> str:
        """AI için prompt oluştur"""
        prompt = f"""
🚨 GÜMÜŞ ZEKA - Hata Analizi Talebi

**Hata Tipi:** {error_info.type.value}
**Şiddet:** {error_info.severity.value}
**Satır:** {error_info.line}
**Mesaj:** {error_info.message}

**Kod Parçası:**
```gümüşdil
{error_info.code_snippet}
```

**Görevin:**
1. Bu hatayı Türkçe olarak açıkla (basit, anlaşılır dil)
2. Hatanın muhtemel nedenlerini listele
3. Adım adım çözüm önerisi sun
4. Mümkünse düzeltilmiş kod örneği ver

**Yanıt Formatı (JSON):**
{{
    "analysis": "Hata analizi...",
    "suggestion": "Çözüm önerisi...",
    "fix_code": "Düzeltilmiş kod..."
}}
"""
        return prompt
        
    def suggest_fix(self, error_info: ErrorInfo) -> str:
        """Hata için düzeltme önerisi"""
        if error_info.ai_suggestion:
            return error_info.ai_suggestion
            
        # Fallback: Pattern-based suggestions
        return self._pattern_based_suggestion(error_info)
        
    def _pattern_based_suggestion(self, error_info: ErrorInfo) -> str:
        """Pattern tabanlı öneri (AI yoksa)"""
        message = error_info.message.lower()
        
        # Tanımsız değişken
        if "tanimlanmamis" in message or "undefined" in message:
            var_match = re.search(r"'(.+)'", error_info.message)
            if var_match:
                var_name = var_match.group(1)
                return f"💡 '{var_name}' değişkeni tanımlanmamış. Önce 'değişken {var_name} = ...' şeklinde tanımlayın."
                
        # Sözdizimi hatası
        if error_info.type == ErrorType.SYNTAX:
            # Türkçe karakter kontrolü
            for wrong, correct in self.turkish_patterns.items():
                if wrong in message:
                    return f"💡 '{wrong}' yerine '{correct}' yazmalısınız."
                    
        # Linker hatası
        if error_type == ErrorType.LINKER:
            return "💡 Eksik kütüphane veya fonksiyon tanımı. '#dahil_et' komutunu kontrol edin."
            
        return "💡 Kodu dikkatle kontrol edin ve hata mesajını okuyun."
        
    def get_error_statistics(self) -> Dict[str, Any]:
        """Hata istatistikleri"""
        if not self.error_history:
            return {}
            
        stats = {
            "total_errors": len(self.error_history),
            "by_type": {},
            "by_severity": {},
            "most_common_line": 0,
        }
        
        # Tip bazında
        for error in self.error_history:
            error_type = error.type.value
            stats["by_type"][error_type] = stats["by_type"].get(error_type, 0) + 1
            
            severity = error.severity.value
            stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1
            
        # En çok hata alan satır
        lines = [e.line for e in self.error_history if e.line > 0]
        if lines:
            stats["most_common_line"] = max(set(lines), key=lines.count)
            
        return stats


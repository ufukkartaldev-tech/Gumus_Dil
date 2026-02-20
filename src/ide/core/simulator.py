import re
import os
import time
import math
import random

class GumusSimulator:
    def __init__(self, output_callback=None):
        self.variables = {}
        self.functions = {}
        self.output_callback = output_callback if output_callback else print
        self.running = True
        self.trace_enabled = True # Görsel hata ayıklama için izleme
        self.execution_delay = 0.05 # Adım adım izleme için gecikme (ms)

    def log(self, message):
        if self.output_callback:
            self.output_callback(str(message))

    def run(self, code):
        self.running = True
        try:
            # Önce fonksiyonları parse et
            self.parse_functions(code)
            
            # Kodu satırlara böl ve çalıştır
            lines = code.split('\n')
            self.execute_block(lines, 0, len(lines))
            
        except SyntaxError as e:
            self.log(f"Syntax Hatası: {e}")
            raise
        except Exception as e:
            err_msg = str(e)
            if "name" in err_msg and "is not defined" in err_msg:
                var_name = err_msg.split("'")[1]
                err_msg = f"Tanımsız değişken veya fonksiyon: '{var_name}'"
            elif "division by zero" in err_msg:
                err_msg = "Sıfıra bölme hatası: Matematik kurallarına aykırı yeğenim."
            
            self.log(f"Simülasyon Hatası: {err_msg}")

    def execute_block(self, lines, start, end):
        """Bir kod bloğunu çalıştır (döngü ve if için)"""
        i = start
        while i < end and self.running:
            line_raw = lines[i]
            line = line_raw.strip()
            
            # 💎 Mühendislik Zirvesi: Görsel İzleme Sinyali
            # IDE bu sinyali yakalayıp editörde satırı vurgulayacak
            if self.trace_enabled and line and not line.startswith('//'):
                # Satır İzleme (Trace)
                self.log(f"__TRACE__:{i + 1}")
                
                # 👁️ GümüşGöz: Değişken İzleme (JSON formatında fırlat)
                if self.variables:
                    import json
                    # Sadece temel tipleri gönder ki şişmesin
                    clean_vars = {k: v for k, v in self.variables.items() if isinstance(v, (int, float, str, bool, list, dict))}
                    self.log(f"__VARS__:{json.dumps(clean_vars)}")

                # 📊 GümüşRadar: Profiling Sinyali
                if i % 10 == 0: # Her 10 satırda bir raporla (Performans için)
                    import psutil
                    cpu = psutil.cpu_percent()
                    mem = psutil.Process().memory_info().rss / (1024 * 1024)
                    self.log(f"__PROFILE__:{{\"cpu\": {cpu}, \"mem\": {mem:.1f}, \"line\": {i+1}}}")

                if self.execution_delay > 0:
                    time.sleep(self.execution_delay)
            
            i += 1
            
            if not line or line.startswith('//'):
                continue
            
            # Fonksiyon tanımlarını atla
            if line.startswith('fonksiyon '):
                brace_count = 0
                while i < end:
                    if '{' in lines[i]: brace_count += 1
                    if '}' in lines[i]: brace_count -= 1
                    i += 1
                    if brace_count == 0:
                        break
                continue
            
            # If-else bloğu
            if line.startswith('eğer ') or line.startswith('eğer('):
                self.log(f"DEBUG: If bloğu bulundu: {line}")
                new_i = self.execute_if(lines, i - 1, end)
                i = new_i
                continue
            
            # Döngü bloğu
            if line.startswith('döngü ') or line.startswith('döngü('):
                new_i = self.execute_loop(lines, i - 1, end)
                i = new_i
                continue
            
            # Blok sonu
            if line == '}':
                continue
            
            # Normal satır
            self.execute_line(line)
        
        return i

    def execute_if(self, lines, start_idx, end):
        """If-else bloğunu çalıştır"""
        line = lines[start_idx].strip()
        
        # Koşulu çıkar: eğer (x > 3) { veya eğer x > 3 {
        if '(' in line:
            cond_start = line.index('(') + 1
            cond_end = line.rindex(')')
            condition = line[cond_start:cond_end]
        else:
            # eğer x > 3 {
            condition = line[5:line.index('{')].strip()
        
        # Koşulu değerlendir
        cond_result = self.evaluate(condition)
        
        # Then bloğunu bul
        i = start_idx + 1
        brace_count = 1
        then_start = i
        while i < end and brace_count > 0:
            if '{' in lines[i]: brace_count += 1
            if '}' in lines[i]: brace_count -= 1
            if brace_count == 0:
                break
            i += 1
        then_end = i
        
        # Else bloğunu kontrol et
        else_start = None
        else_end = None
        
        # } değilse { formatını kontrol et
        next_line_idx = i
        while next_line_idx < end and not lines[next_line_idx].strip():
            next_line_idx += 1
        
        # 'değilse' VEYA 'yoksa' kontrolü
        found_else = False
        else_line = ""
        
        if next_line_idx < end:
            check_line = lines[next_line_idx].strip()
            if check_line.startswith('değilse') or check_line.startswith('yoksa'):
                found_else = True
                i = next_line_idx
                else_line = check_line

        if found_else:
            # değilse eğer ... (else if)
            if 'eğer' in else_line:
                # Recursive if çağır
                return self.execute_if(lines, i, end)
            
            # Normal else bloğu - { satırını bul
            if '{' in else_line:
                # Aynı satırda: } değilse {
                i += 1
            else:
                # Sonraki satırda: değilse \n {
                i += 1
                while i < end and lines[i].strip() != '{':
                    i += 1
                i += 1
            
            brace_count = 1
            else_start = i
            while i < end and brace_count > 0:
                if '{' in lines[i]: brace_count += 1
                if '}' in lines[i]: brace_count -= 1
                if brace_count == 0:
                    break
                i += 1
            else_end = i
        
        # Koşula göre çalıştır
        if cond_result:
            self.execute_block(lines, then_start, then_end)
        elif else_start is not None:
            self.execute_block(lines, else_start, else_end)
        
        return i + 1

    def execute_loop(self, lines, start_idx, end):
        """Döngü bloğunu çalıştır"""
        line = lines[start_idx].strip()
        
        # Koşulu çıkar: döngü (i < 10) { veya döngü i < 10 {
        if '(' in line:
            cond_start = line.index('(') + 1
            cond_end = line.rindex(')')
            condition = line[cond_start:cond_end]
        else:
            # döngü i < 10 {
            condition = line[6:line.index('{')].strip()
        
        # Döngü bloğunu bul
        i = start_idx + 1
        brace_count = 1
        loop_start = i
        while i < end and brace_count > 0:
            if '{' in lines[i]: brace_count += 1
            if '}' in lines[i]: brace_count -= 1
            if brace_count == 0:
                break
            i += 1
        loop_end = i
        
        # Döngüyü çalıştır
        max_iterations = 10000  # Sonsuz döngü koruması
        iteration = 0
        while iteration < max_iterations and self.running:
            # Koşulu kontrol et
            if condition:
                cond_result = self.evaluate(condition)
                if not cond_result:
                    break
            
            # Döngü gövdesini çalıştır
            self.execute_block(lines, loop_start, loop_end)
            iteration += 1
        
        return i + 1

    def parse_functions(self, code):
        """Fonksiyon tanımlarını parse et"""
        lines = code.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('fonksiyon '):
                match = re.match(r'fonksiyon\s+(\w+)\s*\((.*?)\)\s*\{', line)
                if match:
                    func_name = match.group(1)
                    params_str = match.group(2).strip()
                    params = [p.strip() for p in params_str.split(',')] if params_str else []
                    
                    # Fonksiyon gövdesini topla
                    body_lines = []
                    i += 1
                    brace_count = 1
                    while i < len(lines) and brace_count > 0:
                        body_line = lines[i]
                        if '{' in body_line: brace_count += 1
                        if '}' in body_line: brace_count -= 1
                        if brace_count > 0:
                            body_lines.append(body_line)
                        i += 1
                    
                    self.functions[func_name] = {
                        'params': params,
                        'body': '\n'.join(body_lines)
                    }
                    continue
            i += 1

    def call_function(self, func_name, args):
        """Fonksiyon çağır"""
        if func_name not in self.functions:
            raise NameError(f"Fonksiyon tanımlı değil: {func_name}")
        
        func = self.functions[func_name]
        
        # Parametreleri değişkenlere ata
        old_vars = self.variables.copy()
        for param, arg in zip(func['params'], args):
            self.variables[param] = arg
        
        # Fonksiyon gövdesini çalıştır
        result = None
        for line in func['body'].split('\n'):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            # dön statement'ı
            if line.startswith('dön '):
                expr = line[4:].strip()
                result = self.evaluate(expr)
                break
            
            self.execute_line(line)
        
        # Değişkenleri geri yükle
        self.variables = old_vars
        return result

    def execute_line(self, line):
        # Yorum temizle
        if '//' in line:
            line = line.split('//')[0].strip()
        
        # Noktalı virgül temizliği (Otomatik düzeltme)
        if line.rstrip().endswith(';'):
            line = line.rstrip()[:-1]
        
        line = line.strip()

        # 1. Yazdır
        if line.startswith('yazdır('):
            # Parantezleri dengeli şekilde bul
            paren_count = 0
            start_idx = 7
            end_idx = start_idx
            for i in range(start_idx, len(line)):
                if line[i] == '(':
                    paren_count += 1
                elif line[i] == ')':
                    if paren_count == 0:
                        end_idx = i
                        break
                    paren_count -= 1
            
            content = line[start_idx:end_idx]
            val = self.evaluate(content)
            self.log(val)
            return

        # 2. Değişken Tanımlama
        if line.startswith('değişken ') or line.startswith('var '):
            parts = line.split('=')
            var_part = parts[0].strip()
            expr_part = '='.join(parts[1:]).strip()
            
            var_name = var_part.split()[-1]
            val = self.evaluate(expr_part)
            self.variables[var_name] = val
            return

        # 3. Atama
        if '=' in line and not any(op in line for op in ['==', '!=', '>=', '<=']):
            parts = line.split('=')
            var_name = parts[0].strip()
            if var_name in self.variables or not ' ' in var_name:
                expr = '='.join(parts[1:]).strip()
                val = self.evaluate(expr)
                self.variables[var_name] = val
                return

    def evaluate(self, expr):
        expr = str(expr).strip()
        
        # Template String: $"..."
        if expr.startswith('$"'):
            def replacer(match):
                key = match.group(1)
                return str(self.evaluate_expression(key))
            content = expr[2:-1]
            return re.sub(r'\{([^}]+)\}', replacer, content)

        # Saf String
        if expr.startswith('"') and expr.endswith('"'):
            if '+' not in expr:
                return expr.strip('"')
        
        # Türkçe Boolean Sabitleri
        if expr == "doğru": return True
        if expr == "yanlış": return False

        # Fonksiyon Çağrısı
        func_match = re.match(r'^(\w+)\((.*)\)$', expr)
        if func_match:
            func_name = func_match.group(1)
            args_str = func_match.group(2).strip()
            
            # Built-in fonksiyonlar
            if func_name == 'metin':
                arg_val = self.evaluate(args_str) if args_str else ""
                return str(arg_val)
            elif func_name == 'sayı':
                arg_val = self.evaluate(args_str) if args_str else 0
                return int(arg_val)
            elif func_name == 'girdi':
                return input()
            
            # Kullanıcı tanımlı fonksiyon
            if func_name in self.functions:
                if args_str:
                    args = []
                    current_arg = ""
                    paren_depth = 0
                    for char in args_str:
                        if char == '(' : paren_depth += 1
                        elif char == ')': paren_depth -= 1
                        elif char == ',' and paren_depth == 0:
                            args.append(self.evaluate(current_arg.strip()))
                            current_arg = ""
                            continue
                        current_arg += char
                    if current_arg.strip():
                        args.append(self.evaluate(current_arg.strip()))
                else:
                    args = []
                
                return self.call_function(func_name, args)

        # Değişken
        if expr in self.variables:
            return self.variables[expr]

        # Karmaşık ifade
        return self.evaluate_expression(expr)

    def evaluate_expression(self, expr):
        safe_dict = self.variables.copy()
        
        # Native fonksiyonlar
        safe_dict['metin'] = str
        safe_dict['sayı'] = int
        safe_dict['karekok'] = math.sqrt
        safe_dict['rastgele'] = random.random
        safe_dict['zaman'] = time.time
        safe_dict['girdi'] = input
        
        # Türkçe anahtar kelimeler
        safe_dict['doğru'] = True
        safe_dict['yanlış'] = False
        
        # Kullanıcı tanımlı fonksiyonları ekle
        def make_func_wrapper(fn_name):
            def wrapper(*args):
                return self.call_function(fn_name, list(args))
            return wrapper
        
        for func_name in self.functions:
            safe_dict[func_name] = make_func_wrapper(func_name)
        
        try:
            # Türkçe operatör dönüşümleri (Basit)
            expr = expr.replace(' ve ', ' and ').replace(' veya ', ' or ').replace(' değil ', ' not ')
            
            result = eval(expr, {"__builtins__": None, "input": input}, safe_dict)
            return result
        except Exception as e:
            if expr.startswith('"') and expr.endswith('"'):
                return expr.strip('"')
            return f"<{expr}>"


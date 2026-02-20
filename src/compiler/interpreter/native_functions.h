#ifndef NATIVE_FUNCTIONS_H
#define NATIVE_FUNCTIONS_H

// İleri bildirim (Interpreter sınıfını kullanacağız ama header'ı burada include etmemize gerek yok)
class Interpreter;

/**
 * Tüm yerel (native) fonksiyonları interpreter örneğine kaydeder.
 */
void registerNativeFunctions(Interpreter& interpreter);

#endif

import struct
import os

def read_utf8_long(f, offset):
    pos = f.tell()
    f.seek(offset)
    res = b""
    while True:
        c = f.read(1)
        if not c or c == b'\0': break
        res += c
    f.seek(pos)
    return res.decode('utf-8', errors='ignore')

def analyze_pe(path):
    print(f"Analyzing: {path}")
    with open(path, 'rb') as f:
        if f.read(2) != b'MZ': return "Not MZ"
        f.seek(0x3c)
        pe_ptr = struct.unpack('<I', f.read(4))[0]
        f.seek(pe_ptr)
        if f.read(4) != b'PE\0\0': return "Not PE"
        
        # File Header
        machine = struct.unpack('<H', f.read(2))[0]
        num_sections = struct.unpack('<H', f.read(2))[0]
        f.seek(12, 1)
        opt_hdr_size = struct.unpack('<H', f.read(2))[0]
        f.seek(2, 1)
        
        # Optional Header
        magic = struct.unpack('<H', f.read(2))[0]
        is_64 = (magic == 0x20B)
        
        # Find Data Directories (Import is at index 1, skip Export at index 0 (8 bytes))
        if is_64:
            f.seek(pe_ptr + 24 + 112 + 8) # DataDirs start at 112
        else:
            f.seek(pe_ptr + 24 + 96 + 8) # DataDirs start at 96
            
        import_va = struct.unpack('<I', f.read(4))[0]
        import_size = struct.unpack('<I', f.read(4))[0]
        
        print(f"Import VA: {hex(import_va)}, Size: {hex(import_size)}")
        
        # Sections
        f.seek(pe_ptr + 24 + opt_hdr_size)
        sections = []
        for _ in range(num_sections):
            name = f.read(8).decode('utf-8', errors='ignore').strip('\0')
            vsize, vaddr, psize, paddr = struct.unpack('<IIII', f.read(16))
            f.seek(16, 1)
            sections.append({'name': name, 'va': vaddr, 'vs': vsize, 'pa': paddr})
            
        def rva_to_off(rva):
            for s in sections:
                if s['va'] <= rva < s['va'] + s['vs']:
                    return rva - s['va'] + s['pa']
            return None

        import_off = rva_to_off(import_va)
        if import_off is None:
             print("No import directory or not mapped.")
             return

        f.seek(import_off)
        print("\nDependencies:")
        while True:
            # IMAGE_IMPORT_DESCRIPTOR
            orig_first_thunk = struct.unpack('<I', f.read(4))[0]
            f.seek(4, 1) # TimeDateStamp
            f.seek(4, 1) # ForwarderChain
            name_rva = struct.unpack('<I', f.read(4))[0]
            first_thunk = struct.unpack('<I', f.read(4))[0]
            
            if name_rva == 0: break
            
            dll_name = read_utf8_long(f, rva_to_off(name_rva))
            print(f" - {dll_name}")
            
            # Follow FirstThunk to see if we can find missing entry points?
            # Too complex without symbol table.

if __name__ == "__main__":
    analyze_pe("bin/gumus.exe")

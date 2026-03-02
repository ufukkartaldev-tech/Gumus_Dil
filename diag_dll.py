import struct
import os

def check_dlls(exe_path):
    print(f"Checking dependencies for: {exe_path}")
    if not os.path.exists(exe_path):
        print("File not found!")
        return

    with open(exe_path, 'rb') as f:
        # Check MZ header
        if f.read(2) != b'MZ':
            print("Not a valid PE file (no MZ header)")
            return
        
        # Get PE header offset
        f.seek(0x3C)
        pe_offset = struct.unpack('<I', f.read(4))[0]
        
        # Check PE header
        f.seek(pe_offset)
        if f.read(4) != b'PE\0\0':
            print("Not a valid PE file (no PE header)")
            return
        
        # File header
        f.seek(pe_offset + 4 + 16)
        optional_header_size = struct.unpack('<H', f.read(2))[0]
        
        # Optional header (Magic)
        f.seek(pe_offset + 4 + 20)
        magic = struct.unpack('<H', f.read(2))[0]
        
        if magic == 0x10B: # PE32
            data_dir_offset = pe_offset + 4 + 20 + 96
        elif magic == 0x20B: # PE32+ (64-bit)
            data_dir_offset = pe_offset + 4 + 20 + 112
        else:
            print(f"Unknown magic: {hex(magic)}")
            return
            
        # Import Data Directory
        f.seek(data_dir_offset)
        import_va = struct.unpack('<I', f.read(4))[0]
        import_size = struct.unpack('<I', f.read(4))[0]
        
        if import_va == 0:
            print("No imports found.")
            return

        # Find section containing the Import Directory VA
        f.seek(pe_offset + 4 + 20 + optional_header_size)
        num_sections = struct.unpack('<H', struct.read_at(f, pe_offset + 4 + 2, 2))[0] # bit hacky
        
        # Let's just find the section
        sections = []
        for i in range(num_sections):
            name = f.read(8).decode('utf-8', errors='ignore').strip('\0')
            vsize = struct.unpack('<I', f.read(4))[0]
            vaddr = struct.unpack('<I', f.read(4))[0]
            psize = struct.unpack('<I', f.read(4))[0]
            paddr = struct.unpack('<I', f.read(4))[0]
            f.seek(12, os.SEEK_CUR) # skip other fields
            sections.append({'name': name, 'vaddr': vaddr, 'vsize': vsize, 'paddr': paddr})

        def va_to_offset(va):
            for s in sections:
                if s['vaddr'] <= va < s['vaddr'] + s['vsize']:
                    return va - s['vaddr'] + s['paddr']
            return None

        import_offset = va_to_offset(import_va)
        if import_offset is None:
            print("Could not map Import VA to file offset.")
            return

        f.seek(import_offset)
        dll_names = []
        while True:
            # IMAGE_IMPORT_DESCRIPTOR (20 bytes)
            # OriginalFirstThunk (4), TimeDateStamp (4), ForwarderChain (4), Name (4), FirstThunk (4)
            f.seek(12, os.SEEK_CUR)
            name_va = struct.unpack('<I', f.read(4))[0]
            f.seek(4, os.SEEK_CUR)
            
            if name_va == 0:
                break
            
            current_pos = f.tell()
            name_offset = va_to_offset(name_va)
            if name_offset:
                f.seek(name_offset)
                name = b""
                while True:
                    char = f.read(1)
                    if char == b'\0' or not char: break
                    name += char
                dll_names.append(name.decode('utf-8'))
            f.seek(current_pos)

        print("\nRequired DLLs:")
        for dll in dll_names:
            exists = any(os.path.exists(os.path.join(d, dll)) for d in [os.path.dirname(exe_path), "C:\\Windows\\System32"])
            status = "✅ Found" if exists else "❌ MISSING"
            print(f" - {dll:25} {status}")

def struct_read_at(f, offset, size):
    pos = f.tell()
    f.seek(offset)
    res = f.read(size)
    f.seek(pos)
    return res

if __name__ == "__main__":
    import sys
    # Monkey patch for the helper
    struct.read_at = struct_read_at
    check_dlls("bin/gumus.exe")

import os
import shutil
import time

dest_base = r"G:\Mi unidad\RESPALDO_LAPTOP"
os.makedirs(dest_base, exist_ok=True)

# 1. Carpetas y archivos de documentos directos
direct_items = [
    r"D:\TP -2026",
    r"D:\NOS PLANET SAC",
    r"D:\ChaskiProduc",
    r"D:\Tareo_Plantillas",
    r"D:\firmas",
    r"D:\CURSOS DE ESTUDIOS",
    r"D:\github recovery",
    r"D:\fotos randoms",
    r"D:\_Marca Relatia",
    r"D:\PAGOS- NOS PLANET.xlsx"
]

total_files_copied = 0
total_bytes_copied = 0

print("=== INICIANDO RESPALDO HACIA GOOGLE DRIVE (5 TB) ===")
start_time = time.time()

for item in direct_items:
    if not os.path.exists(item):
        print(f"Omitido (no existe): {item}")
        continue
    
    name = os.path.basename(item)
    dest_path = os.path.join(dest_base, name)
    
    if os.path.isfile(item):
        try:
            shutil.copy2(item, dest_path)
            s = os.path.getsize(item)
            total_files_copied += 1
            total_bytes_copied += s
            print(f"[OK Archivo] {name} ({round(s/(1024*1024), 2)} MB)")
        except Exception as e:
            print(f"[Error] {name}: {e}")
    elif os.path.isdir(item):
        print(f"Copiando carpeta: {name} ...")
        count = 0
        b_count = 0
        try:
            for root, dirs, files in os.walk(item):
                rel = os.path.relpath(root, item)
                target_dir = os.path.join(dest_path, rel)
                os.makedirs(target_dir, exist_ok=True)
                
                for f in files:
                    s_file = os.path.join(root, f)
                    d_file = os.path.join(target_dir, f)
                    try:
                        shutil.copy2(s_file, d_file)
                        sz = os.path.getsize(s_file)
                        b_count += sz
                        count += 1
                    except Exception as fe:
                        pass
            total_files_copied += count
            total_bytes_copied += b_count
            print(f"[OK Carpeta] {name}: {count} archivos ({round(b_count/(1024*1024), 2)} MB)")
        except Exception as e:
            print(f"[Error en carpeta] {name}: {e}")

# 2. Respaldo de D:\PROYECTOS (Solo codigo fuente, EXCLUYENDO node_modules y .git pesados)
proyectos_src = r"D:\PROYECTOS"
if os.path.exists(proyectos_src):
    print("\nCopiando codigo fuente de D:\PROYECTOS (sin node_modules)...")
    dest_proyectos = os.path.join(dest_base, "PROYECTOS")
    os.makedirs(dest_proyectos, exist_ok=True)
    
    p_files = 0
    p_bytes = 0
    ignore_dirs = {"node_modules", ".pnpm-store", ".git", "dist", "build", ".next", ".cache", "temp"}
    
    for root, dirs, files in os.walk(proyectos_src):
        # Filtrar carpetas ignoradas in-place
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        rel = os.path.relpath(root, proyectos_src)
        target_dir = os.path.join(dest_proyectos, rel)
        os.makedirs(target_dir, exist_ok=True)
        
        for f in files:
            # ignorar temporales o locks gigantes si los hay
            if f.endswith((".log", ".tmp")):
                continue
            sf = os.path.join(root, f)
            df = os.path.join(target_dir, f)
            try:
                shutil.copy2(sf, df)
                sz = os.path.getsize(sf)
                p_bytes += sz
                p_files += 1
            except Exception:
                pass
                
    total_files_copied += p_files
    total_bytes_copied += p_bytes
    print(f"[OK Proyectos] Codigo fuente respaldado: {p_files} archivos ({round(p_bytes/(1024*1024), 2)} MB)")

duration = round(time.time() - start_time, 2)
print("\n" + "="*60)
print("              RESPALDO COMPLETADO CON EXITO")
print("="*60)
print(f"Destino en Google Drive : {dest_base}")
print(f"Total de archivos      : {total_files_copied}")
print(f"Tamano total respaldado: {round(total_bytes_copied/(1024*1024), 2)} MB ({round(total_bytes_copied/(1024**3), 2)} GB)")
print(f"Tiempo transcurrido    : {duration} segundos")
print("="*60)


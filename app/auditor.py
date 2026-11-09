import os
import platform
import time
import winreg
import psutil
from app.utils import format_size

_CACHED_CPU_NAME = None
_CACHED_GPUS = None

def get_cpu_info():
    """Obtiene el nombre y especificaciones detalladas del procesador sin lentitud."""
    global _CACHED_CPU_NAME
    
    if not _CACHED_CPU_NAME:
        # 1. Leer directamente del Registro de Windows (ultra rápido: <0.001s)
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as k:
                val, _ = winreg.QueryValueEx(k, "ProcessorNameString")
                if val and str(val).strip():
                    _CACHED_CPU_NAME = str(val).strip()
        except Exception:
            pass

        if not _CACHED_CPU_NAME:
            _CACHED_CPU_NAME = platform.processor() or "Procesador x64"

    freq = psutil.cpu_freq()
    return {
        "name": _CACHED_CPU_NAME,
        "physical_cores": psutil.cpu_count(logical=False),
        "total_cores": psutil.cpu_count(logical=True),
        "current_frequency_mhz": round(freq.current, 1) if freq else None,
        "usage_percent": psutil.cpu_percent(interval=None) # interval=None es instantáneo
    }

def get_gpu_info():
    """Obtiene tarjetas gráficas directamente del Registro (ultra rápido: <0.001s)."""
    global _CACHED_GPUS
    if _CACHED_GPUS is not None:
        return _CACHED_GPUS

    gpus = []
    # Clave estándar de adaptadores de pantalla en Windows
    key_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as k:
            num_subkeys = winreg.QueryInfoKey(k)[0]
            for i in range(num_subkeys):
                subk_name = winreg.EnumKey(k, i)
                if subk_name.isdigit():
                    try:
                        with winreg.OpenKey(k, subk_name) as dev:
                            desc, _ = winreg.QueryValueEx(dev, "DriverDesc")
                            driver_ver = "N/D"
                            try:
                                driver_ver, _ = winreg.QueryValueEx(dev, "DriverVersion")
                            except OSError:
                                pass
                            
                            gpus.append({
                                "name": str(desc).strip(),
                                "vram": "Memoria compartida / Dedicada",
                                "driver_version": str(driver_ver).strip(),
                                "processor": str(desc).strip()
                            })
                    except OSError:
                        continue
    except Exception:
        pass

    if not gpus:
        gpus.append({
            "name": "Adaptador de pantalla de Windows",
            "vram": "N/D",
            "driver_version": "N/D",
            "processor": "Gráficos Integrados"
        })

    _CACHED_GPUS = gpus
    return _CACHED_GPUS

def get_system_overview():
    """Genera la auditoría de especificaciones del sistema al instante."""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    drives = []
    for part in psutil.disk_partitions(all=False):
        if 'cdrom' in part.opts or part.fstype == '':
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            drives.append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total_bytes": usage.total,
                "used_bytes": usage.used,
                "free_bytes": usage.free,
                "total_formatted": format_size(usage.total),
                "used_formatted": format_size(usage.used),
                "free_formatted": format_size(usage.free),
                "percent_used": usage.percent
            })
        except Exception:
            continue

    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    uptime_str = f"{days}d {hours}h {minutes}m" if days > 0 else f"{hours}h {minutes}m"

    battery_info = None
    if hasattr(psutil, "sensors_battery"):
        try:
            bat = psutil.sensors_battery()
            if bat:
                battery_info = {
                    "percent": bat.percent,
                    "power_plugged": bat.power_plugged,
                    "time_left_min": round(bat.secsleft / 60) if bat.secsleft and bat.secsleft > 0 else None
                }
        except Exception:
            pass

    return {
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.architecture()[0],
            "hostname": platform.node(),
            "user": os.environ.get('USERNAME', 'Usuario'),
            "uptime": uptime_str,
            "boot_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(boot_time))
        },
        "cpu": get_cpu_info(),
        "ram": {
            "total_bytes": mem.total,
            "used_bytes": mem.used,
            "free_bytes": mem.available,
            "total_formatted": format_size(mem.total),
            "used_formatted": format_size(mem.used),
            "free_formatted": format_size(mem.available),
            "percent_used": mem.percent
        },
        "swap": {
            "total_formatted": format_size(swap.total),
            "used_formatted": format_size(swap.used),
            "percent_used": swap.percent
        },
        "gpus": get_gpu_info(),
        "drives": drives,
        "battery": battery_info
    }

def get_top_processes(limit=10):
    """Obtiene los procesos más demandantes en memoria y CPU."""
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
        try:
            info = p.info
            mem_rss = info['memory_info'].rss if info['memory_info'] else 0
            procs.append({
                "pid": info['pid'],
                "name": info['name'],
                "cpu_percent": info['cpu_percent'] or 0.0,
                "memory_percent": round(info['memory_percent'] or 0.0, 1),
                "memory_bytes": mem_rss,
                "memory_formatted": format_size(mem_rss)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    by_mem = sorted(procs, key=lambda x: x['memory_bytes'], reverse=True)[:limit]
    by_cpu = sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:limit]

    return {
        "by_memory": by_mem,
        "by_cpu": by_cpu
    }

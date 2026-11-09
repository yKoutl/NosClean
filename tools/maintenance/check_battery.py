import subprocess
import os
import re

subprocess.run(['powercfg', '/batteryreport', '/output', 'battery_report.html'], capture_output=True, text=True)

if os.path.exists('battery_report.html'):
    with open('battery_report.html', 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
        
    for m in re.finditer(r'(DESIGN CAPACITY|FULL CHARGE CAPACITY|CYCLE COUNT)[^<]*</td>\s*<td[^>]*>([^<]+)</td>', html, re.I):
        print(m.group(1), ':', m.group(2).strip())
        
    print('\nRecent battery events:')
    # Find table with recent usage
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
    for r in rows:
        if '2026-11' in r and ('Suspended' in r or 'Active' in r or 'Battery' in r or 'Shutdown' in r or 'AC' in r):
            clean = re.sub(r'<[^>]+>', ' | ', r)
            clean = ' '.join(clean.split())
            print(' ', clean)

if os.path.exists('battery_report.html'):
    os.remove('battery_report.html')


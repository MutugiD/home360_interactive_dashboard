import os
import shutil
import subprocess
from pathlib import Path

def setup_adminlte():
    # Define paths
    base_dir = Path(__file__).parent.parent.parent
    webapp_dir = base_dir / 'webapp'
    adminlte_dir = webapp_dir / 'AdminLTE'

    # Create webapp directory if it doesn't exist
    webapp_dir.mkdir(exist_ok=True)

    # Clone AdminLTE if not already present
    if not adminlte_dir.exists():
        print("Cloning AdminLTE...")
        subprocess.run(['git', 'clone', 'https://github.com/ColorlibHQ/AdminLTE.git', str(adminlte_dir)])

    # Create necessary directories
    static_dir = webapp_dir / 'static'
    css_dir = static_dir / 'css'
    js_dir = static_dir / 'js'
    vendors_dir = static_dir / 'vendors'

    for dir_path in [static_dir, css_dir, js_dir, vendors_dir]:
        dir_path.mkdir(exist_ok=True)

    # Copy required files from AdminLTE
    print("Copying required files...")

    # Copy CSS files
    shutil.copy2(adminlte_dir / 'dist' / 'css' / 'adminlte.min.css', css_dir)

    # Copy JS files
    shutil.copy2(adminlte_dir / 'dist' / 'js' / 'adminlte.min.js', js_dir)

    # Copy vendor files
    vendor_files = [
        ('bootstrap', 'dist/js/bootstrap.bundle.min.js'),
        ('jquery', 'dist/jquery.min.js'),
        ('chart.js', 'Chart.min.js')
    ]

    for vendor, file_path in vendor_files:
        vendor_dir = vendors_dir / vendor
        vendor_dir.mkdir(exist_ok=True)
        if vendor == 'chart.js':
            shutil.copy2(adminlte_dir / 'plugins' / 'chart.js' / file_path, vendor_dir)
        else:
            shutil.copy2(adminlte_dir / 'plugins' / vendor / file_path, vendor_dir)

    print("AdminLTE setup completed successfully!")

if __name__ == "__main__":
    setup_adminlte()
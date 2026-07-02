# PyInstaller build spec for BioSUR.
# Cross-platform (Windows / macOS / Linux). Build with:
#   pyinstaller BioSUR.spec --noconfirm
#
# Using a .spec file (instead of command-line flags) avoids the platform
# differences in --add-data path separators and lets us pull in customtkinter's
# bundled theme/asset files, which PyInstaller does not detect automatically.
import sys

from PyInstaller.utils.hooks import collect_all, collect_submodules

# Application resources referenced at runtime via GUI.main_GUI.resource_path.
datas = [
    ("GUI/logo-creck.ico", "GUI"),
    ("GUI/logo-creck.png", "GUI"),
]
binaries = []
hiddenimports = ["matplotlib.backends.backend_tkagg"]

# Explicitly collect every submodule of the app packages so none are missed by
# the dependency analysis (the BioSUR package shares its name with the
# BioSUR.BioSUR module, which can confuse module resolution).
hiddenimports += collect_submodules("BioSUR")
hiddenimports += collect_submodules("GUI")

# customtkinter ships JSON themes and image assets that must be bundled.
for _pkg in ("customtkinter",):
    _d, _b, _h = collect_all(_pkg)
    datas += _d
    binaries += _b
    hiddenimports += _h

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

# Windows can embed the .ico directly; macOS needs .icns (which we don't ship),
# so the runtime iconphoto() call handles the icon there instead.
_icon = "GUI/logo-creck.ico" if sys.platform.startswith("win") else None

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="BioSUR",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,          # windowed app, no terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon,
)

# On macOS, wrap the executable in a proper .app bundle so it launches from
# Finder/Launchpad like a normal application.
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="BioSUR.app",
        icon=None,
        bundle_identifier="org.creck.biosur",
    )

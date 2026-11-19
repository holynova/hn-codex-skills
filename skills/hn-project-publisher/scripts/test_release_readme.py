"""Regression cases for bilingual release README validation (no network)."""
import subprocess
import tempfile
from pathlib import Path

validator = Path(__file__).with_name('validate_release_readme.mjs')
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / 'assets').mkdir()
    for name in ['screenshot.png', 'qr.png', 'hero.svg']:
        (root / 'assets' / name).write_text('fixture; visual validity checked separately')
    common = '\n[Repo](https://github.com/test/demo)\n[Demo](https://demo.example)\n![Screenshot](assets/screenshot.png)\n![QR](assets/qr.png)\n'
    en = 'This application displays your local photographs.\n[简体中文](README.zh-CN.md)\n' + common
    zh = '这个应用展示本地照片。\n[English](README.md)\n' + common
    def run(name, main=en, other=zh, pair=True, flags=(), expected=True):
        (root / 'README.md').write_text(main)
        (root / 'README.zh-CN.md').write_text(other)
        args = ['node', str(validator), str(root / 'README.md'), 'https://github.com/test/demo', 'https://demo.example']
        if pair:
            args += ['--companion', str(root / 'README.zh-CN.md')]
        result = subprocess.run(args + list(flags), capture_output=True, text=True)
        assert (result.returncode == 0) == expected, name + '\n' + result.stdout + result.stderr
        print('PASS:', name)
    run('bilingual pair')
    run('single bilingual', main=en + '\n这个应用展示本地照片。', pair=False)
    run('missing Chinese despite language switch', pair=False, expected=False)
    run('missing backlink', other=zh.replace('[English](README.md)', ''), expected=False)
    run('missing companion demo', other=zh.replace('[Demo](https://demo.example)', ''), expected=False)
    run('hero is not screenshot', main=en.replace('![Screenshot](assets/screenshot.png)', '![Hero](assets/hero.svg)'), expected=False)
    run('explicit screenshot', flags=('--screenshot', str(root / 'assets/screenshot.png')))
    run('wrong explicit screenshot', flags=('--screenshot', str(root / 'assets/missing.png')), expected=False)
    long = en + '\n' + 'Long documentation remains useful. ' * 160
    run('strict length', main=long, expected=False)
    run('preserve existing long document', main=long, flags=('--preserve-length',))
    run('empty translation', other='[English](README.md)\n' + common, expected=False)
    (root / 'assets/qr.png').unlink()
    run('missing QR file', expected=False)

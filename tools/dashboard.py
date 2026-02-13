#!/usr/bin/env python3
"""Serve a simulation output directory with an auto-generated dashboard.

Generates a simple index.html listing PNG frames and an audio player for
`ping.wav`, then starts a static HTTP server serving that directory.
"""
from __future__ import annotations
import argparse
import http.server
import socketserver
import os
from pathlib import Path


TEMPLATE = """<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="5">
    <title>Sonar Simulator Output</title>
    <style>
        body{{font-family: Arial, sans-serif; margin: 1rem}}
        .frame{{max-width: 33vw; margin: .5rem}}
        img{{width:100%; height:auto; display:block}}
        button{{margin-right:.5rem}}
    </style>
</head>
<body>
    <h1>Sonar Simulator Output: {outdir}</h1>
    {audio}
    <h2>Frames</h2>
    <div>
    {frames}
    </div>
    <script src="dashboard.js"></script>
</body>
</html>
"""


def make_index(outdir: Path) -> None:
    pngs = sorted([p.name for p in outdir.iterdir() if p.suffix.lower() in ('.png', '.jpg')])
    audio = None
    if (outdir / 'ping.wav').exists():
        audio = '<audio controls src="ping.wav">Your browser does not support audio</audio>'
    else:
        audio = '<p><em>No ping.wav found.</em></p>'

    frames_html = ''
    for p in pngs:
        frames_html += f'<div class="frame"><img src="{p}" alt="{p}"><div>{p}</div></div>\n'

    html = TEMPLATE.format(outdir=outdir.name, audio=audio, frames=frames_html)
    with open(outdir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    # copy static JS into outdir so the index can load it
    try:
        src = Path(__file__).parent / 'static' / 'dashboard.js'
        dst = outdir / 'dashboard.js'
        with open(src, 'rb') as s, open(dst, 'wb') as d:
            d.write(s.read())
    except Exception:
        pass


def serve(outdir: Path, port: int = 8000) -> None:
    os.chdir(outdir)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(('', port), handler) as httpd:
        print(f"Serving {outdir} at http://localhost:{port}/index.html")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nShutting down')


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--outdir', '-o', type=Path, default=Path('sim_outputs'))
    p.add_argument('--port', type=int, default=8000)
    args = p.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    make_index(args.outdir)
    serve(args.outdir, args.port)


if __name__ == '__main__':
    main()

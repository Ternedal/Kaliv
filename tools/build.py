"""Stage the public GitHub Pages files using only the Python standard library."""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "_site"
PUBLIC_FILES = (
    ".nojekyll", "CNAME", "index.html", "brief.html", "hub.html",
    "proofs.html", "architecture.html", "progress.html", "404.html",
    "offline.html", "home.css", "home.js", "dossier.css", "dossier.js",
    "site-shell.css", "project.json", "llms.txt", "robots.txt", "sitemap.xml",
    "site.webmanifest", "service-worker.js",
    "assets/kaliv-favicon-32.png", "assets/kaliv-apple-touch-icon.png",
    "assets/kaliv-icon-192.png", "assets/kaliv-icon-512.png",
    "assets/kaliv-icon-maskable-512.png", "assets/kaliv-ankh-160.webp",
    "assets/kaliv-ankh-640.webp",
    "assets/modelrig-continuity-female-hair-mobile.webp",
    "assets/modelrig-continuity-female-hair-1920.webp",
    "assets/modelrig-continuity-female-hair-hires.webp",
)


def main():
    # Validate inputs before replacing the last successfully staged site.
    for name in PUBLIC_FILES:
        if not (ROOT / name).is_file():
            raise FileNotFoundError(f"Missing public file: {name}")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    for name in PUBLIC_FILES:
        target = OUTPUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    print(f"Staged {len(PUBLIC_FILES)} public files in {OUTPUT.name}/")


if __name__ == "__main__":
    main()

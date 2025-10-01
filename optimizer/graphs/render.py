import pathlib, shutil, subprocess

DOCS = pathlib.Path("docs/graphs")

def main():
    dot = shutil.which("mmdc") or shutil.which("mermaid")
    if not dot:
        print("Mermaid CLI not found; keeping .mmd only.")
        return
    for mmd in DOCS.glob("*.mmd"):
        png = mmd.with_suffix(".png")
        try:
            subprocess.check_call([dot, "-i", str(mmd), "-o", str(png)])
            print(f"Rendered {png.name}")
        except Exception:
            print(f"Render failed for {mmd.name}; leaving .mmd.")

if __name__ == "__main__":
    main()
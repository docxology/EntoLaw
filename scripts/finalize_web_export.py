#!/usr/bin/env python3
from __future__ import annotations

import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def ensure_web_figure_link(project_root: Path = PROJECT_ROOT) -> Path:
    figures_dir = project_root / "output" / "figures"
    web_dir = project_root / "output" / "web"
    web_figures = web_dir / "figures"

    if not figures_dir.exists():
        raise FileNotFoundError(f"missing figure output directory: {figures_dir}")
    web_dir.mkdir(parents=True, exist_ok=True)

    if web_figures.is_symlink():
        if web_figures.resolve() == figures_dir.resolve():
            return web_figures
        web_figures.unlink()
    elif web_figures.exists():
        if web_figures.is_dir():
            shutil.rmtree(web_figures)
        else:
            web_figures.unlink()

    try:
        web_figures.symlink_to(Path("..") / "figures", target_is_directory=True)
    except OSError:
        shutil.copytree(figures_dir, web_figures)
    return web_figures


def main() -> int:
    link = ensure_web_figure_link()
    print(link)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

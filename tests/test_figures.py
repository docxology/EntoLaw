"""Figure-rendering tests: every captioned figure plus the cover renders to PNG."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.image as mpimg  # noqa: E402

from src import figure_bundle, figure_captions  # noqa: E402


def test_renderers_cover_every_caption_and_vice_versa():
    captioned = set(figure_bundle.captioned_slugs())
    rendered = set(figure_bundle.FIGURE_RENDERERS)
    assert captioned == rendered, captioned ^ rendered
    assert "claim_ledger_coverage" in rendered


def test_build_figures_writes_all_pngs(tmp_path):
    paths = figure_bundle.build_figures(tmp_path)
    # one per caption + the cover
    assert len(paths) == len(figure_captions.all_captions()) + 1
    for p in paths:
        assert p.exists()
        assert p.suffix == ".png"
        assert p.stat().st_size > 0
    assert (tmp_path / "cover.png").exists()


def test_each_captioned_figure_file_is_named_for_its_slug(tmp_path):
    figure_bundle.build_figures(tmp_path)
    for caption in figure_captions.all_captions():
        assert (tmp_path / f"{caption.slug}.png").exists()


def test_cover_places_insect_art_in_upper_visual_fields(tmp_path):
    figure_bundle.build_figures(tmp_path)
    image = mpimg.imread(tmp_path / "cover.png")
    rgb = image[:, :, :3]
    height, width = rgb.shape[:2]
    non_background = (rgb < 0.92).any(axis=2)
    left_insect_zone = non_background[
        int(height * 0.10) : int(height * 0.42),
        int(width * 0.06) : int(width * 0.34),
    ]
    right_insect_zone = non_background[
        int(height * 0.10) : int(height * 0.42),
        int(width * 0.66) : int(width * 0.94),
    ]
    assert left_insect_zone.mean() > 0.015
    assert right_insect_zone.mean() > 0.015


def test_cover_is_landscape_width_for_pdf_title_surface(tmp_path):
    figure_bundle.build_figures(tmp_path)
    image = mpimg.imread(tmp_path / "cover.png")
    height, width = image.shape[:2]
    assert width / height >= 1.45

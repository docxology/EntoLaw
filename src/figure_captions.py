from __future__ import annotations

from string import Formatter
from typing import Iterable, Mapping

from .figure_caption_records import FIGURE_CAPTIONS, FigureCaption


class _SafeCaptionContext(dict[str, str]):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def all_captions() -> tuple[FigureCaption, ...]:
    return FIGURE_CAPTIONS


def caption_by_slug(slug: str) -> FigureCaption:
    for caption in FIGURE_CAPTIONS:
        if caption.slug == slug:
            return caption
    raise KeyError(f"unknown figure caption slug: {slug}")


def caption_by_anchor(anchor: str) -> FigureCaption:
    for caption in FIGURE_CAPTIONS:
        if caption.anchor == anchor:
            return caption
    raise KeyError(f"unknown figure caption anchor: {anchor}")


def caption_tokens(context: Mapping[str, str]) -> dict[str, str]:
    safe = _SafeCaptionContext({k: str(v) for k, v in context.items()})
    return {
        caption.token_name: caption.manuscript_caption.format_map(safe)
        for caption in FIGURE_CAPTIONS
    }


def caption_contract_errors(
    captions: Iterable[FigureCaption],
    manuscript_anchors: Iterable[str],
) -> tuple[str, ...]:
    errors: list[str] = []
    caption_list = tuple(captions)
    slugs = [c.slug for c in caption_list]
    anchors = [c.anchor for c in caption_list]
    for label, values in (("slug", slugs), ("anchor", anchors)):
        duplicates = sorted({v for v in values if values.count(v) > 1})
        errors.extend(f"duplicate {label}: {v}" for v in duplicates)
    for caption in caption_list:
        missing = [
            f
            for f in ("title", "manuscript_caption", "alt_text", "provenance", "caveat")
            if not getattr(caption, f).strip()
        ]
        errors.extend(f"{caption.slug} missing {f}" for f in missing)
    caption_anchors = set(anchors)
    figure_anchors = set(manuscript_anchors)
    errors.extend(
        f"missing caption for {a}" for a in sorted(figure_anchors - caption_anchors)
    )
    errors.extend(
        f"caption without manuscript figure {a}"
        for a in sorted(caption_anchors - figure_anchors)
    )
    return tuple(errors)


def unresolved_caption_placeholders(tokens: Mapping[str, str]) -> tuple[str, ...]:
    formatter = Formatter()
    unresolved: list[str] = []
    for token, value in tokens.items():
        for _, field_name, _, _ in formatter.parse(value):
            if field_name:
                unresolved.append(f"{token}:{field_name}")
    return tuple(unresolved)

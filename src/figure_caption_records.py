# entolaw-size-ok: source-owned figure caption registry records; split from facade for size gate.
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FigureCaption:
    """A reader-facing caption record for one rendered figure."""

    slug: str
    anchor: str
    title: str
    manuscript_caption: str
    alt_text: str
    provenance: str
    caveat: str

    @property
    def token_name(self) -> str:
        return f"FIGURE_CAPTION_{self.slug.upper()}"


FIGURE_CAPTIONS: tuple[FigureCaption, ...] = (
    FigureCaption(
        slug="roles_overview",
        anchor="fig:roles_overview",
        title="Registered legal roles of the insect",
        manuscript_caption=(
            "The {ROLE_COUNT} registered legal roles an insect can occupy in "
            "this release, with the case, statute, species, and milestone "
            "evidence encoded for each. Read "
            "as: the field is not one doctrine but a set of recurring legal "
            "positions that biology can trigger. Why it matters: the figure "
            "sets the manuscript's organizing grammar before the doctrinal "
            "sections specialize it. Provenance: `src/roles.py` "
            "and `src.metrics.role_coverage_matrix()`. Caveat: counts describe "
            "the encoded registries, not the entirety of each legal sub-field."
        ),
        alt_text=(
            "Grouped bar chart of registered legal roles, each showing counts of "
            "cases, statutes, species, and milestones."
        ),
        provenance="Generated from `src/roles.py` through `src.metrics`.",
        caveat="Registry scope is explicit and narrower than the whole field.",
    ),
    FigureCaption(
        slug="timeline",
        anchor="fig:timeline",
        title="Long arc of entomological law",
        manuscript_caption=(
            "Selected milestones of entomological law across the "
            "{TIMELINE_SPAN_YEARS}-year span the registry encodes, from "
            "early bee-theft and bee-property rules to the 2026 "
            "monarch-listing suit, coloured by legal role. Read as: old "
            "evidentiary and property problems keep reappearing inside new "
            "biotechnology, welfare, and conservation disputes. Why it "
            "matters: the chronology shows recurrence rather than novelty as "
            "the field's basic pattern. Provenance: `src/timeline.py`. "
            "Caveat: a selected chronology, not a comprehensive history."
        ),
        alt_text=("Timeline scatter of milestones by year, coloured by legal role."),
        provenance="Generated from `src/timeline.py`.",
        caveat="Selected milestones only; not a complete history.",
    ),
    FigureCaption(
        slug="cases_by_role",
        anchor="fig:cases_by_role",
        title="Registered cases by legal role",
        manuscript_caption=(
            "The {CASE_COUNT} registered decisions grouped by the legal role of "
            "the insect; {ROLES_WITH_CASE_LAW} of {ROLE_COUNT} roles carry "
            "modern reporter case law, while the defendant, welfare, and weapon "
            "roles are history- and statute-driven. Read as: litigation is "
            "concentrated where insects enter court as evidence, property, or "
            "regulated biological facts. Why it matters: it separates "
            "litigated doctrine from roles that are legally important but less "
            "case-law dense. Provenance: `src/cases.py` via `src.metrics`. "
            "Caveat: only citation-parseable decisions are "
            "encoded here."
        ),
        alt_text="Bar chart of case counts per legal role.",
        provenance="Generated from `src/cases.py` through `src.metrics`.",
        caveat="History-driven roles intentionally show zero modern cases.",
    ),
    FigureCaption(
        slug="cases_by_jurisdiction",
        anchor="fig:cases_by_jurisdiction",
        title="Registered cases by jurisdiction",
        manuscript_caption=(
            "The registered case law by issuing court system, spanning the U.S. "
            "Supreme Court, federal appellate and state courts, England & Wales, "
            "Canada, and the U.S. patent system. Read as: the field is "
            "jurisdictionally scattered, so doctrine develops through examples "
            "rather than a single appellate line. Why it matters: the field "
            "has to be assembled comparatively, not read from one reporter "
            "series. Provenance: `src/cases.py`. Caveat: a curated leading-case "
            "set, not a census of all decisions."
        ),
        alt_text="Bar chart of case counts per jurisdiction.",
        provenance="Generated from `src/cases.py`.",
        caveat="Curated leading cases; not exhaustive.",
    ),
    FigureCaption(
        slug="statutes_by_category",
        anchor="fig:statutes_by_category",
        title="Statutes and treaties by category",
        manuscript_caption=(
            "The {STATUTE_COUNT} registered instruments grouped across "
            "{CATEGORY_COUNT} structural categories — forensic, quarantine, "
            "conservation, property, biotech/IP, food, welfare, public-health, "
            "and warfare. Read as: regulation follows the legal problem insects "
            "pose, not insect taxonomy itself. Why it matters: it shows why "
            "the same organism can move between food, biosecurity, conservation, "
            "and weapons law. Provenance: `src/statutes.py` via `src.metrics`. "
            "Caveat: a representative backbone, not every instrument in each category."
        ),
        alt_text="Bar chart of statute counts per category.",
        provenance="Generated from `src/statutes.py` through `src.metrics`.",
        caveat="Representative instruments, not an exhaustive code.",
    ),
    FigureCaption(
        slug="statutes_by_jurisdiction",
        anchor="fig:statutes_by_jurisdiction",
        title="Statutes and treaties by jurisdiction",
        manuscript_caption=(
            "The same {STATUTE_COUNT} instruments partitioned by issuing "
            "jurisdiction — US-federal, US-state, US-colonial, UK, India, "
            "Muscovy, Russian Empire, USSR, EU, and international — "
            "showing the field's multi-level legal architecture. Read as: "
            "insect law is built through stacked authority, with local movement "
            "rules, national statutes, and international instruments all "
            "operating at once. Why it matters: no single legal layer owns the "
            "field's risk decisions. Provenance: `src/statutes.py`. Caveat: "
            "jurisdiction is the issuing level, not a measure of reach or enforcement."
        ),
        alt_text="Bar chart of statute counts per jurisdiction.",
        provenance="Generated from `src/statutes.py`.",
        caveat="Issuing level only; not a measure of effect.",
    ),
    FigureCaption(
        slug="species_by_role",
        anchor="fig:species_by_role",
        title="Insect taxa by legal role",
        manuscript_caption=(
            "The {SPECIES_COUNT} registered taxa grouped by the legal role they "
            "illustrate, from forensic blow flies to quarantined pests, listed "
            "species, owned honey bees, engineered and edible insects, the trial "
            "weevils, and a weaponized flea. Read as: the same biological class "
            "can become evidence, asset, enemy, product, or rights candidate "
            "depending on legal context. Why it matters: legal role, not "
            "species identity alone, determines which institution acts. "
            "Provenance: `src/species.py`. Caveat: an illustrative set chosen "
            "to anchor each role, not a taxonomic survey."
        ),
        alt_text="Bar chart of taxa counts per legal role.",
        provenance="Generated from `src/species.py`.",
        caveat="Illustrative taxa, not a taxonomic census.",
    ),
    FigureCaption(
        slug="role_interconnections",
        anchor="fig:role_interconnections",
        title="How the roles interconnect",
        manuscript_caption=(
            "Network of the {INTERCONNECTION_COUNT} recurring themes that link "
            "the legal roles — the definitional problem, the expert-testimony "
            "bridge, the biotechnology pivot, the property/conservation mirror, "
            "and the ancient/modern rhyme. Edge bundles share a theme colour. "
            "Read as: category changes, not species names, are what move a "
            "dispute from one legal regime into another. Provenance: "
            "`src/interconnections.py`. Why it matters: the synthesis depends "
            "on transfers among categories rather than parallel lists of topics. "
            "Caveat: the graph encodes declared thematic links, not statistical association."
        ),
        alt_text=(
            "Network diagram of registered roles connected by interconnection themes."
        ),
        provenance="Generated from `src/interconnections.py`.",
        caveat="Declared thematic links, not measured correlation.",
    ),
    FigureCaption(
        slug="role_coverage",
        anchor="fig:role_coverage",
        title="Role-coverage matrix",
        manuscript_caption=(
            "Heatmap of how much evidence each role carries across the four "
            "registry kinds (cases, statutes, species, milestones), making the "
            "field's case-driven, statute-driven, and history-driven corners "
            "visible at a glance. Read as: a role can be legally central even "
            "when its evidence is historical or statutory rather than case-law "
            "dense. Why it matters: the figure prevents case-counts from "
            "standing in for the whole legal architecture. Provenance: "
            "`src.metrics.role_coverage_matrix()`. Caveat: cell values are "
            "registry counts, not weights of legal importance."
        ),
        alt_text=(
            "Heatmap of roles against evidence kinds (cases, statutes, species, "
            "milestones)."
        ),
        provenance="Generated from `src.metrics.role_coverage_matrix()`.",
        caveat="Counts, not importance weights.",
    ),
    FigureCaption(
        slug="claim_ledger_coverage",
        anchor="fig:claim_ledger_coverage",
        title="Claim-ledger coverage by manuscript section",
        manuscript_caption=(
            "Coverage of the {CLAIM_LEDGER_COUNT} live-checkable claim-ledger "
            "entries by declared manuscript section. Provenance: "
            "`src.claim_ledger.claim_coverage_by_anchor()`. Read as: volatile "
            "current-status and external magnitude claims are isolated where "
            "live evidence, not registry counts, carries the truth burden. Why "
            "it matters: it makes the manuscript's fact-checking boundary "
            "auditable by section. Caveat: a section with zero entries may still "
            "contain registry-derived facts or qualitative cited claims; this "
            "figure shows external/current claims that require a quote-backed "
            "verification block."
        ),
        alt_text=(
            "Bar chart of claim-ledger entries assigned to each manuscript section."
        ),
        provenance="Generated from `src.claim_ledger.claim_coverage_by_anchor()`.",
        caveat="Shows quote-backed ledger coverage, not all citations.",
    ),
    FigureCaption(
        slug="citation_dates",
        anchor="fig:citation_dates",
        title="Citation dates across the bibliography",
        manuscript_caption=(
            "Date distribution for every bibliography entry with a parseable "
            "year, split into broad bands and individual source-date strips "
            "with pre-1700 and 1700-1999 layers separated from the 2000+ "
            "consolidation, including labelled pre-1800 Rus', Muscovite, "
            "and Russian-Imperial legal/scientific sources plus pre-1950 "
            "Russian and Soviet entomology/legal sources. Read "
            "as: EntoLaw's evidence base is anchored by early legal, "
            "regulatory, and treatise sources but interpreted through modern "
            "scholarship, cases, statutes, and official materials. Why it "
            "matters: the figure makes the historical depth of the citation "
            "stack visible instead of leaving it implicit in the reference "
            "list. Provenance: `manuscript/references.bib` parsed by "
            "`src.viz_citation_dates`. Caveat: the date is the bibliography "
            "year, so modern editions appear at edition date unless the "
            "bibliography declares a source-date anchor."
        ),
        alt_text=(
            "Multi-panel chart showing citation counts by date band and every "
            "parseable source year by citation family."
        ),
        provenance="Generated from `manuscript/references.bib`.",
        caveat="Shows parseable bibliography years and declared source-date anchors.",
    ),
    FigureCaption(
        slug="architecture",
        anchor="fig:architecture",
        title="Package architecture: registries to manuscript",
        manuscript_caption=(
            "How {REGISTRY_COUNT} source-owned registries become reproducible "
            "outputs. Pure generator methods — metrics, validation, "
            "manuscript-variable generation, and figure rendering — turn "
            "registry data into inventories, reports, figures, and the "
            "rendered manuscript itself. Read as: the package treats the "
            "manuscript as a compiled artifact, not as the source of legal "
            "facts. Why it matters: readers can audit whether prose, visuals, "
            "and counts share the same inputs. Provenance: "
            "`src/package_map.py`. Caveat: a local build-pipeline "
            "description, not a deployment diagram."
        ),
        alt_text=(
            "Left-to-right pipeline diagram from registries through methods to outputs."
        ),
        provenance="Generated from `src/package_map.py`.",
        caveat="Local pipeline description, not deployment.",
    ),
)

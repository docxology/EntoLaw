# entolaw-size-ok: source-owned case registry records; split from facade for size gate.

from dataclasses import dataclass

# Controlled vocabulary for the court system a decision issued from.
JURISDICTIONS: tuple[str, ...] = (
    "U.S. Supreme Court",
    "U.S. Court of Appeals",
    "U.S. state court",
    "England & Wales",
    "Canada",
    "U.S. Patent",
)


@dataclass(frozen=True)
class Case:
    """A court decision (or issued patent) anchoring a point of doctrine.

    Attributes:
        slug: Stable identifier used for cross-references and table rows.
        name: Case name as conventionally cited.
        citation: Parseable reporter / docket / patent citation.
        year: Decision (or grant) year.
        jurisdiction: One of :data:`JURISDICTIONS`.
        role: The :mod:`src.roles` slug the decision principally concerns.
        holding: One-sentence statement of what the court held.
        significance: Why the decision matters to entomological law.
    """

    slug: str
    name: str
    citation: str
    year: int
    jurisdiction: str
    role: str
    holding: str
    significance: str


CASES: tuple[Case, ...] = (
    # ── Witness / forensic entomology ──────────────────────────────────────
    Case(
        slug="frye",
        name="Frye v. United States",
        citation="293 F. 1013",
        year=1923,
        jurisdiction="U.S. Court of Appeals",
        role="witness",
        holding="Scientific evidence is admissible only if the technique is "
        '"generally accepted" in its particular field.',
        significance="The original gatekeeping test through which insect "
        "evidence (like all scientific evidence) had to pass; still law in "
        "several states.",
    ),
    Case(
        slug="daubert",
        name="Daubert v. Merrell Dow Pharmaceuticals, Inc.",
        citation="509 U.S. 579",
        year=1993,
        jurisdiction="U.S. Supreme Court",
        role="witness",
        holding="The trial judge is a reliability gatekeeper, weighing "
        "testability, peer review, error rate, acceptance, and fit.",
        significance="The doctrinal spine of forensic-entomology admissibility; "
        "the encoded authorities frame most disputes around application of the "
        "method rather than exclusion of forensic entomology wholesale.",
    ),
    Case(
        slug="kumho_tire",
        name="Kumho Tire Co. v. Carmichael",
        citation="526 U.S. 137",
        year=1999,
        jurisdiction="U.S. Supreme Court",
        role="witness",
        holding="The Daubert reliability inquiry extends to all expert "
        "testimony, not only the conventionally scientific.",
        significance="Confirms that experience-based entomological opinion is "
        "screened under the same reliability standard as quantitative methods.",
    ),
    Case(
        slug="auker",
        name="Commonwealth v. Auker",
        citation="545 Pa. 521",
        year=1996,
        jurisdiction="U.S. state court",
        role="witness",
        holding="Entomological post-mortem-interval testimony (a 19–25 day "
        "estimate) is admissible and probative.",
        significance="A leading state-supreme-court affirmation of PMI "
        "testimony grounded in blow-fly development.",
    ),
    Case(
        slug="westerfield",
        name="People v. Westerfield",
        citation="6 Cal.5th 632",
        year=2019,
        jurisdiction="U.S. state court",
        role="witness",
        holding="A conviction stands despite a celebrated 2002 'battle of five "
        "entomologists' over the post-mortem interval.",
        significance="The field's cautionary tale: when qualified experts "
        "diverge by ten or more days, a jury may discard the entomology entirely.",
    ),
    Case(
        slug="truscott",
        name="R. v. Truscott",
        citation="2007 ONCA 575",
        year=2007,
        jurisdiction="Canada",
        role="witness",
        holding="A 1959 murder conviction is quashed as a miscarriage of justice "
        "on fresh forensic evidence — centrally the unreliability of the "
        "stomach-contents (gastric-emptying) time-of-death estimate, with "
        "supporting entomological evidence.",
        significance="Shows forensic biology, including entomology in a "
        "corroborating role, overturning a wrongful conviction decades later.",
    ),
    # ── Threat / quarantine & invasive-species law ─────────────────────────
    Case(
        slug="amazon_usda",
        name="Amazon Services LLC v. U.S. Department of Agriculture",
        citation="No. 22-1052",
        year=2024,
        jurisdiction="U.S. Court of Appeals",
        role="threat",
        holding="Secondary liability for unlawfully moving regulated pests and "
        'products requires "conscious and culpable participation," not mere '
        "fulfilment services.",
        significance="Marks the limits of secondary liability under the plant- "
        "and animal-health regime; the court vacated a $1,000,000 penalty.",
    ),
    # ── Protected subject / conservation law ───────────────────────────────
    Case(
        slug="home_builders_babbitt",
        name="National Association of Home Builders v. Babbitt",
        citation="130 F.3d 1041",
        year=1997,
        jurisdiction="U.S. Court of Appeals",
        role="protected",
        holding="Congress may protect a purely intrastate insect (the Delhi "
        "Sands flower-loving fly) under the Commerce Clause.",
        significance="The leading authority on federal power to protect insects "
        "that never cross state lines.",
    ),
    Case(
        slug="sweet_home",
        name="Babbitt v. Sweet Home Chapter of Communities for a Great Oregon",
        citation="515 U.S. 687",
        year=1995,
        jurisdiction="U.S. Supreme Court",
        role="protected",
        holding='The ESA "take" prohibition reaches significant habitat '
        "modification, not only direct killing.",
        significance="Means an endangered insect's habitat enjoys the same "
        "protection as the insect itself.",
    ),
    Case(
        slug="almond_alliance",
        name="Almond Alliance of California v. Fish & Game Commission",
        citation="79 Cal.App.5th 337",
        year=2022,
        jurisdiction="U.S. state court",
        role="protected",
        holding='Bumblebees are "fish" under Fish & Game Code § 45 because that '
        'definition includes "invertebrate," allowing CESA listing.',
        significance="The single most-cited 'insect is a fish' holding; links "
        "conservation law to the definitional question that recurs field-wide.",
    ),
    # ── Property / common law of bees and specimens ────────────────────────
    Case(
        slug="case_of_swans",
        name="The Case of Swans",
        citation="77 ER 435",
        year=1592,
        jurisdiction="England & Wales",
        role="property",
        holding="Animals ferae naturae are owned only while reduced to "
        "possession (per industriam), a doctrine later applied to bees.",
        significance="An early common-law root of the rule that bees are owned "
        "only while hived or actively pursued.",
    ),
    Case(
        slug="goff_kilts",
        name="Goff v. Kilts",
        citation="15 Wend. 550",
        year=1836,
        jurisdiction="U.S. state court",
        role="property",
        holding="A beekeeper retains a 'qualified property' in a swarm while it "
        "is kept in sight and actively pursued.",
        significance="The leading American authority on ownership of bees.",
    ),
    Case(
        slug="kearry_pattinson",
        name="Kearry v. Pattinson",
        citation="[1939] 1 KB 471",
        year=1939,
        jurisdiction="England & Wales",
        role="property",
        holding="There is no right to pursue a swarm onto a neighbour's land; "
        "ownership is lost when the bees are not followed.",
        significance="The leading modern English authority on swarm ownership.",
    ),
    Case(
        slug="ferreira_dasaro",
        name="Ferreira v. D'Asaro",
        citation="152 So. 2d 736",
        year=1963,
        jurisdiction="U.S. state court",
        role="property",
        holding="A beekeeper may be liable in negligence for sting injuries "
        "where hives are kept close to a residential property line.",
        significance="Establishes the negligence standard for keeping bees in "
        "proximity to neighbours.",
    ),
    Case(
        slug="horsch_terminex",
        name="Horsch v. Terminex International Co.",
        citation="19 Kan. App. 2d 134",
        year=1993,
        jurisdiction="U.S. state court",
        role="property",
        holding="A pest-control company can face professional liability for a "
        "negligent wood-destroying-insect inspection.",
        significance="Anchors termite/real-estate inspection liability, a high-"
        "volume civil corner of the field.",
    ),
    # ── Invention / IP, biotech & food law ─────────────────────────────────
    Case(
        slug="chakrabarty",
        name="Diamond v. Chakrabarty",
        citation="447 U.S. 303",
        year=1980,
        jurisdiction="U.S. Supreme Court",
        role="invention",
        holding="A live, human-made micro-organism is patentable subject "
        'matter — "anything under the sun that is made by man."',
        significance="The foundation for patenting engineered insect lines and "
        "their products.",
    ),
    Case(
        slug="ex_parte_allen",
        name="Ex parte Allen",
        citation="2 USPQ2d 1425",
        year=1987,
        jurisdiction="U.S. Patent",
        role="invention",
        holding="Chakrabarty extends to multicellular animals as patentable "
        "subject matter.",
        significance="Opened the door to patenting whole engineered animals, "
        "including insects.",
    ),
    Case(
        slug="oncomouse",
        name="Harvard OncoMouse",
        citation="U.S. Patent 4,736,866",
        year=1988,
        jurisdiction="U.S. Patent",
        role="invention",
        holding="A transgenic non-human mammal is a valid patented invention.",
        significance="Confirmed the patentability of engineered animals, the "
        "regime within which GM and sterile-insect lines sit.",
    ),
)

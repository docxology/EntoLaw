# entolaw-size-ok: source-owned taxon registry records; split from facade for size gate.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Taxon:
    """An insect taxon and the legal status it holds.

    Attributes:
        slug: Stable identifier.
        scientific_name: Latin binomial (or family, for the trial weevils).
        common_name: Vernacular name.
        role: The :mod:`src.roles` slug this taxon principally illustrates.
        status: Short legal-status label (e.g. ``"active quarantine"``).
        instrument: Governing instrument, forum, or program.
        note: One-sentence source-anchored note.
        year: Salient year for the status, if a single one applies.
    """

    slug: str
    scientific_name: str
    common_name: str
    role: str
    status: str
    instrument: str
    note: str
    year: int | None = None


TAXA: tuple[Taxon, ...] = (
    # ── Witness — forensic indicators ──────────────────────────────────────
    Taxon(
        slug="blow_fly_vicina",
        scientific_name="Calliphora vicina",
        common_name="blue bottle blow fly",
        role="witness",
        status="forensic indicator",
        instrument="post-mortem-interval estimation",
        note="Larvae aged at 12–14 days secured the first UK murder conviction "
        "by entomology in the Buck Ruxton case.",
        year=1935,
    ),
    Taxon(
        slug="green_bottle_fly",
        scientific_name="Lucilia sericata",
        common_name="common green bottle fly",
        role="witness",
        status="forensic indicator",
        instrument="neglect / myiasis analysis",
        note="Third-instar larvae in necrotic pressure ulcers established a "
        "pre-death neglect window in the 2025 Busan elder-neglect case.",
        year=2025,
    ),
    # ── Threat — regulated pests ───────────────────────────────────────────
    Taxon(
        slug="spotted_lanternfly",
        scientific_name="Lycorma delicatula",
        common_name="spotted lanternfly",
        role="threat",
        status="active quarantine",
        instrument="7 C.F.R. § 301.92",
        note="Under active multi-state quarantine.",
    ),
    Taxon(
        slug="emerald_ash_borer",
        scientific_name="Agrilus planipennis",
        common_name="emerald ash borer",
        role="threat",
        status="federal quarantine lifted",
        instrument="85 FR 81737",
        note="Federal quarantine lifted January 14, 2021; state quarantines remain.",
        year=2021,
    ),
    Taxon(
        slug="asian_longhorned_beetle",
        scientific_name="Anoplophora glabripennis",
        common_name="Asian longhorned beetle",
        role="threat",
        status="active eradication",
        instrument="7 C.F.R. § 301.51",
        note="Under active eradication in Ohio and Massachusetts.",
    ),
    Taxon(
        slug="medfly",
        scientific_name="Ceratitis capitata",
        common_name="Mediterranean fruit fly",
        role="threat",
        status="transient / eradication",
        instrument="7 C.F.R. §§ 301.78 et seq.",
        note="Subject to recurring eradication quarantines, including in California.",
    ),
    Taxon(
        slug="spongy_moth",
        scientific_name="Lymantria dispar",
        common_name="spongy moth",
        role="threat",
        status="active quarantine",
        instrument="7 C.F.R. § 301.45",
        note="Active northeastern quarantine; renamed from 'gypsy moth' in 2022.",
        year=2022,
    ),
    Taxon(
        slug="northern_giant_hornet",
        scientific_name="Vespa mandarinia",
        common_name="northern giant hornet ('murder hornet')",
        role="threat",
        status="eradicated from US",
        instrument="APHIS general authority",
        note="Declared eradicated from the United States on December 18, 2024 — "
        "the first Vespa eradication in North America.",
        year=2024,
    ),
    Taxon(
        slug="new_world_screwworm",
        scientific_name="Cochliomyia hominivorax",
        common_name="New World screwworm",
        role="threat",
        status="sterile-insect eradication",
        instrument="Sterile Insect Technique program",
        note="A June 3, 2026 detection in a calf in Zavala County, Texas "
        "reactivated sterile-insect eradication planning.",
        year=2026,
    ),
    # ── Protected — conservation ───────────────────────────────────────────
    Taxon(
        slug="schaus_swallowtail",
        scientific_name="Heraclides aristodemus ponceanus",
        common_name="Schaus swallowtail",
        role="protected",
        status="ESA-listed",
        instrument="16 U.S.C. § 1531",
        note="Among the first insects listed under the ESA — with the Bahama "
        "swallowtail — initially as threatened (April 28, 1976) and reclassified "
        "endangered in 1984.",
        year=1976,
    ),
    Taxon(
        slug="delhi_sands_fly",
        scientific_name="Rhaphiomidas terminatus abdominalis",
        common_name="Delhi Sands flower-loving fly",
        role="protected",
        status="ESA-listed",
        instrument="16 U.S.C. § 1531",
        note="The first and only fly listed (1993); protagonist of the "
        "Home Builders v. Babbitt Commerce Clause case.",
        year=1993,
    ),
    Taxon(
        slug="rusty_patched_bumblebee",
        scientific_name="Bombus affinis",
        common_name="rusty patched bumble bee",
        role="protected",
        status="ESA-listed",
        instrument="16 U.S.C. § 1531",
        note="First bee in the continental US listed under the ESA (effective "
        "March 21, 2017).",
        year=2017,
    ),
    Taxon(
        slug="american_burying_beetle",
        scientific_name="Nicrophorus americanus",
        common_name="American burying beetle",
        role="protected",
        status="ESA-listed",
        instrument="16 U.S.C. § 1531",
        note="Once found in 35 states; now persisting in only six.",
    ),
    Taxon(
        slug="monarch",
        scientific_name="Danaus plexippus",
        common_name="monarch butterfly",
        role="protected",
        status="proposed threatened (unlisted)",
        instrument="16 U.S.C. § 1531",
        note="Proposed for threatened listing December 12, 2024; final rule "
        "not yet effective as of June 29, 2026, according to FWS status text.",
        year=2024,
    ),
    Taxon(
        slug="queen_alexandras_birdwing",
        scientific_name="Ornithoptera alexandrae",
        common_name="Queen Alexandra's birdwing",
        role="protected",
        status="CITES Appendix I",
        instrument="Convention on International Trade in Endangered Species (1973)",
        note="The world's largest butterfly; central to the illicit butterfly "
        "trade and the Kojima smuggling prosecution.",
    ),
    # ── Property — owned bees ──────────────────────────────────────────────
    Taxon(
        slug="western_honey_bee",
        scientific_name="Apis mellifera",
        common_name="western honey bee",
        role="property",
        status="ferae naturae / qualified property",
        instrument="7 U.S.C. §§ 281–286",
        note="Owned only while hived or actively pursued; ~10,000 hives stolen "
        "2013–2024 and prosecuted as agricultural/livestock theft.",
    ),
    # ── Invention — engineered, farmed, edible ─────────────────────────────
    Taxon(
        slug="oxitec_aedes",
        scientific_name="Aedes aegypti (OX5034)",
        common_name="Oxitec engineered yellow-fever mosquito",
        role="invention",
        status="EPA experimental-use release",
        instrument="Coordinated Framework for Regulation of Biotechnology (1986)",
        note="Genetically engineered line released in the Florida Keys under "
        "EPA Experimental Use Permit (2020; amended 2022).",
        year=2020,
    ),
    Taxon(
        slug="house_cricket",
        scientific_name="Acheta domesticus",
        common_name="house cricket",
        role="invention",
        status="EU novel-food authorized",
        instrument="Regulation (EU) 2015/2283",
        note="Authorized for human food in the EU via an individual "
        "implementing regulation and EFSA opinion.",
    ),
    Taxon(
        slug="yellow_mealworm",
        scientific_name="Tenebrio molitor",
        common_name="yellow mealworm",
        role="invention",
        status="EU novel-food authorized",
        instrument="Regulation (EU) 2015/2283",
        note="Among the first insects authorized as an EU novel food.",
    ),
    Taxon(
        slug="black_soldier_fly",
        scientific_name="Hermetia illucens",
        common_name="black soldier fly",
        role="invention",
        status="authorized feed insect",
        instrument="Regulation (EU) 2017/893",
        note="Larvae approved by the US FDA/AAFCO arrangement for salmonids in "
        "2016 and admitted to EU aquaculture feed.",
        year=2016,
    ),
    Taxon(
        slug="silkworm",
        scientific_name="Bombyx mori",
        common_name="domestic silkworm",
        role="invention",
        status="sericulture-regulated",
        instrument="Central Silk Board Act of 1948 (India)",
        note="Quality-controlled silkworm biology governed as commercial public "
        "interest; some Indian acts criminalize unauthorized seed production.",
    ),
    # ── Moral patient — welfare/sentience ──────────────────────────────────
    Taxon(
        slug="fruit_fly",
        scientific_name="Drosophila melanogaster",
        common_name="common fruit fly",
        role="moral_patient",
        status="candidate sentient invertebrate",
        instrument="Animal Welfare (Sentience) Act 2022 (extension power)",
        note="Gibbons et al. (2022) scored adult flies 6 of 8 sentience "
        "criteria — higher than some decapods already covered by the UK Act.",
        year=2022,
    ),
    # ── Defendant — the animal trials ──────────────────────────────────────
    Taxon(
        slug="trial_weevils",
        scientific_name="Curculionidae (weevils)",
        common_name="the weevils of St-Julien",
        role="defendant",
        status="historical defendant",
        instrument="ecclesiastical trial",
        note="Defendants in the celebrated 1545–46 and 1587 St-Julien vine-"
        "weevil prosecutions; the 1587 community offered them a land preserve.",
        year=1587,
    ),
    # ── Weapon — entomological warfare ─────────────────────────────────────
    Taxon(
        slug="plague_flea",
        scientific_name="Xenopsylla cheopis",
        common_name="oriental rat flea",
        role="weapon",
        status="historical biological weapon",
        instrument="Biological Weapons Convention (1972)",
        note="Plague-infected fleas were air-dropped by Japan's Unit 731; the "
        "October 27, 1940 Ningbo attack alone caused roughly 1,500 deaths.",
        year=1940,
    ),
)

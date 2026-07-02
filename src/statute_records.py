# entolaw-size-ok: source-owned statute registry records; split from facade for size gate.
from dataclasses import dataclass, field


# Structural categories grouping the instruments by the legal machinery they
# operate. These map onto, but are broader than, the registered roles.
CATEGORIES: tuple[str, ...] = (
    "forensic",
    "quarantine",
    "conservation",
    "property",
    "biotech_ip",
    "food",
    "welfare",
    "public_health",
    "warfare",
)

# Issuing jurisdiction vocabulary.
JURISDICTIONS: tuple[str, ...] = (
    "US-federal",
    "US-state",
    "US-colonial",
    "UK",
    "India",
    "EU",
    "international",
)


@dataclass(frozen=True)
class Statute:
    """A statute, regulation, or treaty governing some role of the insect.

    Attributes:
        slug: Stable identifier.
        citation: Parseable citation or named-instrument string.
        short_title: Human-readable instrument name.
        category: One of :data:`CATEGORIES`.
        jurisdiction: One of :data:`JURISDICTIONS`.
        role: The :mod:`src.roles` slug the instrument principally governs.
        summary: One- or two-sentence source-anchored description.
        cross_references: Companion instruments cited by this entry.
    """

    slug: str
    citation: str
    short_title: str
    category: str
    jurisdiction: str
    role: str
    summary: str
    cross_references: tuple[str, ...] = field(default_factory=tuple)


STATUTES: tuple[Statute, ...] = (
    # ── Forensic admissibility ─────────────────────────────────────────────
    Statute(
        slug="fre_702",
        citation="Fed. R. Evid. 702",
        short_title="Federal Rule of Evidence 702",
        category="forensic",
        jurisdiction="US-federal",
        role="witness",
        summary="Admits expert testimony resting on reliable principles "
        "reliably applied to the facts — the rule entomological PMI testimony "
        "is screened under after Daubert and Kumho Tire.",
    ),
    # ── Quarantine & invasive-species ──────────────────────────────────────
    Statute(
        slug="destructive_insects_act_1877",
        citation="Destructive Insects Act 1877",
        short_title="UK Destructive Insects Act",
        category="quarantine",
        jurisdiction="UK",
        role="threat",
        summary="Authorized Privy Council orders to prevent introduction and "
        "spread of Colorado beetle, including landing prohibitions, crop "
        "destruction, entry on land, recordkeeping, and penalties.",
    ),
    Statute(
        slug="federal_insecticide_act_1910",
        citation="Federal Insecticide Act of 1910",
        short_title="Federal Insecticide Act",
        category="quarantine",
        jurisdiction="US-federal",
        role="threat",
        summary="Converted insect-killing chemistry into a federal commerce "
        "problem by barring adulterated or misbranded insecticides, Paris "
        "greens, lead arsenates, and fungicides in interstate trade.",
    ),
    Statute(
        slug="plant_quarantine_act_1912",
        citation="Plant Quarantine Act of 1912",
        short_title="Plant Quarantine Act",
        category="quarantine",
        jurisdiction="US-federal",
        role="threat",
        summary="Created a dedicated federal plant-quarantine apparatus for "
        "plant diseases and insect pests, including import exclusion, "
        "interstate quarantine, inspection, disinfection, certification, and a "
        "Federal Horticultural Board with Bureau of Entomology participation.",
        cross_references=("37 Stat. 315",),
    ),
    Statute(
        slug="india_destructive_insects_pests_act_1914",
        citation="Destructive Insects and Pests Act 1914",
        short_title="India Destructive Insects and Pests Act",
        category="quarantine",
        jurisdiction="India",
        role="threat",
        summary="Gave central authority to prevent introduction into India and "
        "interprovincial transport of insects, fungi, or other pests destructive "
        "to crops.",
    ),
    Statute(
        slug="plant_protection_act",
        citation="7 U.S.C. §§ 7701–7786",
        short_title="Plant Protection Act of 2000",
        category="quarantine",
        jurisdiction="US-federal",
        role="threat",
        summary="The master statute empowering USDA APHIS to prohibit movement, "
        "declare quarantines, require permits, and seize infested articles; "
        "civil penalties reach $1,000,000 per willful violation.",
        cross_references=("7 U.S.C. § 7712", "7 U.S.C. § 7734"),
    ),
    Statute(
        slug="lacey_act_injurious",
        citation="18 U.S.C. § 42",
        short_title="Lacey Act injurious-species provision",
        category="quarantine",
        jurisdiction="US-federal",
        role="threat",
        summary="A strict-liability criminal statute that conspicuously does "
        "not list insects, deferring to the Plant Protection Act for plant "
        "pests and leaving non-plant-pest insects in a regulatory gap.",
    ),
    Statute(
        slug="slf_quarantine",
        citation="7 C.F.R. § 301.92",
        short_title="Spotted Lanternfly quarantine",
        category="quarantine",
        jurisdiction="US-federal",
        role="threat",
        summary="Active federal-coordinated quarantine for Lycorma delicatula "
        "across numerous states.",
    ),
    Statute(
        slug="alb_quarantine",
        citation="7 C.F.R. § 301.51",
        short_title="Asian Longhorned Beetle quarantine",
        category="quarantine",
        jurisdiction="US-federal",
        role="threat",
        summary="Active eradication quarantine for Anoplophora glabripennis.",
    ),
    Statute(
        slug="eu_plant_health",
        citation="Regulation (EU) 2016/2031",
        short_title="EU Plant Health Law",
        category="quarantine",
        jurisdiction="EU",
        role="threat",
        summary="Lists priority quarantine insects and operates a plant-passport "
        "system across the Union.",
    ),
    Statute(
        slug="eu_invasive_alien_species",
        citation="Regulation (EU) 1143/2014",
        short_title="EU Invasive Alien Species Regulation",
        category="quarantine",
        jurisdiction="EU",
        role="threat",
        summary="Creates the Union list of invasive alien species of Union "
        "concern, whose listed species face restrictions on keeping, importing, "
        "selling, breeding, growing, and release.",
    ),
    Statute(
        slug="ippc",
        citation="International Plant Protection Convention (1951)",
        short_title="International Plant Protection Convention",
        category="quarantine",
        jurisdiction="international",
        role="threat",
        summary="The treaty whose ISPMs set the phytosanitary benchmark used "
        "under the WTO SPS Agreement to judge whether a quarantine is science-"
        "based or a disguised trade barrier.",
        cross_references=(
            "Agreement on the Application of Sanitary and Phytosanitary Measures (1995)",
        ),
    ),
    Statute(
        slug="wto_sps",
        citation="Agreement on the Application of Sanitary and Phytosanitary Measures (1995)",
        short_title="WTO SPS Agreement",
        category="quarantine",
        jurisdiction="international",
        role="threat",
        summary="Requires that phytosanitary insect-quarantine measures be "
        "science-based and not disguised restrictions on trade.",
    ),
    # ── Conservation ───────────────────────────────────────────────────────
    Statute(
        slug="esa",
        citation="16 U.S.C. § 1531",
        short_title="Endangered Species Act of 1973",
        category="conservation",
        jurisdiction="US-federal",
        role="protected",
        summary="Defines protected wildlife to expressly include any arthropod "
        "or other invertebrate, putting non-pest insects within the statutory "
        "eligibility frame while retaining an express § 3(6) pest carve-out.",
    ),
    Statute(
        slug="cesa_fish_definition",
        citation="Fish & Game Code § 45",
        short_title="California 'fish' definition (incl. invertebrates)",
        category="conservation",
        jurisdiction="US-state",
        role="protected",
        summary="Defines 'fish' to include invertebrates — the hook on which "
        "Almond Alliance held that bumblebees are 'fish' eligible for CESA "
        "listing.",
    ),
    Statute(
        slug="co_invertebrate_conservation",
        citation="Colorado HB24-1117 (2024)",
        short_title="Colorado invertebrate and rare-plant conservation authority",
        category="conservation",
        jurisdiction="US-state",
        role="protected",
        summary="Adds rare plants and invertebrates to Colorado's nongame "
        "conservation law and authorizes voluntary programs to conserve, "
        "protect, and perpetuate invertebrates.",
    ),
    Statute(
        slug="cites",
        citation="Convention on International Trade in Endangered Species (1973)",
        short_title="CITES",
        category="conservation",
        jurisdiction="international",
        role="protected",
        summary="Lists certain insects — notably birdwing butterflies on "
        "Appendix I/II — and requires domestic implementing legislation to make "
        "trade legal, sustainable, and traceable.",
    ),
    Statute(
        slug="kunming_montreal_gbf",
        citation="Kunming-Montreal Global Biodiversity Framework (2022)",
        short_title="Kunming-Montreal Global Biodiversity Framework",
        category="conservation",
        jurisdiction="international",
        role="protected",
        summary="Sets the current global biodiversity target architecture into "
        "which insect-conservation indicators and national restoration duties "
        "must fit.",
    ),
    Statute(
        slug="eu_nature_restoration",
        citation="Regulation (EU) 2024/1991",
        short_title="EU Nature Restoration Regulation",
        category="conservation",
        jurisdiction="EU",
        role="protected",
        summary="Makes pollinator decline a restoration-law target, tying insect "
        "conservation to EU-wide monitoring and reversal duties.",
    ),
    # ── Property / apiculture ──────────────────────────────────────────────
    Statute(
        slug="honeybee_act",
        citation="7 U.S.C. §§ 281–286",
        short_title="Honeybee Act of 1922",
        category="property",
        jurisdiction="US-federal",
        role="property",
        summary="Restricts importation of honey bees; states layer apiary "
        "registration, disease-control, and Africanized-bee rules on top.",
    ),
    Statute(
        slug="ca_africanized_bee",
        citation="Cal. Food & Agric. Code §§ 29320–29322",
        short_title="California Africanized-bee controls",
        category="property",
        jurisdiction="US-state",
        role="property",
        summary="State controls on Africanized honey bees within California's "
        "billion-dollar almond-pollination economy.",
    ),
    Statute(
        slug="virginia_mulberry_trees",
        citation="Virginia Act Concerning Planting of Mulberry Trees (1658)",
        short_title="Virginia mulberry-tree sericulture mandate",
        category="biotech_ip",
        jurisdiction="US-colonial",
        role="invention",
        summary="Required land proprietors to plant and tend mulberry trees, "
        "making the plant infrastructure for silkworm production a statutory "
        "development duty.",
    ),
    Statute(
        slug="virginia_assembly_mulberry_silke_flaxe",
        citation="Virginia Act Concerning Mulberry Trees and Silke-Flaxe (1619)",
        short_title="Virginia mulberry and silk-flax mandate",
        category="biotech_ip",
        jurisdiction="US-colonial",
        role="invention",
        summary="Required settled colonists to plant and maintain mulberry "
        "trees and to plant silk-flax, making silk inputs an early statutory "
        "development duty.",
    ),
    # ── Biotechnology, IP & food ───────────────────────────────────────────
    Statute(
        slug="patentable_subject_matter",
        citation="35 U.S.C. § 101",
        short_title="Patentable subject matter",
        category="biotech_ip",
        jurisdiction="US-federal",
        role="invention",
        summary="The provision under which Chakrabarty and Ex parte Allen made "
        "engineered insect lines and their products patentable.",
        cross_references=("America Invents Act of 2011 § 33(a)",),
    ),
    Statute(
        slug="coordinated_framework",
        citation="Coordinated Framework for Regulation of Biotechnology (1986)",
        short_title="Coordinated Framework for Biotechnology",
        category="biotech_ip",
        jurisdiction="US-federal",
        role="invention",
        summary="Splits jurisdiction over genetically modified insects among "
        "EPA (FIFRA), USDA (APHIS), and FDA — the regime under which Oxitec's "
        "engineered Aedes aegypti was released in the Florida Keys.",
    ),
    Statute(
        slug="cartagena_protocol",
        citation="Cartagena Protocol on Biosafety (2000)",
        short_title="Cartagena Protocol on Biosafety",
        category="biotech_ip",
        jurisdiction="international",
        role="invention",
        summary="The international biosafety frame relevant to gene-drive "
        "insects, even though deployment-specific governance remains thin.",
    ),
    Statute(
        slug="nagoya_protocol",
        citation="Nagoya Protocol (2010)",
        short_title="Nagoya Protocol on access & benefit-sharing",
        category="biotech_ip",
        jurisdiction="international",
        role="invention",
        summary="Establishes sovereign rights over genetic resources and a "
        "benefit-sharing duty — directly relevant to bioprospecting insect "
        "venom peptides, antimicrobials, and silk proteins.",
    ),
    Statute(
        slug="eu_novel_food",
        citation="Regulation (EU) 2015/2283",
        short_title="EU Novel Food Regulation",
        category="food",
        jurisdiction="EU",
        role="invention",
        summary="Treats insects as novel foods requiring pre-market EFSA safety "
        "assessment; has authorized house cricket, yellow mealworm, migratory "
        "locust, and others through individual implementing regulations.",
    ),
    Statute(
        slug="ffdca_adulteration",
        citation="21 U.S.C. § 342",
        short_title="FFDCA adulteration / 'filth' provision",
        category="food",
        jurisdiction="US-federal",
        role="invention",
        summary="Deems food adulterated if it consists in part of any filthy "
        "substance — the provision behind FDA insect-fragment defect action "
        "levels, between which edible insects sit without a dedicated US "
        "approval pathway.",
    ),
    Statute(
        slug="utah_insect_meat_labeling",
        citation="Utah H.B. 138 (2025)",
        short_title="Utah cultivated meat and insect-based substitute labeling",
        category="food",
        jurisdiction="US-state",
        role="invention",
        summary="Requires consumer-facing labeling for food containing plant or "
        "insect-based meat substitutes, making insect protein a named state-law "
        "product category.",
    ),
    Statute(
        slug="eu_insect_feed",
        citation="Regulation (EU) 2017/893",
        short_title="EU processed-insect-protein feed authorization",
        category="food",
        jurisdiction="EU",
        role="invention",
        summary="Relaxed the post-BSE feed ban to admit processed insect "
        "protein into aquaculture feed (extended to poultry and pigs in 2021).",
    ),
    # ── Welfare & sentience ────────────────────────────────────────────────
    Statute(
        slug="uk_sentience_act",
        citation="Animal Welfare (Sentience) Act 2022",
        short_title="UK Animal Welfare (Sentience) Act",
        category="welfare",
        jurisdiction="UK",
        role="moral_patient",
        summary="Recognizes animal sentience and covers decapod crustaceans and "
        "cephalopods; § 5(2) reserves a regulatory power to extend coverage to "
        "any invertebrate — insects included — without new primary legislation.",
    ),
    Statute(
        slug="eu_animals_in_science",
        citation="Directive 2010/63/EU",
        short_title="EU animals-in-science Directive",
        category="welfare",
        jurisdiction="EU",
        role="moral_patient",
        summary="The key instrument governing animal use in scientific "
        "procedures; it systematically excludes insects despite growing "
        "sentience evidence.",
    ),
    Statute(
        slug="tfeu_article_13",
        citation="Treaty on the Functioning of the European Union, Art. 13",
        short_title="TFEU Article 13 (sentient-beings clause)",
        category="welfare",
        jurisdiction="EU",
        role="moral_patient",
        summary="Acknowledges animals as sentient beings, but the clause is not "
        "self-executing and in practice protections reach almost exclusively "
        "vertebrates.",
    ),
    # ── Public-health vector control ───────────────────────────────────────
    Statute(
        slug="ca_vector_control",
        citation="Cal. Health & Safety Code § 2001",
        short_title="California Mosquito Abatement & Vector Control",
        category="public_health",
        jurisdiction="US-state",
        role="threat",
        summary="Declares organized public programs the best protection against "
        "vector-borne disease and creates special districts to surveil and "
        "control mosquitoes; California has run such districts since 1915.",
    ),
    Statute(
        slug="smash_act",
        citation="Strengthening Mosquito Abatement for Safety and Health Act of 2018",
        short_title="SMASH Act",
        category="public_health",
        jurisdiction="US-federal",
        role="threat",
        summary="House-passed authorization of mosquito-control funding and CDC "
        "epidemiology-laboratory capacity grants — federal recognition of "
        "mosquito biology as national public-health law.",
    ),
    # ── Warfare & biosecurity ──────────────────────────────────────────────
    Statute(
        slug="bwc",
        citation="Biological Weapons Convention (1972)",
        short_title="Biological Weapons Convention",
        category="warfare",
        jurisdiction="international",
        role="weapon",
        summary="Treats insect vectors as covered means of delivery under its "
        "General Purpose Criterion, though ambiguity persists over uninfected "
        "insects used in crop warfare.",
    ),
    Statute(
        slug="ag_bioterrorism_act",
        citation="Agricultural Bioterrorism Protection Act of 2002, 7 U.S.C. § 8401",
        short_title="Agricultural Bioterrorism Protection Act",
        category="warfare",
        jurisdiction="US-federal",
        role="weapon",
        summary="Classifies certain plant pests and pathogens as select agents "
        "subject to stringent possession and transfer regulation.",
    ),
)

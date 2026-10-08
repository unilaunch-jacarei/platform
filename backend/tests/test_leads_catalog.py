from backend.domains.leads.catalog import (
    COURSE_SEEDS,
    INSTITUTION_SEEDS,
    INTEREST_AREA_SEEDS,
    catalog_uuid,
    normalize_catalog_name,
)


def test_catalog_name_normalization_is_stable() -> None:
    assert normalize_catalog_name("  FATEC   Jacareí! ") == "fatec jacarei"
    assert normalize_catalog_name("Ciência da Computação") == "ciencia da computacao"


def test_catalog_seeds_have_deterministic_unique_ids() -> None:
    seeds = (*INSTITUTION_SEEDS, *COURSE_SEEDS, *INTEREST_AREA_SEEDS)

    assert len({seed.id for seed in seeds}) == len(seeds)
    assert COURSE_SEEDS[0].id == catalog_uuid("course", "analise e desenvolvimento de sistemas")


def test_named_catalog_keys_and_aliases_are_unique_per_catalog() -> None:
    for seeds in (INSTITUTION_SEEDS, COURSE_SEEDS):
        keys = []
        for seed in seeds:
            keys.extend(normalize_catalog_name(value) for value in (seed.name, *seed.aliases))
        assert len(keys) == len(set(keys))


def test_interest_area_codes_are_unique() -> None:
    assert len({area.code for area in INTEREST_AREA_SEEDS}) == len(INTEREST_AREA_SEEDS)

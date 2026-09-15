import re
import unicodedata
import uuid
from dataclasses import dataclass

CATALOG_NAMESPACE = uuid.UUID("8c7bc184-f3d8-41ec-adb7-246953ff9347")

LEGACY_INTEREST_AREA_CODES = {
    "backend": "backend",
    "frontend": "frontend",
    "devops": "devops-cloud",
    "produto": "product",
    "ux ui": "ux-ui",
}


def normalize_catalog_name(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    alphanumeric = re.sub(r"[^a-z0-9]+", " ", without_accents.casefold())
    return " ".join(alphanumeric.split())


def catalog_uuid(kind: str, key: str) -> uuid.UUID:
    return uuid.uuid5(CATALOG_NAMESPACE, f"{kind}:{key}")


@dataclass(frozen=True)
class NamedCatalogSeed:
    id: uuid.UUID
    name: str
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class InterestAreaSeed:
    id: uuid.UUID
    code: str
    name: str


def named_seed(kind: str, name: str, *aliases: str) -> NamedCatalogSeed:
    return NamedCatalogSeed(catalog_uuid(kind, normalize_catalog_name(name)), name, aliases)


def interest_seed(code: str, name: str) -> InterestAreaSeed:
    return InterestAreaSeed(catalog_uuid("interest-area", code), code, name)


INSTITUTION_SEEDS = (
    named_seed("institution", "Universidade de São Paulo", "USP"),
    named_seed("institution", "Universidade Estadual de Campinas", "Unicamp"),
    named_seed("institution", "Universidade Estadual Paulista", "Unesp"),
    named_seed("institution", "Universidade Federal do Rio de Janeiro", "UFRJ"),
    named_seed("institution", "Universidade Federal de Minas Gerais", "UFMG"),
    named_seed("institution", "Universidade de Brasília", "UnB"),
    named_seed("institution", "Universidade Federal do Paraná", "UFPR"),
    named_seed("institution", "Universidade Federal do Rio Grande do Sul", "UFRGS"),
    named_seed("institution", "Universidade Federal de Santa Catarina", "UFSC"),
    named_seed("institution", "Universidade Federal de Pernambuco", "UFPE"),
    named_seed("institution", "Universidade Federal do Ceará", "UFC"),
    named_seed("institution", "Universidade Federal da Bahia", "UFBA"),
    named_seed("institution", "Universidade Federal do Pará", "UFPA"),
    named_seed("institution", "Universidade Federal do Amazonas", "UFAM"),
    named_seed("institution", "Universidade Federal de Goiás", "UFG"),
    named_seed("institution", "Universidade Federal de Mato Grosso do Sul", "UFMS"),
    named_seed("institution", "Universidade Federal de São Carlos", "UFSCar"),
    named_seed("institution", "Universidade Tecnológica Federal do Paraná", "UTFPR"),
    named_seed("institution", "Instituto Federal de São Paulo", "IFSP"),
    named_seed(
        "institution",
        "Faculdade de Tecnologia de Jacareí",
        "Fatec Jacareí",
    ),
    named_seed("institution", "Pontifícia Universidade Católica de São Paulo", "PUC-SP"),
    named_seed("institution", "Universidade Presbiteriana Mackenzie", "Mackenzie"),
)

COURSE_SEEDS = (
    named_seed("course", "Análise e Desenvolvimento de Sistemas", "ADS"),
    named_seed("course", "Desenvolvimento de Software Multiplataforma", "DSM"),
    named_seed("course", "Ciência da Computação", "CC", "Ciências da Computação"),
    named_seed("course", "Sistemas de Informação", "SI"),
    named_seed("course", "Engenharia de Software"),
    named_seed("course", "Engenharia de Dados"),
    named_seed("course", "Engenharia da Computação"),
    named_seed("course", "Banco de Dados"),
    named_seed("course", "Ciência de Dados"),
    named_seed("course", "Inteligência Artificial", "IA"),
    named_seed("course", "Segurança da Informação"),
    named_seed("course", "Redes de Computadores"),
)

INTEREST_AREA_SEEDS = (
    interest_seed("backend", "Backend"),
    interest_seed("frontend", "Frontend"),
    interest_seed("mobile", "Desenvolvimento mobile"),
    interest_seed("data", "Dados e analytics"),
    interest_seed("devops-cloud", "DevOps e cloud"),
    interest_seed("ai", "Inteligência artificial"),
    interest_seed("cybersecurity", "Cibersegurança"),
    interest_seed("product", "Produto"),
    interest_seed("ux-ui", "UX e UI"),
    interest_seed("qa", "Qualidade de software"),
    interest_seed("entrepreneurship", "Empreendedorismo"),
)

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional, Union
from urllib.parse import parse_qs, urljoin, urlsplit

import requests
from pyquery import PyQuery


INFOSOUD_URL = "https://infosoud.justice.cz/InfoSoud/public/"

DRUH_ZAHAJENI = "ZAHAJ_RIZ"
DRUH_SKONCENI = "ST_VEC_ODS"
DRUH_ODVOLANI = "ODVOLANI"


@dataclass
class Udalost:
    nazev: str
    datum: date
    url: str = field(default="", compare=False, repr=False)

    @property
    def absolute_url(self):
        return urljoin(INFOSOUD_URL, self.url).replace(" ", "%20")

    @property
    def druh(self):
        parts = urlsplit(self.url)
        return parse_qs(parts.query)["druhUdalosti"][0]


@dataclass
class DilciRizeni:
    spisova_znacka: str


@dataclass
class Rizeni:
    spisova_znacka: str
    soud: str
    stav_rizeni: str
    udalosti: List[Udalost] = field(default_factory=list)
    dilci_rizeni: List[DilciRizeni] = field(default_factory=list)
    predmet_rizeni: str = ""
    posledni_zmena: Optional[datetime] = None
    cas_aktualizace: Optional[datetime] = None

    def udalosti_podle_druhu(self, druh) -> List[Udalost]:
        return list(filter(lambda x: x.druh == druh, self.udalosti))

    @property
    def zahajeni(self) -> Udalost:
        udalosti = self.udalosti_podle_druhu(DRUH_ZAHAJENI)
        assert len(udalosti) == 1, "Ocekavano prave jedno zahajeni rizeni"
        return udalosti[0]

    @property
    def skonceni(self) -> Optional[Udalost]:
        udalosti = self.udalosti_podle_druhu(DRUH_SKONCENI)
        assert len(udalosti) <= 1, "Ocekavano maximalne jedno skonceni rizeni"
        if udalosti:
            return udalosti[0]
        return None

    @property
    def delka_rizeni(self):
        if self.skonceni:
            konec = self.skonceni.datum
        else:
            konec = date.today()
        return konec - self.zahajeni.datum

    @property
    def probehlo_odvolani(self):
        return bool(self.udalosti_podle_druhu(DRUH_ODVOLANI))

    def set_predmet_rizeni(self):
        response = requests.get(self.zahajeni.absolute_url)
        response.raise_for_status()
        self.predmet_rizeni = parse_predmet_rizeni(response.text)


class SpisovaZnackaNeexistujeError(Exception):
    pass


def parse_rizeni(html) -> Rizeni:
    neexituje_re = re.search(r"Hledan?? spisov?? zna??ka ([\w\s\/]+) neexistuje", html)
    if neexituje_re:
        raise SpisovaZnackaNeexistujeError(
            f"Spisov?? zna??ka {neexituje_re.group(1)} neexistuje"
        )

    query = PyQuery(html)
    prefix = "td.body > table > tr > td > table"
    content = query(prefix)
    spisova_znacka = content("tr:nth-child(1) td span.body-banner-data").text()
    soud = content.children(
        "tr:nth-child(3) > td table tr td span.body-vyrazny-text"
    ).text()
    stav = content.children("tr:nth-child(4) > td").text().split(":")[1].strip()
    prubeh = content.children("tr:nth-child(7) > td > table").children("tr")

    parts = (
        content.children("tr:nth-child(9) > td > table > tr > td:nth-child(2)")
        .text()
        .split()
    )
    posledni_zmena = datetime.strptime(f"{parts[0]} {parts[1]}", "%d.%m.%Y %H:%M:%S")
    cas_aktualizace = datetime.strptime(f"{parts[2]} {parts[3]}", "%d.%m.%Y %H:%M:%S")

    rizeni = Rizeni(
        spisova_znacka=spisova_znacka,
        soud=soud,
        stav_rizeni=stav,
        posledni_zmena=posledni_zmena,
        cas_aktualizace=cas_aktualizace,
    )

    for polozka in prubeh[1:]:
        ret = parse_udalost(polozka)
        if isinstance(ret, Udalost):
            rizeni.udalosti.append(ret)
        elif isinstance(ret, DilciRizeni):
            rizeni.dilci_rizeni.append(ret)

    return rizeni


def parse_udalost(elem) -> Union[DilciRizeni, Udalost]:
    udalost = PyQuery(elem)
    if "Sen??tn?? v??c" in udalost.html():
        spisova_znacka = udalost.children("td:nth-child(2) > a").text()
        return DilciRizeni(spisova_znacka=spisova_znacka)
    else:
        link = udalost.children("td:first-child > a")
        url = link.attr("href")
        typ = link.text()
        datum_str = udalost.children("td:nth-child(2)").text()
        datum = datetime.strptime(datum_str, "%d.%m.%Y").date()
        return Udalost(typ, datum, url)


def parse_predmet_rizeni(html):
    query = PyQuery(html)
    content = query("td.body > table > tr > td > table > tr:nth-child(7) > td")
    predmet_rizeni = content.text().split(":")
    assert predmet_rizeni[0].strip() == "P??edm??t ????zen??"
    return predmet_rizeni[1].strip()


def load_from_url(url) -> Rizeni:
    response = requests.get(url)
    response.raise_for_status()
    return parse_rizeni(response.text)


def load_from_file(filename) -> Rizeni:
    with open(filename) as f:
        return parse_rizeni(f.read())

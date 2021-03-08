from dataclasses import dataclass, field
from typing import Iterator, List, Union
from urllib.parse import parse_qs, urljoin, urlsplit

import requests
from pyquery import PyQuery


INFOSOUD_URL = "https://infosoud.justice.cz/InfoSoud/public/"


@dataclass
class Udalost:
    nazev: str
    datum: str
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

    def udalosti_podle_druhu(self, druh) -> List[Udalost]:
        return list(filter(lambda x: x.druh == druh, self.udalosti))

    @property
    def zahajeni(self):
        udalosti = self.udalosti_podle_druhu("ZAHAJ_RIZ")
        assert len(udalosti) == 1, "Ocekavano prave jedno zahajeni rizeni"
        return udalosti[0]

    def set_predmet_rizeni(self):
        response = requests.get(self.zahajeni.absolute_url)
        response.raise_for_status()
        self.predmet_rizeni = parse_predmet_rizeni(response.text)


def parse_rizeni(html) -> Rizeni:
    query = PyQuery(html)
    prefix = "td.body > table > tr > td > table"
    content = query(prefix)
    spisova_znacka = content("tr:nth-child(1) td span.body-banner-data").text()
    soud = content.children(
        "tr:nth-child(3) > td table tr td span.body-vyrazny-text"
    ).text()
    stav = content.children("tr:nth-child(4) > td").text().split(":")[1].strip()
    prubeh = content.children("tr:nth-child(7) > td > table").children("tr")

    rizeni = Rizeni(
        spisova_znacka=spisova_znacka,
        soud=soud,
        stav_rizeni=stav,
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
    if "Senátní věc" in udalost.html():
        spisova_znacka = udalost.children("td:nth-child(2) > a").text()
        return DilciRizeni(spisova_znacka=spisova_znacka)
    else:
        link = udalost.children("td:first-child > a")
        url = link.attr("href")
        typ = link.text()
        datum = udalost.children("td:nth-child(2)").text()
        return Udalost(typ, datum, url)


def parse_predmet_rizeni(html):
    query = PyQuery(html)
    content = query("td.body > table > tr > td > table > tr:nth-child(7) > td")
    predmet_rizeni = content.text().split(":")
    assert predmet_rizeni[0].strip() == "Předmět řízení"
    return predmet_rizeni[1].strip()

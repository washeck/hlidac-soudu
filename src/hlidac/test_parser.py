import datetime
import os
from datetime import date, timedelta
from pathlib import Path
from unittest import TestCase

from hlidac.parser import (
    DRUH_ZAHAJENI,
    DilciRizeni,
    Rizeni,
    SpisovaZnackaNeexistujeError,
    Udalost,
    load_from_file,
    parse_predmet_rizeni,
    parse_udalost,
)

testdata_dir = Path(__file__).parent / "testdata"


class Test(TestCase):
    def test_hlavni_rizeni(self):
        rizeni = load_from_file(testdata_dir / "62-Nc-2528-2019.html")

        self.assertEqual(
            rizeni,
            Rizeni(
                spisova_znacka="62 NC 2528 / 2019",
                soud="Městský soud Praha\xa0>\xa0Obvodní soud Praha 9",
                stav_rizeni="Odškrtnutá - evidenčně ukončená věc (od 08.08.2019)",
                predmet_rizeni="",
                udalosti=[
                    Udalost(nazev="Zahájení řízení", datum=date(2019, 3, 8)),
                    Udalost(nazev="Vyřízení věci", datum=date(2019, 8, 8)),
                    Udalost(nazev="Skončení věci", datum=date(2019, 8, 8)),
                ],
                dilci_rizeni=[
                    DilciRizeni(spisova_znacka="12 P A NC 105 / 2019"),
                    DilciRizeni(spisova_znacka="12 P A NC 104 / 2019"),
                ],
                posledni_zmena=datetime.datetime(2019, 8, 8, 16, 46, 30),
                cas_aktualizace=datetime.datetime(2021, 3, 8, 19, 50, 40),
            ),
        )

    def test_neexistujici_rizeni(self):
        with self.assertRaisesRegex(
            SpisovaZnackaNeexistujeError, "Spisová značka 62 NC 1/2019 neexistuje"
        ):
            load_from_file(testdata_dir / "neexistuje.html")

    def test_parse_dilci_rizeni(self):
        rizeni = load_from_file(testdata_dir / "12-P-A-NC-105.html")

        self.assertEqual(
            rizeni,
            Rizeni(
                spisova_znacka="12 P A NC 105 / 2019",
                soud="Městský soud Praha\xa0>\xa0Obvodní soud Praha 9",
                stav_rizeni="Odškrtnutá - evidenčně ukončená věc (od 24.06.2019)",
                udalosti=[
                    Udalost(nazev="Zahájení řízení", datum=date(2019, 3, 8)),
                    Udalost(nazev="Vydání rozhodnutí", datum=date(2019, 3, 12)),
                    Udalost(nazev="Vyřízení věci", datum=date(2019, 3, 12)),
                    Udalost(
                        nazev="Datum pravomocného ukončení věci", datum=date(2019, 5, 7)
                    ),
                    Udalost(nazev="Skončení věci", datum=date(2019, 6, 24)),
                ],
                dilci_rizeni=[],
                posledni_zmena=datetime.datetime(2019, 6, 24, 12, 44, 54),
                cas_aktualizace=datetime.datetime(2021, 3, 8, 19, 50, 40),
            ),
        )

    def test_parse_udalost(self):
        html = """<tr>
    <td class="data">

        Senátní věc

    </td>
    <td class="data">
        <a href="search.do?org=OSPHA09&amp;cisloSenatu=12&amp;druhVec=P A NC&amp;bcVec=105&amp;rocnik=2019&amp;typSoudu=os&amp;autoFill=true&amp;type=spzn">12
            P A NC 105 / 2019</a>

    </td>
</tr>"""
        self.assertEqual(
            parse_udalost(html), DilciRizeni(spisova_znacka="12 P A NC 105 / 2019")
        )

    def test_zahajeni(self):
        rizeni = load_from_file(testdata_dir / "62-Nc-2528-2019.html")
        self.assertEqual(
            rizeni.zahajeni, Udalost(nazev="Zahájení řízení", datum=date(2019, 3, 8))
        )

    def test_skonceni(self):
        rizeni = load_from_file(testdata_dir / "62-Nc-2528-2019.html")
        self.assertEqual(
            rizeni.skonceni, Udalost(nazev="Skončení věci", datum=date(2019, 8, 8))
        )

    def test_delka_rizeni(self):
        rizeni = load_from_file(testdata_dir / "62-Nc-2528-2019.html")
        self.assertEqual(rizeni.delka_rizeni, timedelta(days=153))

    def test_set_predmet_rizeni(self):
        rizeni = load_from_file(testdata_dir / "62-Nc-2528-2019.html")
        rizeni.set_predmet_rizeni()
        self.assertEqual(
            rizeni.predmet_rizeni, "Svěření do péče a určení výživného (včetně změn)"
        )

    def test_probehlo_odvolani__false(self):
        rizeni = load_from_file(testdata_dir / "62-Nc-2528-2019.html")
        self.assertFalse(rizeni.probehlo_odvolani)

    def test_probehlo_odvolani__true(self):
        rizeni = load_from_file(testdata_dir / "62-Nc-2503-2019.html")
        self.assertTrue(rizeni.probehlo_odvolani)


class TestUdalost(TestCase):
    def test_absolute_url(self):
        u = Udalost(
            nazev="",
            datum=date(2019, 1, 1),
            url="../public/list.do?query",
        )
        self.assertEqual(
            u.absolute_url,
            "https://infosoud.justice.cz/InfoSoud/public/list.do?query",
        )

    def test_druh(self):
        u = Udalost(
            nazev="",
            datum=date(2019, 1, 1),
            url="../public/list.do?druhVec=P A NC&rocnik=2019&cisloSenatu=12&bcVec=105&kraj=null&org=OSPHA09&poradiUdalosti=1&cisloSenatuLabel=12&typSoudu=os&agendaNc=null&druhUdalosti=ZAHAJ_RIZ&idUdalosti=null&druhVecId=P A NC&rocnikId=2019&cisloSenatuId=12&bcVecId=109&orgId=OSPHA09",
        )
        self.assertEqual(u.druh, DRUH_ZAHAJENI)

    def test_parse_predmet_rizeni(self):
        with open(testdata_dir / "62-Nc-2528-2019-ZAHAJ_RIZ.html") as f:
            self.assertEqual(
                parse_predmet_rizeni(f.read()),
                "Svěření do péče a určení výživného (včetně změn)",
            )

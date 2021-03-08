from unittest import TestCase

from hlidac import (
    DilciRizeni,
    Rizeni,
    Udalost,
    parse_predmet_rizeni,
    parse_rizeni,
    parse_udalost,
)


class Test(TestCase):
    def test_hlavni_rizeni_inet(self):
        with open("62-Nc-2528-2019.html") as f:
            rizeni = parse_rizeni(f.read())

        self.assertEqual(
            rizeni,
            Rizeni(
                spisova_znacka="62 NC 2528 / 2019",
                soud="Městský soud Praha\xa0>\xa0Obvodní soud Praha 9",
                stav_rizeni="Odškrtnutá - evidenčně ukončená věc (od 08.08.2019)",
                predmet_rizeni="",
                udalosti=[
                    Udalost(nazev="Zahájení řízení", datum="08.03.2019"),
                    Udalost(nazev="Vyřízení věci", datum="08.08.2019"),
                    Udalost(nazev="Skončení věci", datum="08.08.2019"),
                ],
                dilci_rizeni=[
                    DilciRizeni(spisova_znacka="12 P A NC 105 / 2019"),
                    DilciRizeni(spisova_znacka="12 P A NC 104 / 2019"),
                ],
            ),
        )

    def test_parse_dilci_rizeni(self):
        with open("12-P-A-NC-105.html") as f:
            rizeni = parse_rizeni(f.read())

        self.assertEqual(
            rizeni,
            Rizeni(
                spisova_znacka="12 P A NC 105 / 2019",
                soud="Městský soud Praha\xa0>\xa0Obvodní soud Praha 9",
                stav_rizeni="Odškrtnutá - evidenčně ukončená věc (od 24.06.2019)",
                udalosti=[
                    Udalost(nazev="Zahájení řízení", datum="08.03.2019"),
                    Udalost(nazev="Vydání rozhodnutí", datum="12.03.2019"),
                    Udalost(nazev="Vyřízení věci", datum="12.03.2019"),
                    Udalost(
                        nazev="Datum pravomocného ukončení věci", datum="07.05.2019"
                    ),
                    Udalost(nazev="Skončení věci", datum="24.06.2019"),
                ],
                dilci_rizeni=[],
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
        with open("62-Nc-2528-2019.html") as f:
            rizeni = parse_rizeni(f.read())
        self.assertEqual(
            rizeni.zahajeni, Udalost(nazev="Zahájení řízení", datum="08.03.2019")
        )

    def test_set_predmet_rizeni(self):
        with open("62-Nc-2528-2019.html") as f:
            rizeni = parse_rizeni(f.read())
        rizeni.set_predmet_rizeni()
        self.assertEqual(
            rizeni.predmet_rizeni, "Svěření do péče a určení výživného (včetně změn)"
        )


class TestUdalost(TestCase):
    def test_absolute_url(self):
        u = Udalost(
            nazev="",
            datum="",
            url="../public/list.do?query",
        )
        self.assertEqual(
            u.absolute_url,
            "https://infosoud.justice.cz/InfoSoud/public/list.do?query",
        )

    def test_druh(self):
        u = Udalost(
            nazev="",
            datum="",
            url="../public/list.do?druhVec=P A NC&rocnik=2019&cisloSenatu=12&bcVec=105&kraj=null&org=OSPHA09&poradiUdalosti=1&cisloSenatuLabel=12&typSoudu=os&agendaNc=null&druhUdalosti=ZAHAJ_RIZ&idUdalosti=null&druhVecId=P A NC&rocnikId=2019&cisloSenatuId=12&bcVecId=109&orgId=OSPHA09",
        )
        self.assertEqual(u.druh, "ZAHAJ_RIZ")

    def test_parse_predmet_rizeni(self):
        with open("62-Nc-2528-2019-ZAHAJ_RIZ.html") as f:
            self.assertEqual(
                parse_predmet_rizeni(f.read()),
                "Svěření do péče a určení výživného (včetně změn)",
            )

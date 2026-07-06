#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genere des FAUSSES ordonnances kine (fictives, pour test/demo OCR)."""

from PIL import Image, ImageDraw, ImageFont

F = "C:/Windows/Fonts/arial.ttf"
FB = "C:/Windows/Fonts/arialbd.ttf"
FI = "C:/Windows/Fonts/ariali.ttf"


def font(p, s):
    return ImageFont.truetype(p, s)


# Chaque cas : prescripteur, patient, et lignes de prescription (corps "manuscrit")
CAS = {
    "test_ordonnance.png": {
        "medecin": "Dr Jean MOREAU", "ville": "Lyon", "date": "27/06/2026",
        "patient": "Mme Claire FONTAINE", "ne": "14/03/1968",
        "corps": [
            "Reeducation du genou DROIT suite a la pose",
            "d'une prothese totale de genou (PTG)",
            "operee le 10/06/2026.", "",
            "- 30 seances de reeducation",
            "- Bilan diagnostic kinesitherapique initial",
            "- Soins a domicile (patiente a mobilite reduite)",
        ],
    },
    "ordo_lombalgie.png": {
        "medecin": "Dr Sophie BERNARD", "ville": "Paris", "date": "20/06/2026",
        "patient": "M. Karim HADDAD", "ne": "02/11/1985",
        "corps": [
            "Reeducation dans le cadre d'une",
            "lombalgie commune non operee.", "",
            "- 10 seances de masso-kinesitherapie",
            "- Bilan diagnostic kinesitherapique",
        ],
    },
}


def generer(nom, c):
    W, H = 1000, 1400
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    big, med, reg = font(FB, 30), font(FB, 22), font(F, 22)
    small, ital, hand = font(F, 18), font(FI, 22), font(FI, 26)

    d.rectangle([20, 20, W - 20, H - 20], outline="black", width=2)
    d.text((50, 50), c["medecin"], font=big, fill="black")
    d.text((50, 95), "Medecin Generaliste", font=reg, fill="black")
    d.text((50, 125), "12 rue des Lilas", font=small, fill="black")
    d.text((50, 150), "RPPS : 10101010101", font=small, fill="black")
    d.text((650, 95), f"{c['ville']}, le {c['date']}", font=reg, fill="black")
    d.line([50, 215, W - 50, 215], fill="black", width=1)
    d.text((50, 240), f"Patient : {c['patient']}", font=med, fill="black")
    d.text((50, 275), f"Ne(e) le : {c['ne']}", font=reg, fill="black")
    d.text((400, 330), "O R D O N N A N C E", font=big, fill="black")
    d.line([50, 385, W - 50, 385], fill="black", width=1)
    d.text((70, 430), "Prescription de masso-kinesitherapie :", font=reg, fill="black")

    y = 510
    for ligne in c["corps"]:
        d.text((70, y), ligne, font=hand, fill=(20, 20, 80))
        y += 48

    d.text((620, 1180), "Signature et cachet :", font=small, fill="black")
    d.text((650, 1230), c["medecin"].replace("Dr ", "Dr "), font=ital, fill=(20, 20, 80))
    d.line([640, 1290, 920, 1290], fill="gray", width=1)
    d.text((50, 1330), "DOCUMENT FICTIF - genere pour test logiciel - aucune valeur medicale.",
           font=small, fill="gray")
    img.save(nom)
    print("Cree :", nom)


if __name__ == "__main__":
    for nom, c in CAS.items():
        generer(nom, c)

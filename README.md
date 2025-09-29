# tsoha-forum
Sovellus on Redditin kaltainen foorumi, jossa
- [X] Käyttäjä voi luoda tunnuksen ja kirjautua sisään.
- [X] Käyttäjä voi lisätä, ...
- [X] ... muokata ja ...
- [X] ... poistaa lankojen aloituksia.
- [X] Lankojen yhteydessä näkyy aikaleima.
- [ ] Kommenttien yhteydessä näkyy aikaleima.
- [ ] Käyttäjä voi lisätä kuvia aloituksiin.
- [X] Käyttäjä näkee itse ja muiden lisäämät langat.
- [ ] Käyttäjä voi etsiä lankoja hakusanoin tai tägein.
- [ ] Sovelluksessa on käyttäjäsivut, jossa näkee aloitetut langat, kommentit sekä saatujen tykkäysten yhteismäärän.
- [X] Käyttäjä voi luokitella lankoja tägeillä.
- [ ] Käyttäjä voi kommentoida omia ja muiden tekemiä lankoja, sekä tykätä aloituksista ja kommenteista.

## Sovelluksen asennus

Asenna 'flask' -kirjasto:

```
$ pip install flask
```

Luo tietokannan taulut:

```
$ sqlite3 database.db < schema.sql
```

Voit käynnistää sovelluksen näin:

```
$ flask run
```

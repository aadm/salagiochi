---
title: Invia un Punteggio
layout: submit
---

Compila il modulo: si aprirà una issue sul repository GitHub con tutti i dati già
scritti. Trascina la foto dello schermo o lo screenshot nel corpo della issue e
premi "Submit new issue".

{{< submit-form >}}

## Come funziona

1. Compila il modulo qui sopra.
2. Si apre una nuova issue su GitHub con il punteggio già compilato.
3. Trascina la foto o lo screenshot nel campo di testo della issue.
4. Premi "Submit new issue".
5. La classifica si aggiorna da sola in pochi minuti.

La foto caricata nell'issue viene scaricata, ridotta (1600 pixel, JPEG) e salvata
nel sito in automatico: non devi preparare nulla. Senza foto, la prova resta il
link all'issue.

## Aggiungere un punteggio a mano

Se preferisci, puoi saltare la issue e aggiornare direttamente la classifica.
Serve modificare un solo file: `data/scores.yml` nel repository GitHub (anche
dalla pagina web del repo, senza scaricare nulla).

1. **Prepara la foto.** Hugo copia i file così come sono e non ridimensiona
   niente. Le foto hanno dimensioni molto diverse tra loro: una foto dall'iPhone
   può essere 4000x3000 pixel e pesare megabyte, uno screenshot di un emulatore
   (RetroArch) è tipicamente 1920x1080 ma in PNG può pesare altrettanto, mentre
   una foto passata da WhatsApp arriva già compressa e va bene quasi sempre. Per
   il sito bastano 1600 pixel sul lato lungo e una qualità JPEG media (il file
   scende a poche centinaia di KB).

```bash
python scripts/optimize_photo.py foto.jpg static/proof/mariobros-strmnk-2026-07-18.jpg
```

   Se non hai Pillow installato, va bene anche ImageMagick:

```bash
convert foto.jpg -resize 1600x1600\> -strip -quality 82 static/proof/mariobros-strmnk-2026-07-18.jpg
```

   La foto va salvata in `static/proof/` e compare sul sito all'indirizzo
   `/salagiochi/proof/...`. Se usi la pagina web del repository (senza scaricare
   nulla), trascina la foto già ridotta nella cartella `static/proof/`.

2. **Modifica `data/scores.yml`** e aggiungi una voce alla sezione del gioco (il
   percorso foto va senza la slash iniziale):

```yaml
    entries:
      - player: strmnk
        score: 87400
        date: 2026-07-18
        proof: proof/mariobros-strmnk-2026-07-18.jpg
```

In `proof` va il link alla prova: il percorso della foto locale (senza la slash
iniziale) oppure un URL di issue GitHub. Il nome del gioco va indicato con lo
stesso nome della sezione `games`.

Il punteggio viene caricato così com'è: siamo grandi e ci fidiamo l'uno
dell'altro.
# Disclaimer

Deze software wordt aangeboden zoals deze is, zonder enige vorm van garantie. Het gebruik van deze applicatie is volledig op eigen risico. De maker aanvaardt geen enkele aansprakelijkheid voor directe of indirecte schade, verlies van gegevens, of andere gevolgen die voortvloeien uit het gebruik van deze app, ongeacht de oorzaak daarvan. Door deze software te gebruiken, stemt u ermee in dat u de volledige verantwoordelijkheid draagt voor eventuele gevolgen.

# Presentatie Overlay App

Deze applicatie biedt een transparante overlay voor presentaties, waarmee je eenvoudig tekstslides en een logo over je scherm kunt tonen. Ideaal voor docenten, sprekers of iedereen die tijdens een presentatie extra informatie zichtbaar wil maken zonder het hoofdscherm te blokkeren.

## Gebouwd met Cursor.ai

## Functionaliteit
- **Transparante overlay:** Toont tekstslides en een logo over elk ander venster.
- **Slides beheren:** Slides en instellingen worden ingeladen uit het bestand `slides.txt`.
- **Logo:** Ondersteunt SVG-logo (standaard `Avans.svg`).
- **Schaalbaarheid:** Pas de schaal van tekst en logo aan via het configuratiegedeelte in `slides.txt`.
- **Transparantie:** Stel de transparantie van de achtergrond in.
- **Click-through:** Maak de overlay muisklik-doorlatend ("click-through") met een sneltoets.
- **Systeemvak:** Bedien de overlay via een systeemvak-icoon.

## Installatie
1. **Clone of download dit project.**
2. **Maak een virtuele omgeving aan (optioneel, aanbevolen):**
   ```sh
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. **Installeer de vereiste pakketten:**
   ```sh
   pip install -r requirements.txt
   ```
4. **(Optioneel) Bouw een standalone .exe:**
   ```sh
   pyinstaller overlay_text.py --onefile --noconsole --add-data "Avans.svg;."
   # Of gebruik build_overlay.bat
   Je moet de slides.txt copieren naar de dist map!!
   ```

## Gebruik
1. **Slides voorbereiden:**
   - Bewerk `slides.txt` om je slides en instellingen aan te passen.
   - Eerste regels: schaal, transparantie, marges, logo-schaal (zie voorbeeld in `slides.txt`).
   - Daarna: elke slide gescheiden door een lege regel, eerste regel is de titel, daarna bullets met `-` of `*`.
2. **Start de overlay:**
   - Via `python overlay_text.py` of de gegenereerde `.exe` in de map `dist/`.
3. **Bediening:**
   - Gebruik pijltjestoetsen (links/rechts) om slides te wisselen.
   - `Esc` sluit de overlay.
   - `Home`/`End` naar eerste/laatste slide.
   - `T` of `Ctrl+Alt+T` (globale sneltoets) schakelt click-through aan/uit. Werkt bij mij niet
   - Via het systeemvak-icoon kun je de overlay sluiten of click-through wisselen. Werkt bij mij wel

## Tips
- **Logo aanpassen:** Vervang `Avans.svg` door je eigen logo (SVG aanbevolen).
- **Slides dynamisch aanpassen:** Pas `slides.txt` aan en herstart de app voor nieuwe slides.
- **Click-through:** Handig als je wilt klikken op onderliggende vensters zonder de overlay te sluiten.
- **Problemen met sneltoetsen?** Installeer het `keyboard`-pakket met administratorrechten.

## Vereisten
- Windows 10/11 (andere platforms mogelijk met aanpassingen)
- Python 3.8+
- Zie `requirements.txt` voor benodigde Python-pakketten

## Bekende beperkingen
- Click-through werkt alleen op Windows.
- Sneltoetsen via het `keyboard`-pakket vereisen soms adminrechten.
- Alleen getest met SVG-logo's.

## Contact
Voor vragen of suggesties: open een issue of neem contact op met de maker. 
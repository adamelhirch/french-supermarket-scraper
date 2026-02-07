# Setup CapSolver sur ton PC Local

Le VPS est bloqué car Leclerc détecte les IPs datacenter. Il faut lancer le scraper **depuis ton PC**.

## 🖥️ Installation sur ton PC

### 1. Prérequis
```bash
# Python 3.8+
python --version

# Installer les dépendances
pip install playwright
python -m playwright install chromium
```

### 2. Télécharger le scraper
```bash
# Clone le repo
git clone https://github.com/adamelhirch/french-supermarket-scraper.git
cd french-supermarket-scraper

# Créer un virtualenv
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Installer les deps
pip install -r requirements.txt
```

### 3. Copier les cookies
Télécharge `leclerc_drive_cookies_updated.json` depuis le VPS et mets-le dans le dossier.

### 4. Trouver le chemin de l'extension CapSolver

**Windows:**
```
C:\Users\<TON_USER>\AppData\Local\Google\Chrome\User Data\Default\Extensions\
```

**macOS:**
```
~/Library/Application Support/Google/Chrome/Default/Extensions/
```

**Linux:**
```
~/.config/google-chrome/Default/Extensions/
```

Cherche le dossier qui correspond à CapSolver (identifiant commençant par des lettres aléatoires).

### 5. Script de test

Crée `test_local_capsolver.py` :

```python
import asyncio
from playwright.async_api import async_playwright
import json

# ⚠️ CHANGE CE CHEMIN !
CAPSOLVER_EXTENSION_PATH = r"C:\Users\...\Extensions\pabjfbciaedomjjfelfafejkppknjleh\1.0.0_0"

async def test_with_capsolver():
    print("🧪 Testing CapSolver on Leclerc Drive\n")
    
    with open('leclerc_drive_cookies_updated.json') as f:
        cookies = json.load(f)
    
    async with async_playwright() as p:
        # Launch Chrome with CapSolver extension
        browser = await p.chromium.launch_persistent_context(
            user_data_dir='./chrome_profile',
            headless=False,  # MUST be False
            args=[
                f'--disable-extensions-except={CAPSOLVER_EXTENSION_PATH}',
                f'--load-extension={CAPSOLVER_EXTENSION_PATH}',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        # Add cookies
        await browser.add_cookies(cookies)
        page = await browser.new_page()
        
        url = 'https://fd7-courses.leclercdrive.fr/magasin-123111-123111-Montaudran/recherche.aspx?TexteRecherche=riz'
        
        print(f"🔗 Going to: {url}")
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        
        print("\n⏳ Waiting for CapSolver to solve CAPTCHA (30s)...")
        await asyncio.sleep(30)
        
        # Check results
        text = await page.evaluate('() => document.body.innerText')
        title = await page.title()
        
        print(f"\n📄 Title: {title}")
        print(f"📏 Text length: {len(text)} chars\n")
        
        if 'restricted' in text.lower():
            print("❌ Still blocked by CAPTCHA")
        elif len(text) > 1000:
            print("✅ SUCCESS! Products loaded!")
            print(f"\nFirst 500 chars:\n{text[:500]}")
        else:
            print("⚠️ Unclear status")
            print(text[:300])
        
        print("\n⏸️ Browser stays open for inspection...")
        await asyncio.sleep(60)
        
        await browser.close()

asyncio.run(test_with_capsolver())
```

### 6. Lance le test
```bash
python test_local_capsolver.py
```

Chrome va s'ouvrir avec CapSolver, naviguer vers le Drive, et l'extension devrait résoudre le CAPTCHA automatiquement.

## 📊 Si ça marche

Une fois que CapSolver a résolu le CAPTCHA et que les produits s'affichent, on pourra :
1. Créer un scraper Drive complet
2. L'utiliser depuis ton PC
3. Optionnellement : créer une API locale que le VPS peut appeler

## 🔑 Alternative : API CapSolver

Si tu as une API key CapSolver, on peut aussi utiliser leur API directement sans extension (fonctionne sur le VPS).

Dis-moi comment ça se passe ! 🦾

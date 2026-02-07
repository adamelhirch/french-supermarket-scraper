# CapSolver Setup for Leclerc Drive

Adam a CapSolver (extension Chrome) qui peut bypass DataDome CAPTCHA.

## Approche

**Option 1: Playwright + CapSolver Extension** (recommandé)
- Lancer Chrome en mode non-headless
- Charger l'extension CapSolver
- Laisser l'extension résoudre le CAPTCHA automatiquement
- Scraper ensuite normalement

**Option 2: API CapSolver**
- Utiliser l'API CapSolver pour résoudre le CAPTCHA
- Plus complexe mais automatisable

## Prérequis CapSolver

1. **Extension ID**: Récupérer le chemin de l'extension Chrome
2. **API Key**: Si on utilise l'API

## Test

Pour tester si CapSolver fonctionne, on doit :
1. Lancer Chrome NON-headless avec l'extension
2. Naviguer vers le Drive
3. Attendre que CapSolver résolve le CAPTCHA
4. Scraper les produits

## Limitations

- **Non-headless requis** : Chrome doit avoir une interface graphique
- **VPS**: Nécessite Xvfb (déjà installé sur ce serveur)
- **Lenteur**: Résoudre un CAPTCHA prend 10-30 secondes

## Alternative

Si CapSolver extension ne marche pas sur VPS:
- Utiliser l'API CapSolver directement
- Ou setup un service local sur la machine d'Adam avec Chrome + extension

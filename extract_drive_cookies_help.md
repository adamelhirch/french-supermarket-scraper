# Extraction de cookies pour Leclerc Drive

Le Drive Leclerc est sur un domaine différent (fd7-courses.leclercdrive.fr) donc il faut extraire les cookies spécifiques au Drive.

## 📋 Étapes :

1. **Ouvre ton navigateur** et va sur :
   ```
   https://fd7-courses.leclercdrive.fr/magasin-123111-123111-Montaudran/
   ```

2. **Connecte-toi / sélectionne ton magasin** si nécessaire

3. **Ouvre DevTools** (F12)

4. **Va dans l'onglet Console** et exécute :
   ```javascript
   copy(JSON.stringify(document.cookie.split('; ').map(c => {
     const [name, value] = c.split('=');
     return {
       name: name,
       value: value,
       domain: '.leclercdrive.fr',
       path: '/',
       secure: true,
       httpOnly: false,
       sameSite: 'Lax'
     };
   }), null, 2));
   ```

5. **Les cookies sont dans ton presse-papier**

6. **Envoie-moi le JSON** et je le teste !

## Alternative : Extension EditThisCookie

1. Installe l'extension "EditThisCookie"
2. Va sur le site du Drive
3. Clique sur l'icône EditThisCookie
4. Clique "Export" (copie tous les cookies en JSON)
5. Envoie-moi le résultat

---

Une fois que j'ai tes cookies du Drive, je pourrai tester si ça bypass le DataDome CAPTCHA.

<p align="right"><a href="./README.md">English</a> | <b>Français</b></p>

<h1 align="center">Presentation Forge</h1>

<p align="center">
  <b>Décrivez votre présentation à Claude. Il rédige les slides et les assemble dans un unique <code>index.html</code> portable que vous pouvez double-cliquer, envoyer par mail ou héberger n'importe où.</b>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-22c55e?style=for-the-badge" alt="License MIT"></a>
  <img src="https://img.shields.io/badge/claude-skill-d97757?style=for-the-badge" alt="Claude Skill">
  <img src="https://img.shields.io/badge/sortie-fichier%20unique-2563eb?style=for-the-badge" alt="Fichier unique">
  <img src="https://img.shields.io/badge/python-stdlib%20seule-f59e0b?style=for-the-badge" alt="Python stdlib seule">
</p>

<p align="center">
  <a href="#pourquoi">Pourquoi</a> •
  <a href="#ce-quil-sait-faire">Ce qu'il sait faire</a> •
  <a href="#installation">Installation</a> •
  <a href="#exemple">Exemple</a> •
  <a href="#fonctionnement">Fonctionnement</a> •
  <a href="#thèmes">Thèmes</a>
</p>

---

## C'est quoi ?

Un skill [Claude](https://claude.com) qui transforme du langage naturel en présentations soignées, nativement web. Vous dites *"fais-moi une présentation sur X"* ; Claude structure le deck, rédige une slide par fichier HTML, choisit ou construit un thème, et compile le tout dans un unique **`index.html` autonome**. Le moteur, le thème, les polices et les images sont tous embarqués : le fichier s'ouvre d'un double-clic, s'envoie proprement par mail et fonctionne entièrement hors ligne. Pas de framework, pas de serveur de build, aucune dépendance d'exécution.

C'est un **Agent Skill** : un seul dossier qui fonctionne partout où Claude dispose d'un système de fichiers et de Python. Le même skill tourne dans **Claude Code**, les **apps Claude** (claude.ai et desktop) et via l'**API**. Aucune commande à retenir, il suffit de demander.

## Pourquoi

Faire un deck à l'ancienne, c'est se battre avec ses outils avant même d'avoir écrit une idée. Presentation Forge inverse la logique : vous apportez le contenu, Claude s'occupe de la forme.

| Sans Presentation Forge | Avec Presentation Forge |
| :---------------------- | :---------------------- |
| Ouvrir PowerPoint ou Keynote, batailler avec les mises en page et les masques | Décrire la présentation en une phrase et récupérer un deck structuré |
| Les polices et le style cassent dès que le fichier change de machine | Tout embarqué dans un seul `index.html` au rendu identique partout |
| Partager rime avec pièce jointe lourde ou compte cloud | Envoyer un seul fichier HTML, ou l'héberger en page statique |
| "Reprends juste le template de la boîte" vire à l'après-midi de copier-coller | Importer une charte une fois, l'enregistrer, la réappliquer en quelques secondes |
| Notes, révélation progressive et vue présentateur sont des bricolages | Intégrés d'office : mode présentateur, révélation pas à pas, navigation clavier |
| Le deck est un binaire opaque, impossible à versionner proprement | Du HTML lisible, modifiable et suivi dans git |

Résultat : un deck **portable** (un seul fichier), **professionnel** (vraie typographie, thème cohérent) et **modifiable** (HTML lisible, zéro verrou propriétaire).

## Ce qu'il sait faire

- **Transformer n'importe quel brief en deck.** Un sujet, un plan, des notes en vrac ou un document entier. Talks techniques, cours, pitchs, conférences, tout sujet confondu.
- **Écrire des slides qui font mouche.** Titres en assertion, une idée par slide, puces serrées, mises en page deux colonnes, encarts, citations et blocs de code propres. Les pavés de texte vont dans les notes, pas à l'écran.
- **Présenter comme un pro.** Mode présentateur intégré avec notes et minuteur, révélation progressive (`fragment`) pour dérouler un point pas à pas, et navigation clavier complète. Touche `?` pour les raccourcis.
- **Rester dans la charte.** Des thèmes interchangeables gardent couleurs, typo et espacements cohérents. Changez le look sans toucher une seule slide.
- **Importer une charte.** Recréer une identité visuelle en thème réutilisable depuis un **PowerPoint** (`.pptx`), une **image** (slide ou maquette de marque) ou une simple **description texte**, et intégrer un **logo d'entreprise**.
- **Enregistrer un style une fois, le réutiliser à l'infini.** Tout thème s'exporte en un unique fichier portable **`.pfstyle.json`**. Redonnez ce fichier dans n'importe quelle conversation future pour recréer exactement le même look, à l'octet près, sans le PowerPoint ni l'image d'origine.
- **Livrer un fichier unique.** Un seul `index.html`, prêt hors ligne, sans dépendance, qui s'ouvre partout où un navigateur existe.

## Installation

C'est un [skill Claude](https://docs.claude.com/en/docs/claude-code/skills) classique : un dossier contenant un `SKILL.md` que Claude charge automatiquement quand c'est pertinent. Installez-le une fois sur chaque surface où vous le voulez.

### Claude Code

Déposez le skill dans votre dossier de skills, Claude le détecte tout seul :

```bash
git clone https://github.com/thmsgo18/presentation-forge.git ~/.claude/skills/presentation-forge
```

Pour un seul projet, clonez plutôt dans `.claude/skills/presentation-forge/` au sein du dépôt concerné.

### Apps Claude (claude.ai et desktop)

Importez **`dist/presentation-forge-skill.zip`** dans **Réglages → Fonctionnalités → Skills** (nécessite Pro, Max, Team ou Enterprise avec l'exécution de code activée). Demandez ensuite une présentation à Claude.

### API

Importez le même `dist/presentation-forge-skill.zip` via l'API Skills (`/v1/skills`) et référencez-le depuis le conteneur d'exécution de code.

> Les skills personnalisés ne se synchronisent pas entre surfaces. Importez le zip une fois par surface où vous le voulez.

## Exemple

```
Vous : Fais une présentation HTML sur nos résultats du T3 pour la réunion
       d'équipe. Cinq minutes, ton positif. À retenir : chiffre d'affaires
       +18%, churn redescendu à 4%, deux nouveaux clients grands comptes.
       Utilise notre charte, voici le template du trimestre dernier (.pptx).

Claude : [importe la charte du .pptx en thème réutilisable, structure le
         deck, rédige une slide de titre, un sommaire, trois slides de
         contenu menées par une assertion avec leurs notes, et une slide
         de conclusion avec le message clé, puis compile en un index.html]

         C'est fait. Votre deck est dans t3-reunion/index.html (7 slides).
         Ouvrez-le et pressez p pour le mode présentateur, les flèches pour
         naviguer, ? pour tous les raccourcis. J'ai aussi enregistré le
         thème dans acme.pfstyle.json pour réutiliser ce look au T4.
```

## Fonctionnement

Trois couches, toujours séparées, pour qu'un deck ne casse jamais quand on le re-thème :

- **moteur** (`template/engine/`) : rendu, mise à l'échelle, navigation, mode présentateur, révélation progressive. Jamais modifié pour changer le contenu ou le look.
- **thème** (`template/themes/<nom>/`) : le look. Couleurs, typo, espacements, polices, logos, fonds.
- **contenu** (`slides/`) : les slides, un fichier HTML chacune, ordonnées par nom.

Le pipeline est volontairement banal, et c'est ce qui le rend portable :

1. Choisir un dossier cible et y copier le template.
2. Configurer `deck.config.json` (titre, langue, thème, transition).
3. Écrire les slides dans `slides/`, une `<section class="slide">` par fichier, numérotées `01-`, `02-`, ...
4. Lancer `python3 build.py`. Il embarque le moteur, le thème, les polices et chaque image, puis écrit un unique `index.html`.
5. L'ouvrir, le présenter, le partager. Ajoutez `--watch` pour reconstruire à chaque sauvegarde.

Les slides sont composées sur un canevas fixe **1920x1080** que le moteur met à l'échelle de n'importe quel écran : un deck rend pareil sur un portable, un vidéoprojecteur ou un téléphone. Le contrat de rédaction complet et le guide des thèmes sont dans [`SKILL.md`](SKILL.md) et [`reference/`](reference/).

## Thèmes

Un thème est un dossier autonome (`tokens.css`, `fonts.css`, `slides.css`, plus `fonts/`, `images/`, `logos/`). Chaque thème définit les mêmes noms de tokens et stylise les mêmes classes de slide, donc changer de thème ne casse jamais un deck.

Vous pouvez construire un thème à partir d'une charte de quatre façons :

| Source | Ce que fait Claude |
| :----- | :----------------- |
| PowerPoint `.pptx` | Extrait la palette, les polices, les médias embarqués et la géométrie du masque |
| Image (slide ou maquette) | Échantillonne les couleurs dominantes exactes, lit la typo et la mise en page à l'œil |
| Description texte | Traduit les mots de la marque en tokens de design |
| `.pfstyle.json` | Reconstruit le thème entier (CSS, polices, logos, fonds) en une étape |

Quelle que soit la source, le thème s'exporte en un unique fichier portable **`.pfstyle.json`**. Gardez ce fichier et vous recréez exactement la même identité dans n'importe quelle conversation future, sans aucun fichier d'origine. Procédure complète dans [`reference/import-theme.md`](reference/import-theme.md).

## Prérequis

- Un client Claude qui supporte les skills ([Claude Code](https://docs.claude.com/en/docs/claude-code), les apps Claude ou l'API).
- **Python 3**, bibliothèque standard uniquement, pour construire les decks et lire les `.pptx`. Rien d'autre à installer.
- Un navigateur pour voir le résultat. C'est tout.

## Licence

[MIT](LICENSE) © Thomas Gourmelen

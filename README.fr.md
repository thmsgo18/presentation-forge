# Presentation Forge

Créez des présentations en HTML propre et lisible.

Presentation Forge est un petit moteur de slides sans aucune dépendance. Vous
écrivez chaque slide en HTML simple et sémantique ; le moteur s'occupe de la
mise à l'échelle, de la navigation, du compteur de slides, de l'impression en
PDF et de la génération d'un fichier unique et portable. Aucun framework à
apprendre, rien à compiler — ouvrez une présentation dans un navigateur, c'est
prêt.

*[English version](README.md)*

## Pourquoi

- **Lisible.** Une présentation, ce sont des `<section class="slide">` avec du
  contenu ordinaire à l'intérieur. Toute personne à l'aise avec le HTML s'y
  retrouve.
- **Cohérent.** Un thème fournit les jetons de design et le style des blocs :
  toutes les slides restent harmonieuses sans réglage au cas par cas.
- **Portable.** Une étape de build regroupe tout dans un seul fichier `.html` à
  envoyer par mail, héberger n'importe où, ou ouvrir d'un double-clic.
- **Sans dépendances.** Le moteur tient dans un fichier JavaScript vanilla ; le
  bundler dans un fichier Python n'utilisant que la bibliothèque standard.

## Démarrage rapide

```sh
git clone https://github.com/thmsgo18/presentation-forge.git
cd presentation-forge
open examples/starter/index.html      # ou double-cliquez dessus
```

Utilisez les flèches (ou Espace) pour parcourir les slides.

Pour produire un fichier unique partageable :

```sh
python3 build.py examples/starter/index.html
# -> dist/starter.html
```

## Organisation du projet

```
presentation-forge/
├── src/
│   ├── engine/
│   │   └── deck-stage.js     # le moteur de présentation (un fichier, zéro dépendance)
│   └── themes/
│       ├── base.css          # mécanique uniquement : échelle, disposition, impression
│       └── ink-blue.css      # un thème sobre bleu / encre (couleurs, polices, typo)
├── examples/
│   └── starter/
│       └── index.html        # une présentation de démo montrant chaque type de slide
├── docs/
│   └── writing-slides.md     # comment écrire une présentation
└── build.py                  # regroupe une présentation en un seul .html portable
```

## Écrire une présentation

Voir [docs/writing-slides.md](docs/writing-slides.md). En résumé : une
présentation est un `<deck-stage>` contenant des `<section class="slide">`,
écrites sur un canevas fixe de 1920×1080 que le moteur met à l'échelle pour
remplir n'importe quel écran.

## Licence

[MIT](LICENSE) © Thomas Gourmelen

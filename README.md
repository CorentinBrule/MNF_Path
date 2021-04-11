# MNF Path
 
MNF Path est une famille de police _stroke line_, dessinée à partir de [Manifont Grotesk Book](https://github.com/Interstices-/Manifont-Grotesk). Elle facilite la création de gcode pour ~~l'impression~~ l'inscription sur table traçante (CNC) depuis n'importe quel logiciel de mise en page.

```
PAO -> .svg -> .gcode
```

## Une fonte pour l'inscription

Dans l'héritage des techniques d'*impression*, les formats de fontes standards (.otf, .ttf) définissent les glyphes par des contours. Ces courbes marquent la frontière entre ce qui est imprimé et ce qui est épargné. Chaque glyphe est donc une forme étanche.

À l'inverse, on peut dessiner des lettres en déplaçant un outil qui laissera une trace sur un support. Dans ce cas les glyphes ne sont plus définies par leurs contours mais par leurs squelette, qui devient le chemin de l'outil. On parlera donc d'*inscription*.

Il y a donc une incompatiblité entre les formats de fonte et leur utilisation avec un dispostif d'inscription. Le pis-aller actuels est de tracer le contour et/ou à remplir la forme de la lettre par des hachures. Dans un cas, le rendu visuel est altéré et dans l'autre, le chemin donc le temps de dessin est allongé. Une autre approche est de déléguer la gestion du texte à un outil externe et spécifique qui générera directement un chemin. Ces solutions n'ont pas la puissance des outils de mises en page auquel nous sommes habitué·e·s.

Pour profiter des avantages des logiciels de PAO tout en utilisant l'inscription, nous avons fait le choix d'utiliser ces formats de fontes en contournant leurs contraintes. On utilise les contours de MNF_Path.otf comme le squelette des glyphes qui seront utilisés comme les futurs chemins à suivre par le feutre. Avec ce principe, c'est le diamètre du feutre qui définit maintenant la graisse de la police. Les glyphes sont donc bien des formes étanches mais leur tracé se fond dans l'épaisseur de l'outil pour ressembler à une _single line_, en limitant au maximum les doubles passages inutiles. 
 
## MNF PATH 5 -> 0

MNF Path comporte 6 déclinaisons allant de 5 à 0 en fonction de l'échelle de l'impression et de la taille du feutre. La version 5 correspond à la (5)tructure (squelette) de la lettre, calqué sur la typographie ManifontGrosteskBook. La version 0 pour (0)ptique, corrige les aberrations (déformations) de la graisse apparaissant avec un feutre épais.
 
## Usage de la fonte
 
- Installer les polices.
- Mettre en page en prévisualisant le résultat avec des réglages du style de texte:

    - strock = épaisseur de votre feutre
    - no fill
    - angles ronds
    - terminaisons arrondies

- Export vectoriel -> .svg/.eps/...
- Conversion en .gcode : Inkscape avec l'extension [Gcodetools](https://github.com/cnc-club/gcodetools)
- Envoie à votre CNC avec le logiciel de votre choix

## Ce dépôt

Ce dépôt comprend  le script permettant de générer la fonte par l'interpolation entre deux tracés pour chaque glyphes ainsi que la réglages fin de quelques métriques.

```
fonts/
print/
sources/
  glyphes/                     # sources .svg
  sfd/                         # sources Fontforge temporaires
  build_MNF_path.py            # script de génération des fontes
  interpolated_fonts.py        # bibliothèque d'interpolation et de génération de fonte
  ManifontsGroteskBook.sfd     # source Fontforge de la typo de base
  requirements.txt
```

## To Do

- script suppression double passage
- séparation des réglages du script dans un fichier de config


--------------------------------------------------------------------
 
## installation
 
### fontforge version
 
this working with the current version in ubuntu's archives : `20190801` with `python3-fontforge`
```
sudo apt install fontforge python3-fontforge
```
### python other libraries
 
with virtualenv :
```
virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r requirements.txt
```
 
pip requirements :
- svg.path
 
## usage
 
`python build_MNF_path.py`

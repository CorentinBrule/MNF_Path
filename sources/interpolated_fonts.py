#!/usr/bin/env python3
# coding=utf-8

import os
import shutil
import argparse

import fontforge
import xml.dom.minidom as minidom
from svg.path import parse_path, Path, Line, CubicBezier, QuadraticBezier, Close, Move

# configuration du parser
SVGMODEL = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
   <svg
      xmlns:dc="http://purl.org/dc/elements/1.1/"
      xmlns:cc="http://creativecommons.org/ns#"
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:svg="http://www.w3.org/2000/svg"
      xmlns="http://www.w3.org/2000/svg"
      xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
      xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
      viewBox="0 -250 545 1000"
      version="1.1"
      >
   </svg>
   """


def get_all_svg_files(path, extension=".svg"):
    return [os.path.join(dp, f) for dp, dn, filenames in os.walk(path) for f in filenames if os.path.splitext(f)[1] == extension]


def sfd2otf(font_file):
    print("generate : " + font_file.split(".sfd")[0] + ".otf")
    font = fontforge.open(font_file)
    font.generate(font_file.split(".sfd")[0] + ".otf")
    print("done")


def get_svg_layer(xml, layerName):
    groups = xml.getElementsByTagName('g')
    # print(layerName)
    for g in groups:
        if g.getAttribute("inkscape:label") == layerName:
            # print(g.toxml("utf-8"))
            # print(g.getAttribute("inkscape:label") == layerName)
            return g


def interpolate_paths(structure, optique, step):
    parsed_structure = parse_path(structure)
    parsed_optique = parse_path(optique)
    parsed_pathinter = Path()
    if len(parsed_structure) == len(parsed_optique):
        for i in range(len(parsed_structure)):
            e_min = parsed_structure[i]
            e_max = parsed_optique[i]
            if type(e_min) == type(e_max):
                if type(e_min) == Move:
                    parsed_pathinter.append(Move(to=lerp(e_min.start, e_max.start, step)))
                elif type(e_min) == Line:
                    parsed_pathinter.append(
                        Line(start=lerp(e_min.start, e_max.start, step), end=lerp(e_min.end, e_max.end, step)))
                elif type(e_min) == Close:
                    parsed_pathinter.append(
                        Close(start=lerp(e_min.start, e_max.start, step), end=lerp(e_min.end, e_max.end, step)))
                else:
                    print("paths contain unknow element: " + str(type(e_min)))
                    exit()
            else:
                print("path element n°" + str(i) + " types not similar :")
                print("structure : " + str(e_min) + "-->" + str(type(e_min)))
                print("optique :" + str(e_max) + "-->" + str(type(e_max)))
                exit()
        return parsed_pathinter
    else:
        print("number of path element not similar : "+str(len(parsed_structure))+" != "+str(len(parsed_optique)))


def lerp(pA, pB, v, m=0, M=1):
    xA = pA.real
    yA = pA.imag
    xB = pB.real
    yB = pB.imag
    xC = mapping(v, m, M, xA, xB)
    yC = mapping(v, m, M, yA, yB)
    return complex(xC, yC)


def mapping(value, leftMin, leftMax, rightMin, rightMax):
    left_span = leftMax - leftMin
    right_span = rightMax - rightMin
    value_scaled = float(value - leftMin) / float(left_span)
    return rightMin + (value_scaled * right_span)


def integrate_contour_in_font(font, unicodepoint, svg_file):
    glyph = font.createChar(unicodepoint)

    # remove all points of the glyph
    fore = glyph.foreground
    for k in range(len(fore)):
        fore[k] = fontforge.contour()
    glyph.foreground = fore
    glyph.importOutlines(svg_file)


def generate_diacritique(font, accent_offset_percent, composite_glyphs_to_ignore):
    print(accent_offset_percent)
    accent_offset = accent_offset_percent
    fontforge.setPrefs("AccentOffsetPercent", accent_offset)

    '''composites glyphs'''
    font.selection.all()
    for glyph_to_ignore in composite_glyphs_to_ignore:
        font.selection.select(("less", None), glyph_to_ignore)
    font.build()

def build_interpolated_fonts(svg_files, original_font_file, individual_glyph_folder, styles, weights, accent_offset_percents, composite_glyphs_to_ignore):

    '''fontforge global settings'''
    fontforge.loadPrefs()

    if len(weights) == 0:
        accent_offset = 8
    fontforge.setPrefs("AccentOffsetPercent", 8)

    fontforge.setPrefs("AccentCenterLowest", 0)
    fontforge.setPrefs("CharCenterHighest", 0)
    fontforge.savePrefs()

    if not os.path.exists(individual_glyph_folder):
        os.mkdir(individual_glyph_folder)

    print(original_font_file)
    print(svg_files)

    '''create all font files'''
    font_files = []
    for style in styles:
        new_font_file = original_font_file.split(".")[0] + "-" + style + "." + original_font_file.split(".")[-1]
        shutil.copy(original_font_file, new_font_file)
        font_files.append(new_font_file)

    for svgFile in svg_files:
        print("--------------- new char from svgfile -------------------")
        print(svgFile)
        if svgFile.split(".")[-1] != "svg":
            print("this is not a svg !!!!")

        svg_dom = minidom.parse(svgFile)
        # print(svg_dom.toxml("utf-8"))
        svg_dom = svg_dom.getElementsByTagName("svg")[0]

        # get contours on svg file
        layerMin = get_svg_layer(svg_dom, "structure")
        layerMax = get_svg_layer(svg_dom, "optique")

        # print(structure.toxml("utf-8"))
        # print(svglyphlayers[0].getAttribute("inkscape:label"))

        ''' find glyph name and its codepoint '''

        str_glyph = svgFile.split("/")[-1].split("_")[0]
        glyph_name = str_glyph
        unicodepoint = fontforge.unicodeFromName(glyph_name)
        print(glyph_name)
        print(unicodepoint)

        for i, style in enumerate(styles):
            print("------------------- new font -----------------")
            style_step = 1.0 / (len(styles) - 1.0) * i
            print(style_step)
            # create or open fonts by styles

            tmp_svg = minidom.parseString(SVGMODEL)  # attention, le model casse tout ! il faut repartir du svg de la glyphe !

            ''' interpolate contours '''

            for j, elementMin in enumerate(layerMin.getElementsByTagName("path")):
                tmp_element = elementMin.cloneNode(1)

                structure = layerMin.getElementsByTagName("path")[j]
                optique = layerMax.getElementsByTagName("path")[j]

                if structure.getAttribute("transform") or optique.getAttribute("transform"):
                    print("Warning, there is a translation in this path !")
                    #exit()

                dMin = structure.getAttribute("d")
                dMax = optique.getAttribute("d")
                #print(structure)
                #print(optique)
                print("--------- interpolate ---------")
                interpolated_path = interpolate_paths(dMin, dMax, style_step).d()  # temporaire

                #print(interpolated_path)
                # print(tmp_element.toxml("utf-8"))
                tmp_element.setAttribute("d", interpolated_path)
                tmp_element.setAttribute("style", "fill:#000000;fill-opacity:1;stroke:none;")
                # print(tmp_element.getAttribute("d"))
                # print(tmp_element.toxml("utf-8"))
                tmp_svg.getElementsByTagName("svg")[0].appendChild(tmp_element)

            ''' save contour in temporary svg file '''
            tmp_svg_file = individual_glyph_folder + glyph_name + style + ".svg"
            with open(tmp_svg_file, 'wb') as f:
                f.write(tmp_svg.toxml("utf-8"))

            ''' integration contour in font '''
            font = fontforge.open(font_files[i])

            integrate_contour_in_font(font, unicodepoint, tmp_svg_file)

            font.save()
            print("save : " + font_files[i])
            #newFont.close()

    ''' individual font settings '''
    for i, fontFile in enumerate(font_files):
        font = fontforge.open(fontFile)

        generate_diacritique(font, accent_offset_percents[i], composite_glyphs_to_ignore)

        # OS2 Weight -> graisse
        font.os2_weight = weights[i]  # 0=100 5 = 900
        font.fontname += styles[i]
        font.fullname += styles[i]
        font.weight = styles[i]

        font.save()
        #font.close()

    print(font_files)
    return font_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--svg", help="svg_font source file(s) or folder(s)", nargs="+")
    parser.add_argument("-f", "--font", help="font source file")
    parser.add_argument("-g", "--individualGlyphFolder", help="folder to save individual glyphs used in font")
    parser.add_argument("--styles", help="name of the styles to be used for interpolation", nargs='+')
    parser.add_argument("--weights", help="font weights to be used for interpolation", nargs='+')
    parser.add_argument("--accentOffsetPercents", help="accents offset to be used for interpolation", nargs='+')
    args = parser.parse_args()

    svg_files = []
    original_font_file = ""
    individual_glyph_folder = ""

    styles = []
    weights = []
    accent_offset_percents = []
    composite_glyphs_to_ignore = []

    if args.svg is not None:
        svg_files = get_all_svg_files(args.svg)

    if args.font is not None:
        original_font_file = args.font

    if args.individualGlyphFolder is not None:
        individual_glyph_folder = args.individualGlyphFolder

    if args.styles is not None:
        styles = args.styles

    if args.weights is not None:
        weights = args.weights
    else:
        weights = [int((800/len(styles) * s) + 100 - (800/len(styles) * s) % 100) for s in range(0, len(styles))] # generate values between 0 and 900 for weight

    if args.accentOffsetPercents is not None:
        accent_offset_percents = args.accentOffsetPercents

    if (len(styles) == len(weights) == len(accent_offset_percents)) is False :
        print("Set the same number of parameters for the Styles, Weights and Accent Offset arguments")
        exit()

    build_interpolated_fonts(svg_files,
                             original_font_file,
                             individual_glyph_folder,
                             styles,
                             weights,
                             accent_offset_percents,
                             composite_glyphs_to_ignore)

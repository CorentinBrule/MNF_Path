import interpolated_fonts, fontforge, os

if __name__ == "__main__":
    svg_path = "glyphes/"
    svg_files = interpolated_fonts.get_all_svg_files(svg_path)

    original_font_file = "ManifontGroteskBook.sfd"
    individual_glyph_folder = "individual_glyph_folder/"

    styles = ["5", "4", "3", "2", "1", "0"]
    weights = [100, 200, 500, 700, 800, 900]
    accent_offset_percents = [8, 9, 11, 13, 14, 16]
    composite_glyphs_to_ignore = [
        "icircumflex",
        "i",
        0,
        int('FB00', 16),
        int('FB01', 16),
        int('FB02', 16),
        int('FB03', 16),
        int('FB04', 16),
        int('FB05', 16),
        int('0152', 16),  # oe
        int('0153', 16),
        int('00c6', 16)
    ]

    font_files = interpolated_fonts.build_interpolated_fonts(svg_files,
                                                                 original_font_file,
                                                                 individual_glyph_folder,
                                                                 styles,
                                                                 weights,
                                                                 accent_offset_percents,
                                                                 composite_glyphs_to_ignore)

    for font_file in font_files:
        interpolated_fonts.sfd2otf(font_file)

from PIL import BdfFontFile
import os

for x in os.listdir("../../rpi-rgb-led-matrix/fonts"):
    if x.endswith(".bdf"):
        font = BdfFontFile.BdfFontFile(open(f"../../rpi-rgb-led-matrix/fonts/{x}", "rb"))
        name = x[:-4]
        font.save(f"{name}.pil")

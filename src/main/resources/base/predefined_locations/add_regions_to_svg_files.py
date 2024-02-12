import io
import os


def main():
    for destfolder in ["green_HL_withregions", "yellow_HL_withregions", "violet_HL_withregions"]:
        srcfolder = destfolder.replace("_withregions", " - original (no regions)")
        if not os.path.exists(destfolder):
            os.mkdir(destfolder)
        srcfilenames_frontview = [fname for fname in os.listdir(srcfolder) if not isbackview(fname)]
        srcfilenames_backview = [fname for fname in os.listdir(srcfolder) if isbackview(fname)]
        replace("front", srcfilenames_frontview, srcfolder, destfolder)
        replace("back", srcfilenames_backview, srcfolder, destfolder)


def replace(frontorback, srcfilenames, srcfolder, destfolder):
    for srcfilename in srcfilenames:
        srcfilepath = os.path.join(srcfolder, srcfilename)
        destfilepath = os.path.join(destfolder, srcfilename)
        print("updating", srcfilepath, "to", destfilepath)

        with io.open(srcfilepath, "r") as src:
            with io.open(destfilepath, "w") as dst:
                ln = src.readline()
                while len(ln) > 0:
                    if "</style>" in ln:
                        with io.open("style_replacement.txt", "r") as style_replace:
                            dst.writelines(style_replace.readlines())
                    elif "</defs>" in ln:
                        with io.open("defs_replacement_" + frontorback + ".txt", "r") as defs_replace:
                            dst.writelines(defs_replace.readlines())
                    else:
                        dst.write(ln)
                    ln = src.readline()


def isbackview(svg_filename):
    for backname in ["Back_of_Head", "Behind_Ears", "Buttocks"]:
        if backname in svg_filename:
            return True
    return False


if __name__ == '__main__':
    main()

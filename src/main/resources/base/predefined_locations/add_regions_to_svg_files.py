import io
import os
import shutil


def main():
    # for destfolder in ["green_HL_withregions", "yellow_HL_withregions", "violet_HL_withregions"]:
    #     srcfolder = destfolder.replace("_withregions", " - original (no regions)")
    for srcfolder in ["yellow_20240508version", "green_20240508version", "violet_20240508version"]:
        destfolder = srcfolder + "_withselectedregions"
        if not os.path.exists(destfolder):
            os.mkdir(destfolder)
        srcfilenames_frontview = [fname for fname in os.listdir(srcfolder) if not isbackview(fname)]
        srcfilenames_backview = [fname for fname in os.listdir(srcfolder) if isbackview(fname)]
        # replace_20240508("front", srcfilenames_frontview, srcfolder, destfolder)
        # replace_20240508("back", srcfilenames_backview, srcfolder, destfolder)
        replace_20240703("front", srcfilenames_frontview, srcfolder, destfolder)
        replace_20240703("back", srcfilenames_backview, srcfolder, destfolder)


def replace_20240703(frontorback, srcfilenames, srcfolder, destfolder):
    for srcfilename in srcfilenames:
        srcfilepath = os.path.join(srcfolder, srcfilename)
        destfilepath = os.path.join(destfolder, srcfilename)
        print("updating", srcfilepath, "to", destfilepath)

        if frontorback == "back":
            shutil.copyfile(srcfilepath, destfilepath)
        else:
            with io.open(srcfilepath, "r") as src:
                with io.open(destfilepath, "w") as dst:
                    ln = src.readline()
                    while len(ln) > 0:
                        if '<g id="Right_Fingers_and_thumb" data-name="Right Fingers and thumb">' in ln:
                            with io.open("selectedfingersandthumb_replacement_" + frontorback + ".txt", "r") as sft_replace:
                                dst.writelines(sft_replace.readlines())
                        elif '<g id="Right_Fingers" data-name="Right Fingers">' in ln:
                            with io.open("selectedfingers_replacement_" + frontorback + ".txt", "r") as sf_replace:
                                dst.writelines(sf_replace.readlines())
                        else:
                            dst.write(ln)
                        ln = src.readline()


def replace_20240508(frontorback, srcfilenames, srcfolder, destfolder):
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
                        with io.open("defs_replacement_updatedagain_" + frontorback + ".txt", "r") as defs_replace:
                            dst.writelines(defs_replace.readlines())
                    else:
                        dst.write(ln)
                    ln = src.readline()


def isbackview(svg_filename):
    for backname in ["Back_of_head", "Behind_Ear", "Buttocks"]:
        if backname in svg_filename:
            return True
    return False


if __name__ == '__main__':
    main()

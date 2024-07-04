import io
import os
import shutil


# adds regions for placeholder images: selected fingers (& thumb), tongue, upper/lower teeth
def main():
    # update highlighted .svg files in colour-coded folders
    for colour in ["yellow", "green", "violet"]:
        srcfolder = os.path.join("..", colour + "_20240508version_noplaceholders")
        destfolder = os.path.join("..", colour + "_20240703version")
        if not os.path.exists(destfolder):
            os.mkdir(destfolder)
        srcfilenames_frontview = [fname for fname in os.listdir(srcfolder) if not isbackview(fname)]
        srcfilenames_backview = [fname for fname in os.listdir(srcfolder) if isbackview(fname)]
        replace_20240703("front", srcfilenames_frontview, srcfolder, destfolder)
        replace_20240703("back", srcfilenames_backview, srcfolder, destfolder)

    # update default (non-highlighted) .svg files in default folder
    srcfolder = os.path.join("..", "defaultviews_20240508version_noplaceholders")
    destfolder = os.path.join("..", "defaultviews_20240703version")
    if not os.path.exists(destfolder):
        os.mkdir(destfolder)
    replace_20240703("front", ["Front_View.svg"], srcfolder, destfolder)
    replace_20240703("back", ["Back_View.svg"], srcfolder, destfolder)
    replace_20240703("side", ["Side_View.svg"], srcfolder, destfolder)


def replace_20240703(frontorback, srcfilenames, srcfolder, destfolder):
    for srcfilename in srcfilenames:
        srcfilepath = os.path.join(srcfolder, srcfilename)
        destfilepath = os.path.join(destfolder, srcfilename)
        print("updating", srcfilepath, "to", destfilepath)

        if frontorback in ["back", "side"]:
            shutil.copyfile(srcfilepath, destfilepath)
        else:  # front
            with io.open(srcfilepath, "r") as src:
                with io.open(destfilepath, "w") as dst:
                    ln = src.readline()
                    while len(ln) > 0:
                        if '<g id="Right_Fingers_and_thumb" data-name="Right Fingers and thumb">' in ln:
                            with io.open("selectedfingersandthumb_replacement_front.txt", "r") as sft_replace:
                                dst.writelines(sft_replace.readlines())
                        elif '<g id="Right_Fingers" data-name="Right Fingers">' in ln:
                            with io.open("selectedfingers_replacement_front.txt", "r") as sf_replace:
                                dst.writelines(sf_replace.readlines())
                        elif '<g id="Mouth" data-name="Mouth">' in ln:
                            with io.open("tongue_replacement_front.txt", "r") as tongue_replace:
                                dst.writelines(tongue_replace.readlines())
                        elif '<g id="Teeth" data-name="Teeth">' in ln:
                            with io.open("upperlowerteeth_replacement_front.txt", "r") as ulteeth_replace:
                                dst.writelines(ulteeth_replace.readlines())
                        else:
                            dst.write(ln)
                        ln = src.readline()


def isbackview(svg_filename):
    for backname in ["Back_of_head", "Behind_Ear", "Buttocks"]:
        if backname in svg_filename:
            return True
    return False


# adds (invisible) regions for all locations
def main_20240508():
    for destfolder in ["green_HL_withregions", "yellow_HL_withregions", "violet_HL_withregions"]:
        srcfolder = destfolder.replace("_withregions", " - original (no regions)")
        if not os.path.exists(destfolder):
            os.mkdir(destfolder)
        srcfilenames_frontview = [fname for fname in os.listdir(srcfolder) if not isbackview(fname)]
        srcfilenames_backview = [fname for fname in os.listdir(srcfolder) if isbackview(fname)]
        replace_20240508("front", srcfilenames_frontview, srcfolder, destfolder)
        replace_20240508("back", srcfilenames_backview, srcfolder, destfolder)


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


if __name__ == '__main__':
    main()

import io
import shutil
import os

curfile_to_locationtext = {
    "Abdominal-Waist_Area": "Abdominal/waist area",
    "Above_Forehead-Hairline": "Above forehead (hairline)",
    "Ankles": "Ankle",
    # "Ankle": "Ankle",
    "Back_of_head": "Back of head",
    "Behind_Ears": "Behind ear",
    "Behind_Ear": "Behind ear",
    "Below_Nose-Philtrum": "Below nose / philtrum",
    "Between_Eyebrows": "Between eyebrows",
    "Between_Fingers_1_and_2": "Between Fingers 1 and 2",
    "Between_Fingers_2_and_3": "Between Fingers 2 and 3",
    "Between_Fingers_3_and_4": "Between Fingers 3 and 4",
    "Between_Thumb_and_Finger_1": "Between Thumb and Finger 1",
    "Between_Fingers": "Between fingers",

    # this set needs to go in this order
    "Upper_Arm_above_Bicep": "Upper arm above biceps",
    "Upper_Arms_above_Bicep": "Upper arm above biceps",
    "Upper_Arm": "Upper arm",
    "Upper_Arms": "Upper arm",
    "Bicep": "Biceps",
    # "Biceps": "Biceps",
    "Armpits": "Armpit",
    # "Armpit": "Armpit",
    "Arms": "Arm",
    # "Arm": "Arm",

    # "Buttocks": "Buttocks",
    "Cheek_and_Nose": "Cheek/nose",
    "Cheekbone_in_Front_of_Ear": "Cheekbone in front of ear",
    "Cheekbone_under_Eye": "Cheekbone under eye",
    "Cheeks": "Cheek",
    # "Cheek": "Cheek",
    "Chest-Breast_Area": "Chest/breast area",
    # "Chin": "Chin",
    "Corners_of_Mouth": "Corner of mouth",
    "Corner_of_Mouth": "Corner of mouth",
    "Earlobes": "Earlobe",
    # "Earlobe": "Earlobe",
    "Ears": "Ear",
    # "Ear": "Ear",
    "Elbows": "Elbow",
    # "Elbow": "Elbow",
    "Eye_Region": "Eye region",
    "Eyebrows": "Eyebrow",
    # "Eyebrow": "Eyebrow",
    "Eyelids": "Eyelid",
    # "Eyelid": "Eyelid",

    # outer corners of eyes have to go before eyes
    "Outer_Corner_of_Left_Eye": "Left Outer corner of eye",
    "Outer_Corner_of_Right_Eye": "Right Outer corner of eye",
    "Outer_Corners_of_Eyes": "Outer corner of eye",
    "Eyes": "Eye",
    # "Eye": "Eye",

    # "Face": "Face",
    "Finger_1": "Finger 1",
    "Finger_2": "Finger 2",
    "Finger_3": "Finger 3",
    "Finger_4": "Finger 4",
    "Fingers_and_Thumbs": "Fingers and thumb",
    "Fingers_and_Thumb": "Fingers and thumb",
    # "Fingers": "Fingers",
    "Forearms": "Forearm",
    # "Forearm": "Forearm",
    "Forehead_Region": "Forehead region",
    # "Forehead": "Forehead",
    # "Groin": "Groin",

    # hands minus fingers & heels of hands have to go before hands
    "Hands_minus_Fingers": "Hand minus fingers",
    "Hand_minus_Fingers": "Hand minus fingers",
    "Heels_of_Hands": "Heel of hand",
    "Heel_of_Hand": "Heel of hand",
    "Hands": "Whole hand",
    "Hand": "Whole hand",

    # "Head": "Head",
    "Hips": "Hip",
    # "Hip": "Hip",
    "Jaws": "Jaw",
    # "Jaw": "Jaw",
    "Knees": "Knee",
    # "Knee": "Knee",
    "Leg_and_Foot": "Leg and foot",
    "Legs_and_Feet": "Leg and foot",
    "Feet": "Foot",
    # "Foot": "Foot",
    # "Lips": "Lips",
    "Lower_Eyelid": "Lower eyelid",
    "Lower_Eyelids": "Lower eyelid",
    "Lower_Leg": "Lower leg",
    "Lower_Legs": "Lower leg",
    "Lower_Lip": "Lower lip",
    "Lower_Torso": "Lower torso",
    # "Mouth": "Mouth",
    # "Neck": "Neck",
    "Nose_Ridge": "Nose ridge",
    "Nose_Root": "Nose root",
    "Nose_Tip": "Nose tip",
    # "Nose": "Nose",
    "Nostrils": "Nostril",
    # "Nostril": "Nostril",
    "Overall_Highlight": "Overall",
    "Pelvis_Area": "Pelvis area",
    # "Septum": "Septum",
    "Septum-Nostril_Area": "Septum / nostril area",
    # "Shoulder": "Shoulder",
    "Shoulders": "Shoulder",
    "Side_of_Face": "Side of face",
    "Sides_of_Face": "Side of face",
    "Sternum-Clavicle_Area": "Sternum/clavicle area",
    # "Teeth": "Teeth",
    # "Temple": "Temple",
    "Thumbs": "Thumb",
    # "Thumb": "Thumb",
    "Top_of_Head": "Top of head",
    # "Torso": "Torso",
    "Underchin": "Under chin",
    "Upper_Eyelid": "Upper eyelid",
    "Upper_Eyelids": "Upper eyelid",
    "Upper_Leg": "Upper leg",
    "Upper_Legs": "Upper leg",
    "Upper_Lip": "Upper lip",
    "Upper_Torso": "Upper torso",
    # "Wrist": "Wrist",
    "Wrists": "Wrist",
}


def main():
    for destfolder in ["green_20240508version", "yellow_20240508version", "violet_20240508version"]:
        srcfolder = destfolder.replace("_renamed", "")
        if not os.path.exists(destfolder):
            os.mkdir(destfolder)
        srcfilenames = [fname for fname in os.listdir(srcfolder)]
        copy_and_rename(srcfilenames, srcfolder, destfolder)


def copy_and_rename(srcfilenames, srcfolder, destfolder):
    for srcfilename in srcfilenames:
        srcfilepath = os.path.join(srcfolder, srcfilename)

        destfilename = srcfilename
        for fname_substr in curfile_to_locationtext.keys():
            # the fussy - / _with stuff is to ensure that (eg) we don't replace Bicep+s with Biceps+s
            if fname_substr + "-" in destfilename:
                destfilename = destfilename.replace(fname_substr + "-", curfile_to_locationtext[fname_substr] + "-")
                break
            elif fname_substr + "_with" in destfilename:
                destfilename = destfilename.replace(fname_substr + "_with", curfile_to_locationtext[fname_substr] + "_with")
                break
        destfilename = format_locationtext_to_filename(destfilename)
        destfilepath = os.path.join(destfolder, destfilename)
        print("updating", srcfilepath, "to", destfilepath)
        shutil.copyfile(srcfilepath, destfilepath)


def format_locationtext_to_filename(locationtext):
    filename = locationtext.replace(" ", "_")
    filename = filename.replace("/", "-slash-")
    return filename


if __name__ == '__main__':
    main()

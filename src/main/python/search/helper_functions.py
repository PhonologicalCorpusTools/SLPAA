import logging
from search.search_classes import XslotTypes

def articulatordisplaytext(arts, phase):
    k = arts[0] # hand, arm, or leg
    if arts[1][1] and not arts[1][2]:
        todisplay = k + " " + str(1)
    elif arts[1][2] and not arts[1][1]:
        todisplay = k + " " + str(2)
    elif arts[1][1] and arts[1][2]:
        
        todisplay = "Both " + k.lower() + "s"
        if phase == 1:
            todisplay += " in phase"
        elif phase == 2:
            todisplay += " out of phase"
        elif phase == 3:
            todisplay += " connected"
        elif phase == 4:
            todisplay += " connected, in phase"
    return todisplay

def phonlocsdisplaytext(phonlocs):
    todisplay = []
    if phonlocs.phonologicalloc:
        if phonlocs.majorphonloc:
            todisplay.append("Maj. phonological locn")
        if phonlocs.minorphonloc:
            todisplay.append("Min. phonological locn")
        else:
            todisplay.append("Phonological locn")
    if phonlocs.phoneticloc:
        todisplay.append("Phonetic locn")
    return todisplay

def loctypedisplaytext(loctype):
    todisplay = []
    if loctype.body:
       todisplay.append("Body")
    elif loctype.signingspace:
        txt = "Signing space"
        if loctype.bodyanchored:
            txt += " (body anchored)"
        elif loctype.purelyspatial:
            txt += " (purely spatial)"
        todisplay.append(txt)
    return todisplay

def signtypedisplaytext(specslist):
    
    specs = [s[0] for s in specslist]
    disp = []
    if 'Unspecified' in specs:
        disp.append('Unspecified')
    if '1h' in specs:
        oneh = []
        for s in ['1h.moves', '1h.no mvmt']:
            if s in specs:
                oneh.append(s)
        if len(oneh) > 0:
            disp.extend(oneh)
        else:
            disp.append('1h')

    if '2h' in specs:
        twoh = []
        for s in ['same HCs', 'different HCs', 'maintain contact', 'contact not maintained', 'bilaterally symmetric', 'not bilaterally symmetric', 'neither moves']:
            if ('2h.' + s) in specs:
                twoh.append('2h.' + s)
        if '2h.only 1 moves' in specs:
            only1moves = []
            for s in ['H1 moves', 'H2 moves']:
                if ('2h.only 1 moves.' + s) in specs:
                    only1moves.append('2h.only ' + s)
            if len(only1moves) > 0:
                twoh.extend(only1moves)
            else:
                twoh.append('2h.one hand moves')
        if '2h.both move' in specs:
            bothmove = []
            for s in ['move differently', 'move similarly']:
                if ('2h.both move.' + s) in specs:
                    bothmove.append('2h.hands ' + s)
            if len(bothmove) > 0:
                twoh.extend(bothmove)
            else:
                twoh.append('2h.both move')     
        if (len(twoh) > 0):
            disp.extend(twoh)
        else:
            disp.append('2h')

    return disp

# TODO
def module_matches_xslottype(timingintervals, targetintervals, xslottype):
    if xslottype == XslotTypes.IGNORE:
        return True
    
    if xslottype == XslotTypes.CONCRETE:
        return timingintervals == targetintervals

    if xslottype == XslotTypes.ABSTRACT_WHOLE:
        # logging.warning("target intervals:")
        # logging.warning(targetintervals)
        return True

    if xslottype == XslotTypes.ABSTRACT_XSLOT:
        return True



        
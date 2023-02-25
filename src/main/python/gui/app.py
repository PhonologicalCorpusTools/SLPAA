from fbs_runtime.application_context.PyQt5 import ApplicationContext, cached_property
from .main_window import MainWindow


class AppContext(ApplicationContext):
    def __init__(self):
        super().__init__()
        
    def run(self):
        self.main_window.show()
        return self.app.exec_()

    @cached_property
    def main_window(self):
        return MainWindow(self)

    @cached_property
    def icons(self):
        return {
            'blank': self.get_resource('icons/blank.png'),
            'blank16': self.get_resource('icons/blank16.png'),
            'copy': self.get_resource('icons/copy.png'),
            'delete': self.get_resource('icons/delete.png'),
            'load': self.get_resource('icons/load.png'),
            'load16': self.get_resource('icons/load16.png'),
            'paste': self.get_resource('icons/paste.png'),
            'plus': self.get_resource('icons/plus.png'),
            'save': self.get_resource('icons/disk.png'),
            'saveas': self.get_resource('icons/diskpencil.png'),
            'hand': self.get_resource('icons/hand.png'),
            'redo': self.get_resource('icons/redo.png'),
            'undo': self.get_resource('icons/undo.png')
        }

    @cached_property
    def default_location_images(self):
        return {
            'head': self.get_resource('default_location_images/head.jpg'),
            'upper_body': self.get_resource('default_location_images/upper_body.jpg'),
            'weak_hand': self.get_resource('default_location_images/weak_hand.jpg'),
            'body_hands_front': self.get_resource('default_location_images/body_hands_front.png'),
            'body_hands_back': self.get_resource('default_location_images/body_hands_back.png')
        }

    # TODO KV eventually delete once we've figured out what we're doing with vector/raster images & qualities
    @cached_property
    def temp_test_images(self):
        return {
            'layers_posterR.svg': self.get_resource('temp_test_images/layers_posterR.svg'),
            'layers_posterR_min.svg': self.get_resource('temp_test_images/layers_posterR_min.svg'),
            'Layers_PosterR-01.png': self.get_resource('temp_test_images/Layers_PosterR-01.png'),
            'shading_A4p.png': self.get_resource('temp_test_images/shading_A4p.png'),
            'shading_A4p_min-01.svg': self.get_resource('temp_test_images/shading_A4p_min-01.svg'),
            'shading_letter.png': self.get_resource('temp_test_images/shading_letter.png'),
            'shading_letter.svg': self.get_resource('temp_test_images/shading_letter.svg'),
            'shading_letter_min.svg': self.get_resource('temp_test_images/shading_letter_min.svg'),
            'shading_poster.png': self.get_resource('temp_test_images/shading_poster.png'),
            'shading_poster.svg': self.get_resource('temp_test_images/shading_poster.svg'),
            'shading_poster_min.svg': self.get_resource('temp_test_images/shading_poster_min.svg'),
            'symmetry_sample.png': self.get_resource('temp_test_images/symmetry_sample.png'),
            'symmetry_sample.svg': self.get_resource('temp_test_images/symmetry_sample.svg')
        }

    @cached_property
    def hand_illustrations(self):
        return {
            'neutral': self.get_resource('illustrations/neutral.jpg'),
            'slot2': self.get_resource('illustrations/slot2.jpg'),
            'slot3': self.get_resource('illustrations/slot3.jpg'),
            'slot4': self.get_resource('illustrations/slot4.jpg'),
            'slot5': self.get_resource('illustrations/slot5.jpg'),
            'slot6': self.get_resource('illustrations/slot6.jpg'),
            'slot7': self.get_resource('illustrations/slot7.jpg'),
            'slot10': self.get_resource('illustrations/slot10.jpg'),
            'slot11': self.get_resource('illustrations/slot11.jpg'),
            'slot12': self.get_resource('illustrations/slot12.jpg'),
            'slot13': self.get_resource('illustrations/slot13.jpg'),
            'slot14': self.get_resource('illustrations/slot14.jpg'),
            'slot15': self.get_resource('illustrations/slot15.jpg'),
            'slot17': self.get_resource('illustrations/slot17.jpg'),
            'slot18': self.get_resource('illustrations/slot18.jpg'),
            'slot19': self.get_resource('illustrations/slot19.jpg'),
            'slot20': self.get_resource('illustrations/slot20.jpg'),
            'slot22': self.get_resource('illustrations/slot22.jpg'),
            'slot23': self.get_resource('illustrations/slot23.jpg'),
            'slot24': self.get_resource('illustrations/slot24.jpg'),
            'slot25': self.get_resource('illustrations/slot25.jpg'),
            'slot27': self.get_resource('illustrations/slot27.jpg'),
            'slot28': self.get_resource('illustrations/slot28.jpg'),
            'slot29': self.get_resource('illustrations/slot29.jpg'),
            'slot30': self.get_resource('illustrations/slot30.jpg'),
            'slot32': self.get_resource('illustrations/slot32.jpg'),
            'slot33': self.get_resource('illustrations/slot33.jpg'),
            'slot34': self.get_resource('illustrations/slot34.jpg')
        }

    # @cached_property
    # def xslotimage(self):
    #     return {
    #         'xslot': self.get_resource('xslotsample.png')
    #     }

    @cached_property
    def predefined(self):
        return {
            'base': self.get_resource('predefined/base.png'),
            'no-match': self.get_resource('predefined/no-match.png'),
            'empty': self.get_resource('predefined/empty.png'),

            '1': self.get_resource('predefined/1.png'),
            'bent-1': self.get_resource('predefined/bent-1.png'),
            'crooked-1': self.get_resource('predefined/crooked-1.png'),

            '3': self.get_resource('predefined/3.png'),
            'clawed-3': self.get_resource('predefined/clawed-3.png'),
            'contracted-3': self.get_resource('predefined/contracted-3.png'),

            '4': self.get_resource('predefined/4.png'),
            'bent-4': self.get_resource('predefined/bent-4.png'),
            'clawed-4': self.get_resource('predefined/clawed-4.png'),
            'crooked-4': self.get_resource('predefined/crooked-4.png'),
            'slanted-4': self.get_resource('predefined/slanted-4.png'),

            '5': self.get_resource('predefined/5.png'),
            'bent-5': self.get_resource('predefined/bent-5.png'),
            'bent-midfinger-5': self.get_resource('predefined/bent-midfinger-5.png'),
            'clawed-extended-5': self.get_resource('predefined/clawed-extended-5.png'),
            'contracted-5': self.get_resource('predefined/contracted-5.png'),
            'relaxed-contracted-5': self.get_resource('predefined/relaxed-contracted-5.png'),
            'crooked-5': self.get_resource('predefined/crooked-5.png'),
            'crooked-slanted-5': self.get_resource('predefined/crooked-slanted-5.png'),
            'modified-5': self.get_resource('predefined/modified-5.png'),
            'slanted-5': self.get_resource('predefined/slanted-5.png'),
            
            '8': self.get_resource('predefined/8.png'),
            'covered-8': self.get_resource('predefined/covered-8.png'),
            'extended-8': self.get_resource('predefined/extended-8.png'),
            'open-8': self.get_resource('predefined/open-8.png'),

            'A': self.get_resource('predefined/A.png'),
            'closed-A-index': self.get_resource('predefined/closed-A-index.png'),
            'extended-A': self.get_resource('predefined/extended-A.png'),
            'A-index': self.get_resource('predefined/A-index.png'),
            'modified-A': self.get_resource('predefined/modified-A.png'),
            'open-A': self.get_resource('predefined/open-A.png'),

            'B1': self.get_resource('predefined/B1.png'),
            'bent-B': self.get_resource('predefined/bent-B.png'),
            'bent-extended-B': self.get_resource('predefined/bent-extended-B.png'),
            'clawed-extended-B': self.get_resource('predefined/clawed-extended-B.png'),
            'contracted-B': self.get_resource('predefined/contracted-B.png'),
            'extended-B': self.get_resource('predefined/extended-B.png'),
            'slanted-extended-B': self.get_resource('predefined/slanted-extended-B.png'),

            'B2': self.get_resource('predefined/B2.png'),

            'C': self.get_resource('predefined/C.png'),
            'clawed-C': self.get_resource('predefined/clawed-C.png'),
            'clawed-spread-C': self.get_resource('predefined/clawed-spread-C.png'),
            'contracted-C': self.get_resource('predefined/contracted-C.png'),
            'extended-C': self.get_resource('predefined/extended-C.png'),
            'flat-C': self.get_resource('predefined/flat-C.png'),
            'C-index': self.get_resource('predefined/C-index.png'),
            'double-C-index': self.get_resource('predefined/double-C-index.png'),
            'spread-C': self.get_resource('predefined/spread-C.png'),

            'D': self.get_resource('predefined/D.png'),
            'partially-bent-D': self.get_resource('predefined/partially-bent-D.png'),
            'closed-bent-D': self.get_resource('predefined/closed-bent-D.png'),
            'modified-D': self.get_resource('predefined/modified-D.png'),

            'E': self.get_resource('predefined/E.png'),
            'open-E': self.get_resource('predefined/open-E.png'),

            'F': self.get_resource('predefined/F.png'),
            'adducted-F': self.get_resource('predefined/adducted-F.png'),
            'clawed-F': self.get_resource('predefined/clawed-F.png'),
            'covered-F': self.get_resource('predefined/covered-F.png'),
            'flat-F': self.get_resource('predefined/flat-F.png'),
            'flat-clawed-F': self.get_resource('predefined/flat-clawed-F.png'),
            'flat-open-F': self.get_resource('predefined/flat-open-F.png'),
            'offset-F': self.get_resource('predefined/offset-F.png'),
            'open-F': self.get_resource('predefined/open-F.png'),
            'slanted-F': self.get_resource('predefined/slanted-F.png'),

            'G': self.get_resource('predefined/G.png'),
            'closed-modified-G': self.get_resource('predefined/closed-modified-G.png'),
            'closed-double-modified-G': self.get_resource('predefined/closed-double-modified-G.png'),
            'double-modified-G': self.get_resource('predefined/double-modified-G.png'),
            'modified-G': self.get_resource('predefined/modified-G.png'),

            'I': self.get_resource('predefined/I.png'),
            'bent-I': self.get_resource('predefined/bent-I.png'),
            'bent-combined-I+1': self.get_resource('predefined/bent-combined-I+1.png'),
            'clawed-I': self.get_resource('predefined/clawed-I.png'),
            'combined-I+1': self.get_resource('predefined/combined-I+1.png'),
            'combined-ILY': self.get_resource('predefined/combined-ILY.png'),
            'combined-I+A': self.get_resource('predefined/combined-I+A.png'),
            'flat-combined-I+1': self.get_resource('predefined/flat-combined-I+1.png'),

            'K': self.get_resource('predefined/K.png'),
            'extended-K': self.get_resource('predefined/extended-K.png'),

            'L': self.get_resource('predefined/L.png'),
            'bent-L': self.get_resource('predefined/bent-L.png'),
            'bent-thumb-L': self.get_resource('predefined/bent-thumb-L.png'),
            'clawed-extended-L': self.get_resource('predefined/clawed-extended-L.png'),
            'contracted-L': self.get_resource('predefined/contracted-L.png'),
            'double-contracted-L': self.get_resource('predefined/double-contracted-L.png'),
            'crooked-L': self.get_resource('predefined/crooked-L.png'),

            'M': self.get_resource('predefined/M.png'),
            'flat-M': self.get_resource('predefined/flat-M.png'),

            'middle-finger': self.get_resource('predefined/middle-finger.png'),

            'N': self.get_resource('predefined/N.png'),

            'O': self.get_resource('predefined/O.png'),
            'covered-O': self.get_resource('predefined/covered-O.png'),
            'flat-O': self.get_resource('predefined/flat-O.png'),
            'O-index': self.get_resource('predefined/O-index.png'),
            'modified-O': self.get_resource('predefined/modified-O.png'),
            'offset-O': self.get_resource('predefined/offset-O.png'),
            'open-O-index': self.get_resource('predefined/open-O-index.png'),
            'spread-open-O': self.get_resource('predefined/spread-open-O.png'),

            'R': self.get_resource('predefined/R.png'),
            'bent-R': self.get_resource('predefined/bent-R.png'),
            'extended-R': self.get_resource('predefined/extended-R.png'),

            'S': self.get_resource('predefined/S.png'),

            'T': self.get_resource('predefined/T.png'),
            'covered-T': self.get_resource('predefined/covered-T.png'),

            'U': self.get_resource('predefined/U.png'),
            'bent-U': self.get_resource('predefined/bent-U.png'),
            'bent-extended-U': self.get_resource('predefined/bent-extended-U.png'),
            'clawed-U': self.get_resource('predefined/clawed-U.png'),
            'contracted-U': self.get_resource('predefined/contracted-U.png'),
            'contracted-U-index': self.get_resource('predefined/contracted-U-index.png'),
            'crooked-U': self.get_resource('predefined/crooked-U.png'),
            'extended-U': self.get_resource('predefined/extended-U.png'),

            'V': self.get_resource('predefined/V.png'),
            'bent-V': self.get_resource('predefined/bent-V.png'),
            'bent-extended-V': self.get_resource('predefined/bent-extended-V.png'),
            'clawed-V': self.get_resource('predefined/clawed-V.png'),
            'clawed-extended-V': self.get_resource('predefined/clawed-extended-V.png'),
            'closed-V': self.get_resource('predefined/closed-V.png'),
            'crooked-V': self.get_resource('predefined/crooked-V.png'),
            'crooked-extended-V': self.get_resource('predefined/crooked-extended-V.png'),
            'slanted-V': self.get_resource('predefined/slanted-V.png'),

            'W': self.get_resource('predefined/W.png'),
            'clawed-W': self.get_resource('predefined/clawed-W.png'),
            'closed-W': self.get_resource('predefined/closed-W.png'),
            'covered-W': self.get_resource('predefined/covered-W.png'),
            'crooked-W': self.get_resource('predefined/crooked-W.png'),

            'X': self.get_resource('predefined/X.png'),
            'closed-X': self.get_resource('predefined/closed-X.png'),

            'Y': self.get_resource('predefined/Y.png'),
            'combined-Y+middle': self.get_resource('predefined/combined-Y+middle.png'),
            'combined-Y+U': self.get_resource('predefined/combined-Y+U.png'),
            # 'modified-Y': self.get_resource('predefined/modified-Y.png'),  # TODO KV April deleted this file 20211115

            'open-palm': self.get_resource('predefined/open-palm.png')
        }

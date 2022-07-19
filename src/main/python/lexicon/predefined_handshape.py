NULL = '\u2205'

class PredefinedHandshape:
    def __init__(self, name, filename, canonical):
        self._name = name
        self._filename = filename
        self._canonical = canonical

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def canonical(self):
        return self._canonical

    @canonical.setter
    def canonical(self, new_canonical):
        self._canonical = new_canonical

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, new_filename):
        self._filename = new_filename


class HandshapeNoMatch(PredefinedHandshape):
    def __init__(self, name='no match', filename='no-match', canonical=None):
        super().__init__(name, filename, canonical)


class HandshapeEmpty(PredefinedHandshape):
    def __init__(self, name='empty', filename='empty', canonical=(
            '', '', '', '',
            '', '', NULL, '/', '', '', '', '', '', '',
            '1', '', '', '',
            '', '2', '', '', '',
            '', '3', '', '', '',
            '', '4', '', '', ''
    )):
        super().__init__(name, filename, canonical)


class Handshape1(PredefinedHandshape):
    def __init__(self, name='1', filename='1', canonical=(
            'O', '=', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'm', '-', '2', '-', '-',
            '1', 'E', 'E', 'E',
            '<', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class Handshape3(PredefinedHandshape):
    def __init__(self, name='3', filename='3', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'E', 'E',
            '{', '2', 'E', 'E', 'E',
            '<', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name, filename, canonical)


class Handshape4(PredefinedHandshape):
    def __init__(self, name='4', filename='4', canonical=(
            'O', '=', 'i', 'i',
            'u', 'd', NULL, '/', 'fr', 'M', '-', '-', '3', '-',
            '1', 'E', 'E', 'E',
            '{', '2', 'E', 'E', 'E',
            '{', '3', 'E', 'E', 'E',
            '{', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class Handshape5(PredefinedHandshape):
    def __init__(self, name='5', filename='5', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'E', 'E',
            '{', '2', 'E', 'E', 'E',
            '{', '3', 'E', 'E', 'E',
            '{', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class Handshape6(PredefinedHandshape):
    def __init__(self, name='6', filename='6', canonical=(
            'O', '{', 'E', 'i',
            't', 'd', NULL, '/', 't', 'd', '-', '-', '-', '4',
            '1', 'E', 'E', 'E',
            '{', '2', 'E', 'E', 'E',
            '{', '3', 'E', 'E', 'E',
            '<', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class Handshape8(PredefinedHandshape):
    def __init__(self, name='8', filename='8', canonical=(
            'O', '{', 'i', 'i',
            'fr', 'd', NULL, '/', 'fr', 'd', '-', '2', '-', '-',
            '1', 'E', 'E', 'E',
            '{', '2', 'i', 'i', 'E',
            '<', '3', 'i', 'E', 'E',
            '{', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeA(PredefinedHandshape):
    def __init__(self, name='A', filename='A', canonical=(
            'U', '=', 'E', 'E',
            'fr', 'd', NULL, '/', 'r', 'p', '1', '-', '-', '-',
            '1', 'F', 'F', 'F',
            '=', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeAdductedF(PredefinedHandshape):
    # fontmap: m
    def __init__(self, name='adducted F', filename='adducted-F', canonical=(
            'O', '{', 'i', 'i',
            't', 'd', NULL, '/', 't', 'd', '1', '-', '-', '-',
            '1', 'i', 'i', 'i',
            '=', '2', 'i', 'E', 'E',
            '=', '3', 'E', 'E', 'E',
            '=', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeB1(PredefinedHandshape):
    def __init__(self, name='B1', filename='B1', canonical=(
            'O', '=', 'i', 'i',
            'fr', 'd', NULL, '/', 'fr', 'M', '-', '-', '3', '-',
            '1', 'E', 'E', 'E',
            '=', '2', 'E', 'E', 'E',
            '=', '3', 'E', 'E', 'E',
            '=', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeB2(PredefinedHandshape):
    def __init__(self, name='B2', filename='B2', canonical=(
            'U', '=', 'E', 'i',
            'u', 'p', NULL, '/', 'r', 'M', '1', '-', '-', '-',
            '1', 'E', 'E', 'E',
            '=', '2', 'E', 'E', 'E',
            '=', '3', 'E', 'E', 'E',
            '=', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeBase(PredefinedHandshape):
    def __init__(self, name='base', filename='base', canonical=(
            'U', '<', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'i', 'E', 'E',
            '=', '2', 'i', 'E', 'E',
            '=', '3', 'i', 'E', 'E',
            '=', '4', 'i', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeBent1(PredefinedHandshape):
    def __init__(self, name='bent 1', filename='bent-1', canonical=(
            'O', '=', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'm', '-', '2', '-', '-',
            '1', 'F', 'E', 'E',
            '=', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeBent4(PredefinedHandshape):
    def __init__(self, name='bent 4', filename='bent-4', canonical=(
            'O', '=', 'i', 'i',
            'b', 'd', NULL, '/', 'fr', 'p', '-', '-', '3', '-',
            '1', 'F', 'E', 'E',
            '{', '2', 'F', 'E', 'E',
            '{', '3', 'F', 'E', 'E',
            '{', '4', 'F', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeBent5(PredefinedHandshape):
    def __init__(self, name='bent 5', filename='bent-5', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'F', 'E', 'E',
            '{', '2', 'F', 'E', 'E',
            '{', '3', 'F', 'E', 'E',
            '{', '4', 'F', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeBentB(PredefinedHandshape):
    def __init__(self, name='bent B', filename='bent-B', canonical=(
            'O', '=', 'i', 'i',
            'b', 'd', NULL, '/', 'fr', 'p', '-', '-', '-', '4',
            '1', 'F', 'E', 'E',
            '=', '2', 'F', 'E', 'E',
            '=', '3', 'F', 'E', 'E',
            '=', '4', 'F', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeBentCombinedIPlus1(PredefinedHandshape):
    def __init__(self, name='bent combined I+1', filename='bent-combined-I+1', canonical=(
            'O', '=', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'm', '-', '2', '-', '-',
            '1', 'F', 'E', 'E',
            '=', '2', 'F', 'F', 'E',
            '=', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeBentExtendedB(PredefinedHandshape):
    # fontmap: :
    def __init__(self, name='bent extended B', filename='bent-extended-B', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'F', 'E', 'E',
            '=', '2', 'F', 'E', 'E',
            '=', '3', 'F', 'E', 'E',
            '=', '4', 'F', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeBentExtendedU(PredefinedHandshape):
    def __init__(self, name='bent extended U', filename='bent-extended-U', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'F', 'E', 'E',
            '=', '2', 'F', 'E', 'E',
            '=', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeBentExtendedV(PredefinedHandshape):
    def __init__(self, name='bent extended V', filename='bent-extended-V', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'F', 'E', 'E',
            '{', '2', 'F', 'E', 'E',
            '=', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeBentI(PredefinedHandshape):
    # fontmap: Q
    def __init__(self, name='bent I', filename='bent-I', canonical=(
            'O', '=', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'm', '1', '-', '-', '-',
            '1', 'F', 'F', 'E',
            '=', '2', 'F', 'F', 'E',
            '=', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeBentL(PredefinedHandshape):
    def __init__(self, name='bent L', filename='bent-L', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'F', 'E', 'E',
            '=', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeBentMidfinger5(PredefinedHandshape):
    def __init__(self, name='bent midfinger 5', filename='bent-midfinger-5', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'E', 'E',
            '{', '2', 'F', 'E', 'E',
            '{', '3', 'i', 'E', 'E',
            '{', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeBentOffset1(PredefinedHandshape):
    def __init__(self, name='bent offset 1', filename='bent-offset-1', canonical=(
            'O', '=', 'E', 'i',
            'fr', 'd', NULL, '/', 'u', 'm', '1', '-', '-', '-',
            '1', 'F', 'E', 'E',
            '<', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeBentR(PredefinedHandshape):
    def __init__(self, name='bent R', filename='bent-R', canonical=(
            'O', '=', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'm', '-', '-', '3', '-',
            '1', 'F', 'E', 'E',
            'x', '2', 'F', 'i', 'i',
            '<', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeBentThumbL(PredefinedHandshape):
    # fontmap: F
    def __init__(self, name='bent thumb L', filename='bent-thumb-L', canonical=(
            'L', '<', 'i', 'F',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'E', 'E',
            '<', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeBentU(PredefinedHandshape):
    def __init__(self, name='bent U', filename='bent-U', canonical=(
            'O', '{', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'd', '-', '-', '3', '-',
            '1', 'F', 'E', 'E',
            '=', '2', 'F', 'E', 'E',
            '=', '3', 'i', 'i', 'i',
            '=', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeBentV(PredefinedHandshape):
    # fontmap: a
    def __init__(self, name='bent V', filename='bent-V', canonical=(
            'O', '{', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'd', '-', '-', '3', '-',
            '1', 'F', 'E', 'E',
            '{', '2', 'F', 'E', 'E',
            '=', '3', 'i', 'i', 'i',
            '=', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeC(PredefinedHandshape):
    def __init__(self, name='C', filename='C', canonical=(
            'O', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'i', 'i',
            '=', '2', 'E', 'i', 'i',
            '=', '3', 'E', 'i', 'i',
            '=', '4', 'E', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCIndex(PredefinedHandshape):
    # fontmap: L
    def __init__(self, name='C index', filename='C-index', canonical=(
            'O', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'i', 'i',
            '<', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClawed1(PredefinedHandshape):
    def __init__(self, name='clawed 1', filename='clawed-1', canonical=(
            'O', '=', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'm', '-', '2', '-', '-',
            '1', 'E', 'F', 'F',
            '<', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClawed3(PredefinedHandshape):
    # fontmap: @
    def __init__(self, name='clawed 3', filename='clawed-3', canonical=(
            'L', '{', 'i', 'F',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'F', 'i',
            '{', '2', 'E', 'F', 'i',
            '<', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClawed4(PredefinedHandshape):
    def __init__(self, name='clawed 4', filename='clawed-4', canonical=(
            'O', '=', 'i', 'i',
            'u', 'd', NULL, '/', 'fr', 'M', '-', '-', '3', '-',
            '1', 'E', 'F', 'i',
            '{', '2', 'E', 'F', 'i',
            '{', '3', 'E', 'F', 'i',
            '{', '4', 'E', 'F', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClawedExtended5(PredefinedHandshape):
    def __init__(self, name='clawed extended 5', filename='clawed-extended-5', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'F', 'i',
            '{', '2', 'E', 'F', 'i',
            '{', '3', 'E', 'F', 'i',
            '{', '4', 'E', 'F', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClawedC(PredefinedHandshape):
    # fontmap: /
    def __init__(self, name='clawed C', filename='clawed-C', canonical=(
            'O', '{', 'i', 'F',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'F', 'i',
            '=', '2', 'E', 'F', 'i',
            '=', '3', 'E', 'F', 'i',
            '=', '4', 'E', 'F', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClawedExtendedB(PredefinedHandshape):
    # fontmap: =
    def __init__(self, name='clawed extended B', filename='clawed-extended-B', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'F', 'i',
            '=', '2', 'E', 'F', 'i',
            '=', '3', 'E', 'F', 'i',
            '=', '4', 'E', 'F', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClawedExtendedL(PredefinedHandshape):
    # fontmap: E
    def __init__(self, name='clawed extended L', filename='clawed-extended-L', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'F', 'i',
            '<', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClawedExtendedV(PredefinedHandshape):
    # fontmap: c
    def __init__(self, name='clawed extended V', filename='clawed-extended-V', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'F', 'i',
            '{', '2', 'E', 'F', 'i',
            '<', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClawedF(PredefinedHandshape):
    # fontmap: O
    def __init__(self, name='clawed F', filename='clawed-F', canonical=(
            'O', '{', 'i', 'i',
            't', 'd', NULL, '/', 't', 'd', '1', '-', '-', '-',
            '1', 'i', 'i', 'i',
            '{', '2', 'E', 'F', 'i',
            '{', '3', 'E', 'F', 'i',
            '{', '4', 'E', 'F', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClawedI(PredefinedHandshape):
    # fontmap: R
    def __init__(self, name='clawed I', filename='clawed-I', canonical=(
            'O', '=', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'm', '1', '-', '-', '-',
            '1', 'F', 'F', 'E',
            '=', '2', 'F', 'F', 'E',
            '=', '3', 'F', 'F', 'E',
            '=', '4', 'E', 'F', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClawedL(PredefinedHandshape):
    def __init__(self, name='clawed L', filename='clawed-L', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'F', 'F',
            '<', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClawedSpreadC(PredefinedHandshape):
    # fontmap: )
    def __init__(self, name='clawed spread C', filename='clawed-spread-C', canonical=(
            'O', '{', 'i', 'F',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'F', 'i',
            '{', '2', 'E', 'F', 'i',
            '{', '3', 'E', 'F', 'i',
            '{', '4', 'E', 'F', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClawedU(PredefinedHandshape):
    def __init__(self, name='clawed U', filename='clawed-U', canonical=(
            'O', '{', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'd', '-', '-', '3', '-',
            '1', 'E', 'F', 'i',
            '=', '2', 'E', 'F', 'i',
            '<', '3', 'i', 'i', 'i',
            '=', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClawedV(PredefinedHandshape):
    # fontmap: b
    def __init__(self, name='clawed V', filename='clawed-V', canonical=(
            'O', '{', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'd', '-', '-', '3', '-',
            '1', 'E', 'F', 'i',
            '{', '2', 'E', 'F', 'i',
            '<', '3', 'i', 'i', 'i',
            '=', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClawedW(PredefinedHandshape):
    # fontmap: k
    def __init__(self, name='clawed W', filename='clawed-W', canonical=(
            'O', '{', 'i', 'i',
            'fr', 'd', NULL, '/', 'fr', 'd', '-', '-', '-', '4',
            '1', 'E', 'F', 'i',
            '{', '2', 'E', 'F', 'i',
            '{', '3', 'E', 'F', 'i',
            '<', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClosedAIndex(PredefinedHandshape):
    # fontmap: 3
    def __init__(self, name='closed A index', filename='closed-A-index', canonical=(
            'U', '=', 'E', 'E',
            'fr', 'd', NULL, '/', 'r', 'm', '1', '-', '-', '-',
            '1', 'i', 'F', 'i',
            '=', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClosedBentD(PredefinedHandshape):
    def __init__(self, name='closed bent D', filename='closed-bent-D', canonical=(
            'O', '{', 'E', 'E',
            't', 'd', NULL, '/', 't', 'd', '-', '2', '-', '-',
            '1', 'F', 'E', 'E',
            '=', '2', 'i', 'i', 'i',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClosedDoubleModifiedG(PredefinedHandshape):
    # fontmap: U
    def __init__(self, name='closed double modified G', filename='closed-double-modified-G', canonical=(
            'O', '{', 'E', 'E',
            'fr', 'd', NULL, '/', 'fr', 'd', '1', '2', '-', '-',
            '1', 'F', 'E', 'E',
            '=', '2', 'F', 'E', 'E',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClosedModifiedG(PredefinedHandshape):
    # fontmap: I
    def __init__(self, name='closed modified G', filename='closed-modified-G', canonical=(
            'O', '{', 'E', 'E',
            'fr', 'd', NULL, '/', 'fr', 'd', '1', '-', '-', '-',
            '1', 'F', 'E', 'E',
            '=', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClosedV(PredefinedHandshape):
    def __init__(self, name='closed V', filename='closed-V', canonical=(
            'O', '=', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'm', '-', '-', '3', '-',
            '1', 'i', 'F', 'F',
            '{', '2', 'i', 'F', 'F',
            '<', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClosedW(PredefinedHandshape):
    # fontmap: l
    def __init__(self, name='closed W', filename='closed-W', canonical=(
            'O', '{', 'i', 'i',
            'fr', 'd', NULL, '/', 'fr', 'd', '-', '-', '-', '4',
            '1', 'E', 'E', 'E',
            '=', '2', 'E', 'E', 'E',
            '=', '3', 'E', 'E', 'E',
            '=', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeClosedX(PredefinedHandshape):
    def __init__(self, name='closed X', filename='closed-X', canonical=(
            'O', '=', 'E', 'E',
            't', 'd', NULL, '/', 't', 'd', '1', '-', '-', '-',
            '1', 'E', 'F', 'i',
            '<', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCombinedIPlus1(PredefinedHandshape):
    # fontmap: g
    def __init__(self, name='combined I+1', filename='combined-I+1', canonical=(
            'O', '=', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'm', '-', '2', '-', '-',
            '1', 'E', 'E', 'E',
            '<', '2', 'F', 'F', 'E',
            '=', '3', 'F', 'F', 'E',
            '=', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCombinedIPlusA(PredefinedHandshape):
    def __init__(self, name='combined I+A', filename='combined-I+A', canonical=(
            'U', '=', 'E', 'E',
            'fr', 'd', NULL, '/', 'r', 'p', '1', '-', '-', '-',
            '1', 'F', 'F', 'E',
            '=', '2', 'F', 'F', 'E',
            '=', '3', 'F', 'F', 'E',
            '=', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCombinedILY(PredefinedHandshape):
    # fontmap: h
    def __init__(self, name='combined ILY', filename='combined-ILY', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'E', 'E',
            '<', '2', 'F', 'F', 'E',
            '=', '3', 'F', 'F', 'E',
            '=', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCombinedYAndU(PredefinedHandshape):
    def __init__(self, name='combined Y+U', filename='combined-Y+U', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'E', 'E',
            '=', '2', 'E', 'E', 'E',
            '<', '3', 'F', 'F', 'E',
            '<', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCombinedYAndMiddle(PredefinedHandshape):
    def __init__(self, name='combined Y+middle', filename='combined-Y+middle', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'F', 'F',
            '=', '2', 'E', 'E', 'E',
            '<', '3', 'i', 'F', 'E',
            '<', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeContracted3(PredefinedHandshape):
    def __init__(self, name='contracted 3', filename='contracted-3', canonical=(
            'O', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'i', 'E', 'E',
            '{', '2', 'i', 'E', 'E',
            '<', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeContracted5(PredefinedHandshape):
    # fontmap: 5
    def __init__(self, name='contracted 5', filename='contracted-5', canonical=(
            'O', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'i', 'E', 'E',
            '{', '2', 'i', 'E', 'E',
            '{', '3', 'i', 'E', 'E',
            '{', '4', 'i', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeContractedB(PredefinedHandshape):
    def __init__(self, name='contracted B', filename='contracted-B', canonical=(
            'O', '=', 'E', 'E',
            'u', 'd', NULL, '/', 'fr', 'm', '-', '2', '-', '-',
            '1', 'i', 'E', 'E',
            '=', '2', 'i', 'E', 'E',
            '=', '3', 'i', 'E', 'E',
            '=', '4', 'i', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeContractedC(PredefinedHandshape):
    # fontmap: ;
    def __init__(self, name='contracted C', filename='contracted-C', canonical=(
            'O', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'i', 'E', 'E',
            '=', '2', 'i', 'E', 'E',
            '=', '3', 'i', 'E', 'E',
            '=', '4', 'i', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeContractedL(PredefinedHandshape):
    def __init__(self, name='contracted L', filename='contracted-L', canonical=(
            'O', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'i', 'E', 'E',
            '<', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeContractedU(PredefinedHandshape):
    def __init__(self, name='contracted U', filename='contracted-U', canonical=(
            'O', '{', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'd', '-', '-', '3', '-',
            '1', 'i', 'E', 'E',
            '=', '2', 'i', 'E', 'E',
            '<', '3', 'i', 'i', 'i',
            '=', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeContractedUIndex(PredefinedHandshape):
    # fontmap: }
    def __init__(self, name='contracted U index', filename='contracted-U-index', canonical=(
            'O', '{', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'd', '-', '-', '3', '-',
            '1', 'E', 'F', 'E',
            '=', '2', 'E', 'E', 'E',
            '<', '3', 'i', 'i', 'i',
            '=', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCovered8(PredefinedHandshape):
    # fontmap: s
    def __init__(self, name='covered 8', filename='covered-8', canonical=(
            'O', '{', 'i', 'F',
            'fr', 'd', NULL, '/', 'b', 'd', '-', '2', '-', '-',
            '1', 'E', 'E', 'E',
            '{', '2', 'i', 'i', 'F',
            '<', '3', 'i', 'E', 'E',
            '{', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCoveredF(PredefinedHandshape):
    # fontmap: n
    def __init__(self, name='covered F', filename='covered-F', canonical=(
            'O', '{', 'i', 'F',
            'fr', 'd', NULL, '/', 'b', 'd', '1', '-', '-', '-',
            '1', 'F', 'F', 'i',
            '{', '2', 'i', 'E', 'E',
            '{', '3', 'E', 'E', 'E',
            '{', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCoveredO(PredefinedHandshape):
    def __init__(self, name='covered O', filename='covered-O', canonical=(
            'O', '=', 'i', 'E',
            'fr', 'd', NULL, '/', 'b', 'd', '-', '-', '3', '-',
            '1', 'i', 'i', 'i',
            '=', '2', 'i', 'i', 'i',
            '=', '3', 'i', 'i', 'i',
            '=', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCoveredT(PredefinedHandshape):
    def __init__(self, name='covered T', filename='covered-T', canonical=(
            'O', '=', 'E', 'E',
            't', 'd', NULL, '/', 'fr', 'm', '1', '-', '-', '-',
            '1', 'i', 'F', 'F',
            '<', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCoveredW(PredefinedHandshape):
    def __init__(self, name='covered W', filename='covered-W', canonical=(
            'O', '{', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'd', '-', '-', '-', '4',
            '1', 'E', 'E', 'E',
            '{', '2', 'E', 'E', 'E',
            '{', '3', 'E', 'E', 'E',
            '<', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCrooked1(PredefinedHandshape):
    def __init__(self, name='crooked 1', filename='crooked-1', canonical=(
            'O', '=', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'm', '-', '2', '-', '-',
            '1', 'E', 'i', 'i',
            '<', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCrooked4(PredefinedHandshape):
    def __init__(self, name='crooked 4', filename='crooked-4', canonical=(
            'O', '=', 'i', 'i',
            'u', 'd', NULL, '/', 'fr', 'M', '-', '-', '3', '-',
            '1', 'E', 'i', 'i',
            '{', '2', 'E', 'i', 'i',
            '{', '3', 'E', 'i', 'i',
            '{', '4', 'E', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCrooked5(PredefinedHandshape):
    def __init__(self, name='crooked 5', filename='crooked-5', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'i', 'i',
            '{', '2', 'E', 'i', 'i',
            '{', '3', 'E', 'i', 'i',
            '{', '4', 'E', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCrookedC(PredefinedHandshape):
    def __init__(self, name='crooked C', filename='crooked-C', canonical=(
            'O', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'i', 'i',
            '=', '2', 'E', 'i', 'i',
            '=', '3', 'E', 'i', 'i',
            '=', '4', 'E', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCrookedExtendedB(PredefinedHandshape):
    def __init__(self, name='crooked extended B', filename='crooked-extended-B', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'i', 'i',
            '=', '2', 'E', 'i', 'i',
            '=', '3', 'E', 'i', 'i',
            '=', '4', 'E', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCrookedExtendedV(PredefinedHandshape):
    def __init__(self, name='crooked extended V', filename='crooked-extended-V', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'i', 'i',
            '{', '2', 'E', 'i', 'i',
            '<', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCrookedL(PredefinedHandshape):
    def __init__(self, name='crooked L', filename='crooked-L', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'i', 'i',
            '<', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCrookedSlanted5(PredefinedHandshape):
    def __init__(self, name='crooked slanted 5', filename='crooked-slanted-5', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'i', 'i',
            '{', '2', 'i', 'i', 'i',
            '{', '3', 'F', 'i', 'i',
            '{', '4', 'F', 'F', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCrookedU(PredefinedHandshape):
    def __init__(self, name='crooked U', filename='crooked-U', canonical=(
            'O', '{', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'd', '-', '-', '3', '-',
            '1', 'E', 'i', 'i',
            '=', '2', 'E', 'i', 'i',
            '<', '3', 'i', 'i', 'i',
            '=', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCrookedV(PredefinedHandshape):
    def __init__(self, name='crooked V', filename='crooked-V', canonical=(
            'O', '{', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'd', '-', '-', '3', '-',
            '1', 'E', 'i', 'i',
            '{', '2', 'E', 'i', 'i',
            '<', '3', 'i', 'i', 'i',
            '=', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeCrookedW(PredefinedHandshape):
    # fontmap: _
    def __init__(self, name='crooked W', filename='crooked-W', canonical=(
            'O', '{', 'i', 'i',
            'fr', 'd', NULL, '/', 'fr', 'd', '-', '-', '-', '4',
            '1', 'E', 'i', 'i',
            '{', '2', 'E', 'i', 'i',
            '{', '3', 'E', 'i', 'i',
            '<', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeD(PredefinedHandshape):
    def __init__(self, name='D', filename='D', canonical=(
            'O', '{', 'i', 'i',
            't', 'd', NULL, '/', 't', 'd', '-', '2', '-', '-',
            '1', 'E', 'E', 'E',
            '<', '2', 'i', 'i', 'i',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeDoubleCIndex(PredefinedHandshape):
    # fontmap: q
    def __init__(self, name='double C index', filename='double-C-index', canonical=(
            'O', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'i', 'i',
            '<', '2', 'i', 'i', 'i',
            '<', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeDoubleContractedL(PredefinedHandshape):
    def __init__(self, name='double contracted L', filename='double-contracted-L', canonical=(
            'O', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'i', 'E', 'E',
            '=', '2', 'i', 'E', 'E',
            '<', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeDoubleModifiedG(PredefinedHandshape):
    # fontmap: V
    def __init__(self, name='double modified G', filename='double-modified-G', canonical=(
            'O', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'F', 'E', 'E',
            '=', '2', 'F', 'E', 'E',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeE(PredefinedHandshape):
    def __init__(self, name='E', filename='E', canonical=(
            'O', '<', 'F', 'i',
            'b', 'd', NULL, '/', 't', 'd', '1', '2', '3', '-',
            '1', 'i', 'F', 'F',
            '=', '2', 'i', 'F', 'F',
            '=', '3', 'i', 'F', 'F',
            '=', '4', 'i', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeExtended8(PredefinedHandshape):
    # fontmap: r
    def __init__(self, name='extended 8', filename='extended-8', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'E', 'E',
            '{', '2', 'i', 'i', 'E',
            '<', '3', 'i', 'E', 'E',
            '{', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeExtendedA(PredefinedHandshape):
    # fontmap: 2
    def __init__(self, name='extended A', filename='extended-A', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'F', 'F', 'F',
            '=', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeExtendedB(PredefinedHandshape):
    # fontmap: x
    def __init__(self, name='extended B', filename='extended-B', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'E', 'E',
            '=', '2', 'E', 'E', 'E',
            '=', '3', 'E', 'E', 'E',
            '=', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeExtendedC(PredefinedHandshape):
    def __init__(self, name='extended C', filename='extended-C', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'i', 'i',
            '=', '2', 'E', 'i', 'i',
            '=', '3', 'E', 'i', 'i',
            '=', '4', 'E', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeExtendedK(PredefinedHandshape):
    def __init__(self, name='extended K', filename='extended-K', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'E', 'E',
            '<', '2', 'F', 'E', 'E',
            '=', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeExtendedR(PredefinedHandshape):
    def __init__(self, name='extended R', filename='extended-R', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'E', 'E',
            'x', '2', 'E', 'i', 'i',
            '<', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeExtendedU(PredefinedHandshape):
    # fontmap: W
    def __init__(self, name='extended U', filename='extended-U', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'E', 'E',
            '=', '2', 'E', 'E', 'E',
            '<', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeAIndex(PredefinedHandshape):
    def __init__(self, name='A index', filename='A-index', canonical=(
            'U', '<', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'i', 'F', 'i',
            '=', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeF(PredefinedHandshape):
    def __init__(self, name='F', filename='F', canonical=(
            'O', '{', 'i', 'i',
            't', 'd', NULL, '/', 't', 'd', '1', '-', '-', '-',
            '1', 'i', 'i', 'i',
            '{', '2', 'i', 'E', 'E',
            '{', '3', 'E', 'E', 'E',
            '{', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeFlatC(PredefinedHandshape):
    # fontmap: z
    def __init__(self, name='flat C', filename='flat-C', canonical=(
            'O', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'F', 'E', 'E',
            '=', '2', 'F', 'E', 'E',
            '=', '3', 'F', 'E', 'E',
            '=', '4', 'F', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeFlatClawedF(PredefinedHandshape):
    def __init__(self, name='flat clawed F', filename='flat-clawed-F', canonical=(
            'O', '{', 'E', 'E',
            'fr', 'd', NULL, '/', 'fr', 'd', '1', '-', '-', '-',
            '1', 'F', 'E', 'E',
            '{', '2', 'E', 'F', 'i',
            '{', '3', 'E', 'F', 'i',
            '{', '4', 'E', 'F', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeFlatCombinedIPlus1(PredefinedHandshape):
    # fontmap: i
    def __init__(self, name='flat combined I+1', filename='flat-combined-I+1', canonical=(
            'O', '{', 'E', 'E',
            'fr', 'd', NULL, '/', 'fr', 'd', '-', '2', '3', '-',
            '1', 'E', 'E', 'E',
            '<', '2', 'F', 'E', 'E',
            '=', '3', 'F', 'E', 'E',
            '=', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeFlatF(PredefinedHandshape):
    def __init__(self, name='flat F', filename='flat-F', canonical=(
            'O', '{', 'E', 'E',
            'fr', 'd', NULL, '/', 'fr', 'd', '1', '-', '-', '-',
            '1', 'F', 'E', 'E',
            '{', '2', 'i', 'E', 'E',
            '{', '3', 'E', 'E', 'E',
            '{', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeFlatM(PredefinedHandshape):
    def __init__(self, name='flat M', filename='flat-M', canonical=(
            'O', '=', 'F', 'i',
            'fr', 'd', NULL, '/', 'r', 'p', '-', '-', '-', '4',
            '1', 'F', 'E', 'E',
            '=', '2', 'F', 'E', 'E',
            '=', '3', 'F', 'E', 'E',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeFlatO(PredefinedHandshape):
    def __init__(self, name='flat O', filename='flat-O', canonical=(
            'O', '{', 'E', 'E',
            'fr', 'd', NULL, '/', 'fr', 'd', '1', '2', '-', '-',
            '1', 'F', 'E', 'E',
            '=', '2', 'F', 'E', 'E',
            '=', '3', 'F', 'E', 'E',
            '=', '4', 'F', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeFlatOpenF(PredefinedHandshape):
    def __init__(self, name='flat open F', filename='flat-open-F', canonical=(
            'O', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'F', 'E', 'E',
            '{', '2', 'E', 'E', 'E',
            '{', '3', 'E', 'E', 'E',
            '{', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeG(PredefinedHandshape):
    def __init__(self, name='G', filename='G', canonical=(
            'U', '=', 'E', 'E',
            'fr', 'p', NULL, '/', 'r', 'p', '1', '-', '-', '-',
            '1', 'F', 'E', 'E',
            '=', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeI(PredefinedHandshape):
    def __init__(self, name='I', filename='I', canonical=(
            'O', '=', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'm', '1', '-', '-', '-',
            '1', 'F', 'F', 'E',
            '=', '2', 'F', 'F', 'E',
            '=', '3', 'F', 'F', 'E',
            '=', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeK(PredefinedHandshape):
    def __init__(self, name='K', filename='K', canonical=(
            'O', '=', 'E', 'E',
            'fr', 'd', NULL, '/', 'r', 'p', '-', '2', '-', '-',
            '1', 'E', 'E', 'E',
            '<', '2', 'F', 'E', 'E',
            '=', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeL(PredefinedHandshape):
    def __init__(self, name='L', filename='L', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'E', 'E',
            '<', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeM(PredefinedHandshape):
    def __init__(self, name='M', filename='M', canonical=(
            'O', '=', 'F', 'i',
            'fr', 'd', NULL, '/', 'r', 'p', '-', '-', '-', '4',
            '1', 'F', 'i', 'i',
            '=', '2', 'F', 'i', 'i',
            '=', '3', 'F', 'i', 'i',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeMiddleFinger(PredefinedHandshape):
    # fontmap: N
    def __init__(self, name='middle finger', filename='middle-finger', canonical=(
            'O', '{', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'd', '-', '-', '3', '-',
            '1', 'i', 'F', 'F',
            '<', '2', 'i', 'E', 'E',
            '<', '3', 'i', 'F', 'F',
            '=', '4', 'i', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeModified5(PredefinedHandshape):
    def __init__(self, name='modified 5', filename='modified-5', canonical=(
            'O', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'E', 'E',
            '{', '2', 'E', 'E', 'E',
            '{', '3', 'E', 'E', 'E',
            '{', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeModifiedA(PredefinedHandshape):
    def __init__(self, name='modified A', filename='modified-A', canonical=(
            'U', '=', 'E', 'E',
            'fr', 'd', NULL, '/', 'r', 'p', '1', '-', '-', '-',
            '1', 'F', 'F', 'E',
            '=', '2', 'F', 'F', 'E',
            '=', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeModifiedD(PredefinedHandshape):
    # fontmap: G
    def __init__(self, name='modified D', filename='modified-D', canonical=(
            'O', '{', 'i', 'i',
            't', 'd', NULL, '/', 't', 'd', '-', '2', '3', '-',
            '1', 'E', 'E', 'E',
            '<', '2', 'i', 'i', 'i',
            '=', '3', 'i', 'i', 'i',
            '=', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeModifiedG(PredefinedHandshape):
    def __init__(self, name='modified G', filename='modified-G', canonical=(
            'O', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'F', 'E', 'E',
            '=', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeModifiedO(PredefinedHandshape):
    def __init__(self, name='modified O', filename='modified-O', canonical=(
            'O', '{', 'E', 'E',
            'fr', 'd', NULL, '/', 't', 'd', '1', '2', '-', '-',
            '1', 'F', 'i', 'i',
            '=', '2', 'F', 'i', 'i',
            '=', '3', 'F', 'i', 'i',
            '=', '4', 'F', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeModifiedY(PredefinedHandshape):
    def __init__(self, name='modified Y', filename='modified-Y', canonical=(
            'O', '<', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'F', 'F', 'E',
            '=', '2', 'F', 'F', 'E',
            '=', '3', 'F', 'F', 'E',
            '<', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeN(PredefinedHandshape):
    def __init__(self, name='N', filename='N', canonical=(
            'O', '=', 'i', 'i',
            'fr', 'd', NULL, '/', 'r', 'p', '-', '-', '3', '-',
            '1', 'F', 'i', 'i',
            '=', '2', 'F', 'i', 'i',
            '<', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeO(PredefinedHandshape):
    def __init__(self, name='O', filename='O', canonical=(
            'O', '{', 'i', 'i',
            't', 'd', NULL, '/', 't', 'd', '1', '2', '-', '-',
            '1', 'i', 'i', 'i',
            '=', '2', 'i', 'i', 'i',
            '=', '3', 'i', 'i', 'i',
            '=', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeOIndex(PredefinedHandshape):
    # fontmap: M
    def __init__(self, name='O index', filename='O-index', canonical=(
            'O', '{', 'i', 'i',
            't', 'd', NULL, '/', 't', 'd', '1', '-', '-', '-',
            '1', 'i', 'i', 'i',
            '<', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeOffsetF(PredefinedHandshape):
    def __init__(self, name='offset F', filename='offset-F', canonical=(
            'O', '{', 'E', 'E',
            'fr', 'p', NULL, '/', 'r', 'm', '1', '-', '-', '-',
            '1', 'i', 'i', 'i',
            '{', '2', 'i', 'E', 'E',
            '{', '3', 'E', 'E', 'E',
            '{', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeOffsetO(PredefinedHandshape):
    def __init__(self, name='offset O', filename='offset-O', canonical=(
            'O', '{', 'E', 'E',
            'fr', 'p', NULL, '/', 'r', 'd', '1', '-', '-', '-',
            '1', 'F', 'i', 'i',
            '=', '2', 'F', 'i', 'i',
            '=', '3', 'F', 'i', 'i',
            '=', '4', 'F', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeOpen8(PredefinedHandshape):
    # fontmap: t
    def __init__(self, name='open 8', filename='open-8', canonical=(
            'O', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'E', 'E',
            '{', '2', 'F', 'E', 'E',
            '<', '3', 'i', 'E', 'E',
            '{', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeOpenA(PredefinedHandshape):
    def __init__(self, name='open A', filename='open-A', canonical=(
            'U', '<', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'F', 'i', 'i',
            '=', '2', 'F', 'i', 'i',
            '=', '3', 'F', 'i', 'i',
            '=', '4', 'F', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeOpenE(PredefinedHandshape):
    # fontmap: 0
    def __init__(self, name='open E', filename='open-E', canonical=(
            'O', '<', 'F', 'i',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'F', 'F',
            '=', '2', 'E', 'F', 'F',
            '=', '3', 'E', 'F', 'F',
            '=', '4', 'E', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeOpenF(PredefinedHandshape):
    # fontmap: o
    def __init__(self, name='open F', filename='open-F', canonical=(
            'O', '{', 'i', 'i',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'i', 'i', 'i',
            '{', '2', 'i', 'E', 'E',
            '{', '3', 'E', 'E', 'E',
            '{', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeOpenOIndex(PredefinedHandshape):
    def __init__(self, name='open O index', filename='open-O-index', canonical=(
            'O', '{', 'i', 'i',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'i', 'i', 'i',
            '<', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)

#TODO: still need to be implemented
class HandshapeOpenPalm(PredefinedHandshape):
    def __init__(self, name='open palm', filename='open-palm', canonical=(
            '', '', '', '',
            '', '', NULL, '/', '', '', '', '', '', '',
            '1', '', '', '',
            '', '2', '', '', '',
            '', '3', '', '', '',
            '', '4', '', '', ''
    )):
        super().__init__(name, filename, canonical)


class HandshapeSpreadOpenO(PredefinedHandshape):
    def __init__(self, name='spread open O', filename='spread-open-O', canonical=(
            'O', '{', 'i', 'i',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'i', 'i', 'i',
            '{', '2', 'i', 'i', 'i',
            '{', '3', 'i', 'i', 'i',
            '{', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapePartiallyBentD(PredefinedHandshape):
    def __init__(self, name='partially bent D', filename='partially-bent-D', canonical=(
            'O', '{', 'i', 'i',
            't', 'd', NULL, '/', 't', 'd', '-', '2', '-', '-',
            '1', 'i', 'E', 'E',
            '=', '2', 'i', 'i', 'i',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeR(PredefinedHandshape):
    def __init__(self, name='R', filename='R', canonical=(
            'O', '=', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'm', '-', '-', '3', '-',
            '1', 'E', 'E', 'E',
            'x', '2', 'E', 'i', 'i',
            '<', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeRelaxedContracted5(PredefinedHandshape):
    # fontmap: ?
    def __init__(self, name='relaxed contracted 5', filename='relaxed-contracted-5', canonical=(
            'O', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'i', 'i', 'E',
            '<', '2', 'i', 'i', 'E',
            '<', '3', 'i', 'i', 'E',
            '<', '4', 'i', 'i', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeS(PredefinedHandshape):
    def __init__(self, name='S', filename='S', canonical=(
            'O', '=', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'm', '-', '2', '-', '-',
            '1', 'F', 'F', 'F',
            '=', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeSlanted4(PredefinedHandshape):
    def __init__(self, name='slanted 4', filename='slanted-4', canonical=(
            'O', '=', 'i', 'i',
            'u', 'd', NULL, '/', 'fr', 'M', '-', '-', '3', '-',
            '1', 'E', 'E', 'E',
            '{', '2', 'i', 'E', 'E',
            '{', '3', 'i', 'E', 'E',
            '{', '4', 'F', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeSlanted5(PredefinedHandshape):
    def __init__(self, name='slanted 5', filename='slanted-5', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'E', 'E',
            '{', '2', 'i', 'E', 'E',
            '{', '3', 'i', 'E', 'E',
            '{', '4', 'F', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeSlantedExtendedB(PredefinedHandshape):
    # fontmap: (
    def __init__(self, name='slanted extended B', filename='slanted-extended-B', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'E', 'E',
            'x-', '2', 'i', 'E', 'E',
            'x-', '3', 'i', 'E', 'E',
            'x-', '4', 'i', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeSlantedF(PredefinedHandshape):
    # fontmap: %
    def __init__(self, name='slanted F', filename='slanted-F', canonical=(
            'O', '{', 'i', 'i',
            't', 'd', NULL, '/', 't', 'd', '1', '-', '-', '-',
            '1', 'i', 'i', 'i',
            '{', '2', 'i', 'E', 'E',
            '{', '3', 'i', 'E', 'E',
            '{', '4', 'F', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)


class HandshapeSlantedV(PredefinedHandshape):
    def __init__(self, name='slanted V', filename='slanted-V', canonical=(
            'O', '{', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'd', '-', '-', '3', '-',
            '1', 'i', 'E', 'E',
            '{', '2', 'F', 'E', 'E',
            '=', '3', 'i', 'i', 'i',
            '=', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeSpreadC(PredefinedHandshape):
    def __init__(self, name='spread C', filename='spread-C', canonical=(
            'O', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'i', 'i',
            '{', '2', 'E', 'i', 'i',
            '{', '3', 'E', 'i', 'i',
            '{', '4', 'E', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeSpreadExtendedC(PredefinedHandshape):
    def __init__(self, name='spread extended C', filename='spread-extended-C', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'F', 'i',
            '{', '2', 'E', 'F', 'i',
            '{', '3', 'E', 'F', 'i',
            '{', '4', 'E', 'F', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeT(PredefinedHandshape):
    def __init__(self, name='T', filename='T', canonical=(
            'O', '=', 'i', 'E',
            'fr', 'd', NULL, '/', 'r', 'p', '-', '2', '-', '-',
            '1', 'i', 'F', 'i',
            '<', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeU(PredefinedHandshape):
    def __init__(self, name='U', filename='U', canonical=(
            'O', '{', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'd', '-', '-', '3', '-',
            '1', 'E', 'E', 'E',
            '=', '2', 'E', 'E', 'E',
            '<', '3', 'i', 'i', 'i',
            '=', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeV(PredefinedHandshape):
    def __init__(self, name='V', filename='V', canonical=(
            'O', '{', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'd', '-', '-', '3', '-',
            '1', 'E', 'E', 'E',
            '{', '2', 'E', 'E', 'E',
            '<', '3', 'i', 'i', 'i',
            '=', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeW(PredefinedHandshape):
    def __init__(self, name='W', filename='W', canonical=(
            'O', '{', 'i', 'i',
            'fr', 'd', NULL, '/', 'fr', 'd', '-', '-', '-', '4',
            '1', 'E', 'E', 'E',
            '{', '2', 'E', 'E', 'E',
            '{', '3', 'E', 'E', 'E',
            '<', '4', 'i', 'i', 'i'
    )):
        super().__init__(name, filename, canonical)


class HandshapeX(PredefinedHandshape):
    def __init__(self, name='X', filename='X', canonical=(
            'O', '=', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'm', '-', '2', '-', '-',
            '1', 'E', 'F', 'i',
            '<', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name, filename, canonical)


class HandshapeY(PredefinedHandshape):
    def __init__(self, name='Y', filename='Y', canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'F', 'F', 'E',
            '=', '2', 'F', 'F', 'E',
            '=', '3', 'F', 'F', 'E',
            '<', '4', 'E', 'E', 'E'
    )):
        super().__init__(name, filename, canonical)

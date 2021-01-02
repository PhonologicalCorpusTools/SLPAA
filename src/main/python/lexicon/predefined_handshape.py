from constant import NULL


class PredefinedHandshape:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name


class HandshapeEmpty(PredefinedHandshape):
    def __init__(self, name, canonical=(
            '', '', '', '',
            '', '', NULL, '/', '', '', '', '', '', '',
            '1', '', '', '',
            '', '2', '', '', '',
            '', '3', '', '', '',
            '', '4', '', '', ''
    )):
        super().__init__(name)

        self._canonical = canonical


class Handshape1(PredefinedHandshape):
    def __init__(self, name, canonical=(
            'O', '=', 'i', 'i',
            'fr', 'd', NULL, '/', 'b', 'm', '-', '2', '-', '-',
            '1', 'E', 'E', 'E',
            '<', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name)

        self._canonical = canonical


class Handshape3(PredefinedHandshape):
    def __init__(self, name, canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'E', 'E',
            '{', '2', 'E', 'E', 'E',
            '{', '3', 'F', 'F', 'E',
            '=', '4', 'F', 'F', 'E'
    )):
        super().__init__(name)

        self._canonical = canonical


class Handshape4(PredefinedHandshape):
    def __init__(self, name, canonical=(
            'O', '=', 'i', 'F',
            'u', 'd', NULL, '/', 'fr', 'M', '-', '-', '3', '-',
            '1', 'E', 'E', 'E',
            '{', '2', 'E', 'E', 'E',
            '{', '3', 'E', 'E', 'E',
            '{', '4', 'E', 'E', 'E'
    )):
        super().__init__(name)

        self._canonical = canonical


class Handshape5(PredefinedHandshape):
    def __init__(self, name, canonical=(
            'L', '{', 'E', 'E',
            '-', '-', NULL, '/', '-', '-', '-', '-', '-', '-',
            '1', 'E', 'E', 'E',
            '{', '2', 'E', 'E', 'E',
            '{', '3', 'E', 'E', 'E',
            '{', '4', 'E', 'E', 'E'
    )):
        super().__init__(name)

        self._canonical = canonical


class Handshape6(PredefinedHandshape):
    def __init__(self, name, canonical=(
            'O', '{', 'E', 'i',
            't', 'd', NULL, '/', 't', 'd', '-', '-', '-', '4',
            '1', 'E', 'E', 'E',
            '{', '2', 'E', 'E', 'E',
            '{', '3', 'E', 'E', 'E',
            '<', '4', 'i', 'i', 'i'
    )):
        super().__init__(name)

        self._canonical = canonical


class Handshape8(PredefinedHandshape):
    def __init__(self, name, canonical=(
            'O', '{', 'i', 'i',
            't', 'd', NULL, '/', 't', 'd', '-', '2', '-', '-',
            '1', 'E', 'E', 'E',
            '{', '2', 'i', 'i', 'i',
            '<', '3', 'E', 'E', 'E',
            '{', '4', 'E', 'E', 'E'
    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeA(PredefinedHandshape):
    def __init__(self, name, canonical=(
            'U', '=', 'E', 'E',
            'fr', 'd', NULL, '/', 'r', 'p', '1', '-', '-', '-',
            '1', 'F', 'F', 'F',
            '=', '2', 'F', 'F', 'F',
            '=', '3', 'F', 'F', 'F',
            '=', '4', 'F', 'F', 'F'
    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeAdductedF(PredefinedHandshape):
    def __init__(self, name, canonical=(
            'O', '{', 'i', 'i',
            't', 'd', NULL, '/', 't', 'd', '1', '-', '-', '-',
            '1', 'i', 'i', 'i',
            '=', '2', 'E', 'E', 'E',
            '=', '3', 'E', 'E', 'E',
            '=', '4', 'E', 'E', 'E'
    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeB1(PredefinedHandshape):
    def __init__(self, name, canonical=(
            'O', '=', 'i', 'i',
            'fr', 'd', NULL, '/', 'fr', 'M', '-', '-', '3', '-',
            '1', 'E', 'E', 'E',
            '=', '2', 'E', 'E', 'E',
            '=', '3', 'E', 'E', 'E',
            '=', '4', 'E', 'E', 'E'
    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeB2(PredefinedHandshape):
    def __init__(self, name, canonical=(
            'U', '=', 'E', 'i',
            'u', 'p', NULL, '/', 'r', 'M', '1', '-', '-', '-',
            '1', 'E', 'E', 'E',
            '=', '2', 'E', 'E', 'E',
            '=', '3', 'E', 'E', 'E',
            '=', '4', 'E', 'E', 'E'
    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeBase(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeBent1(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeBent4(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeBent5(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeBentB(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeBentCombinedIPlus1(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeBentExtendedB(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeBentExtendedU(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeBentExtendedV(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeBentI(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeBentL(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeBentMidfinger5(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeBentOffset1(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeBentR(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeBentThumbL(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeBentU(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeBentV(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeC(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCIndex(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClawed1(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClawed3(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClawed4(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClawed5(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClawedC(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClawedExtendedB(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClawedExtendedV(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClawedF(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClawedI(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClawedL(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClawedSpreadC(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClawedU(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClawedV(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClawedW(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClosedAIndex(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClosedBentD(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClosedDoubleModifiedG(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClosedG(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClosedModifiedG(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClosedV(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClosedW(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeClosedX(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCombinedIPlus1(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCombinedIPlusA(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCombinedILY(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCombinedUAndY(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCombinedYAndMiddle(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeContracted3(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeContracted5(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeContractedB(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeContractedC(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeContractedL(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeContractedU(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeContractedUIndex(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCovered8(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCoveredF(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCoveredO(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCoveredT(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCrooked1(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCrooked4(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCrooked5(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCrookedC(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCrookedExtendedB(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCrookedExtendedV(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCrookedF(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCrookedL(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCrookedSlanted5(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCrookedU(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCrookedV(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeCrookedW(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeD(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeDoubleCIndex(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeDoubleContractedL(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeDoubleModifiedG(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeE(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeExtended8(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeExtendedA(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeExtendedB(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeExtendedC(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeExtendedK(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeExtendedR(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeExtendedU(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeExtendedX(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeF(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeFlatC(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeFlatClawedF(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeFlatCombinedIPlus1(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeFlatF(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeFlatM(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeFlatO(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeFlatOpenF(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeG(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeI(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeK(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeL(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeM(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeMiddleFinger(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeModified5(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeModifiedA(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeModifiedD(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeModifiedF(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeModifiedG(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeModifiedO(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeModifiedY(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeN(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeO(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeOIndex(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeOffsetF(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeOffsetO(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeOpen8(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeOpenA(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeOpenE(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeOpenF(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeOpenOIndex(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeOpenPalm(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeOpenSpreadO(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapePartiallyBentD(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeR(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeRelaxedContracted5(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeS(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeSlanted4(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeSlanted5(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeSlantedB(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeSlantedExtendedB(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeSlantedF(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeSlantedV(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeSpreadC(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeSpreadExtendedC(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeT(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeU(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeV(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeW(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeX(PredefinedHandshape):
    def __init__(self, name, canonical=(
    )):
        super().__init__(name)

        self._canonical = canonical


class HandshapeY(PredefinedHandshape):
    def __init__(self, name, canonical=(

    )):
        super().__init__(name)

        self._canonical = canonical

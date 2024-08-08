from datetime import date

class Person:
    def __init__(self):
        self.role = ""
        self.name = ""
        self.initials = ""
        self.otherID = ""
        self.personaldescription = ""
        self.ethnicity = ""
        self.culturalaffiliation = ""
        self.hairdescription = ""
        self.clothingdescription = ""
        self.gender = ""
        self.pronouns = ""
        self.age = 0
        self.dateofbirth = None  # date.today()
        self.languages = ""
        self.dialects = ""
        self.placeoforigin = ""
        self.placeofresidence = ""
        self.otherplacesofinfluence = ""
        self.deafhearingstatus = ""
        self.fluencyoflanguages = ""
        self.ageofacquisitionoflanguages = ""
        self.parentsuseofSL = ""
        self.parentsdeafhearingstatus = ""
        self.siblingsuseofSL = ""
        self.siblingsdeafhearingstatus = ""
        self.othersuseofSL = ""
        self.othersdeafhearingstatus = ""
        self.acquisitionlocation = ""
        self.dducation = ""
        self.educationwithcommunity = ""
        self.familybelonging = ""
        self.linguisticawareness = ""
        self.experienceteachingSL = ""
        self.datasharingpermission = ""
        self.contactinfo = ""
        self.otherinfo = ""

    
class Source:
    def __init__(self):
        self.name = ""
        self.initials = ""
        self.otherID = ""
        self.citation = ""
        self.datasharingpermission = ""
        self.otherinfo = ""
    
    
class Recording:
    def __init__(self):
        self.signers = []  # list of Persons
        self.interlocutors = []  # list of Persons
        self.interpreters = []  # list of Persons
        self.datacollectors = []  # list of Persons
        self.PIs = []  # list of Persons
        self.location = ""
        self.sources = []  # list of Sources
        self.date = None  # date.today()
        self.elicitationmethod = ""
        self.equipment = ""
        self.setup = ""
        self.task = ""
        self.otherinfo = ""
        
    
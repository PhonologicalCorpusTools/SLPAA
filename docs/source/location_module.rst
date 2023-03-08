.. todo::
    current version in the program combined with details from system overview
    
.. comment::
    Outstanding issue: Allow any particular individual selection to be tagged as ‘major phonological location’ or ‘minor phonological location’ (e.g., if someone selects eyebrow / head, they can tag ‘head’ as the major phonological location and ‘eyebrow’ as the minor one). At the moment, we can only tag the whole module as a (major/minor) phonological or phonetic location.
    
.. _location_module:

***************
Location Module
***************

This :ref:`module` is used to code the **location** components of a sign. As many :ref:`instances<instance>` of this module as necessary can be called for any given sign coding. For more discussion on the use of modules in SLP-AA to encode information about signs, see :ref:`modularity`. 

Select the hand(s) involved in this instance of the module.

Module instances link to generic :ref:`x-slots<x_slot>` to record information about their timing relative to any others within a sign. For more information on the use of x-slots in SLP-AA, consult :ref:`timing_page`.

.. note::
    Each module instance can be tagged as a (major or minor) phonological location, a phonetic location, or both.

.. _location_type:

1. Location type
`````````````````

**Location options:** The highest node on the tree is an option to select whether the current module applies to a body location or a signing space location (necessary to choose one: either body-anchored, with a body location as a reference point and relation to that point, or purely spatial in terms of distances along axes in neutral space). The biggest difference between these is how linked contact modules work **(confirm this, notes in each applicable section below)**.

.. _body_location_section:

2. Body and body-anchored locations
```````````````````````````````````

.. _body_location:

I. Body location
================

.. note::
    **Linked contact modules**
    
    For this selection, the program expects a contact module. Some discussion has happened about how the program will prompt the user for this to be made clear. The important thing to note is that (only) this module will have a "save and add linked contact module" type of button in addition to the regular set of save buttons.

Choose from the body location list.

.. warning::
    **To include here:**
    
    * how to navigate the image view
        
        * selecting, zooming, flipping images, 'link' button
        
    * how to access the locations text list in the upper box
    * how to interact with sub-menus, how the columns are set up in the lower box
        
        * exists **only** relative to the selection in the locations list window
        
    * mutually exclusive location options within an instance of the module
    * **list of body locations**
        
        * maximal list of sub-areas and surfaces
        * for each location area, the set of sub-areas and surfaces that can apply for that area

.. _body_anchored_location:

II. Body-anchored location
==========================

.. note::
    **Linked contact modules**
    
    From the 'system overview' doc: It is possible to be body-anchored without having actual contact (e.g. it can be iconically anchored), so lack of physical contact is still indicated in the ‘contact’ module
    
    update: Kathleen mentioned that there's a system ambiguity between whether a body-anchored location has an associated 'no contact' module or whether it does not have an associated contact module at all, so I have something mixed up.

Select a reference location on the body, just as above for a body location. 

Then select the appropriate reference to that location.

**Will this option allow selecting sub-areas as well? yes.** We use abbreviations for joints in Hand Config (mcp, pip, dip for metacarpophalangeal, proximal interphalangeal, distal interphalangeal) – this will also be the case for the Location sub-menus. This makes room for “Relation” to take up a third column for body-anchored signing space locations.

.. _purely_spatial_location:

3. Purely spatial locations
```````````````````````````

.. note::
    **Linked contact modules**
    
    The program expects there to be no associated contact module for this type of location. If there is one, it will be flagged.

**Simple set of options, no additional images for this in the program.** The window with the body locations will be replaced with the applicable tree structure, so the module with this selection looks more like Movement. **(Does the same configuration of windows still apply, with two areas on the right side? There doesn't seem to be another necessary set of information, so I assume that it only shows the dropdown menu and the selected list item.)**

.. comment::
    **(Module summary from system overview)**
    
    This module applies to:
        [ ] H1
        [ ] H2
    
    Timing: Timing options as listed above.
    
    Location:
        ( ) Body-anchored location 
            [If this is coded, a contact module is expected] 
            Location: Choose from the body location list > “KCH Body locations-Proposal_streamlined”
        ( ) Signing space location 
            [If this is coded, a contact module is not expected to be associated with it and if there is one, it should be flagged]
            ( ) Body-anchored spatial location 
                [(modified) body location as reference for locations on the vertical and horizontal axes plus distance from that location]
                    Reference location: Body location option from the body location list under > “KCH Body locations-Proposal_streamlined”
                    Relation to the body location 
                    [max one from each column (and don’t have to have one from each column selected!)]
                        ( ) Above            ( ) In front of       ( ) Ipsilateral to
                            ( ) Far              ( ) Far               ( ) Far
                            ( ) Med.             ( ) Med.              ( ) Med.
                            ( ) Close            ( ) Close             ( ) Close
                        ( ) Below            ( ) Behind            ( ) Contralateral to
                            ( ) Far              ( ) Far               ( ) Far
                            ( ) Med.             ( ) Med.              ( ) Med.
                            ( ) Close            ( ) Close             ( ) Close
        ( ) Purely spatial location 
            [code locations on the vertical, horizontal, and sagittal axes]
            [expect one in each column]
            [defaults could be mid / in front med / central]
                Vertical axis:    Sagittal axis:      Horizontal axis:
                  ( ) High          ( ) In front        ( ) Ipsi 
                  ( ) Mid               ( ) Far             ( ) Far
                  ( ) Low               ( ) Med.            ( ) Med.
                                        ( ) Close           ( ) Close
                                    ( ) Behind          ( ) Central
                                        ( ) Far         ( ) Contra 
                                        ( ) Med.            ( ) Far
                                        ( ) Close           ( ) Med.
                                                            ( ) Close

    Allow any instance of the location module to be tagged as:  
        ( ) Phonological location
            ( ) Major location
            ( ) Minor location
        ( ) Phonetic location



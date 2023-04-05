.. todo::
    list of body locations and suboptions
        may be better to include the full list in a separate page
    axis of relation and contact?
    acting as a connected unit description
    
.. comment::
    Outstanding issue: Allow any particular individual selection to be tagged as ‘major phonological location’ or ‘minor phonological location’ (e.g., if someone selects eyebrow / head, they can tag ‘head’ as the major phonological location and ‘eyebrow’ as the minor one). At the moment, we can only tag the whole module as a (major/minor) phonological or phonetic location.
    
.. _location_module:

***************
Location Module
***************

This :ref:`module` is used to code the **location** components of a sign. As many :ref:`instances<instance>` of this module as necessary can be called for any given sign coding. For more discussion on the use of modules in SLP-AA to encode information about signs, see :ref:`modularity`. 

Select the hand(s) involved in this instance of the module.

.. warning::
    **Both hands acting as a connected unit**
    
    From system overview: this option is intended to accomplish a similar thing as in the movement module, in that it allows a single specification to be given for H1 while applying to both hands. But e.g. if the specification is ‘ipsilateral shoulder’ then it is interpreted as meaning that both hands are on the SAME shoulder, ipsilateral for H1 (as in `SINCE <https://asl-lex.org/visualization/?sign=since>`_ or `RESPONSIBILITY <https://asl-lex.org/visualization/?sign=responsibility>`_) – it could be used in conjunction with an axis of relation and / or a connected movement module, but it wouldn’t have to

Module instances link to generic :ref:`x-slots<x_slot>` to record information about their timing relative to any others within a sign. For more information on the use of x-slots in SLP-AA, consult :ref:`timing_page`.

.. note::
    Each module instance can optionally be tagged as a phonological location, a phonetic location, or both of these at once. If the instance of the module is selected as a phonological location, it can optionally be further described as a major or minor phonological location.
    
.. warning::
    **(For Kathleen and Oksana)**
    
    There should be some discussion somewhere around here for the difference between our broad use of 'location' vs. how the term is usually defined phonologically.

**(Start with a basic description of the highest-level options for types of locations available in the program.)**

.. _body_location_section:

1. Body and body-anchored locations
```````````````````````````````````

**(Explain differences between how these options function in the program, and list possible uses for the distinction.)**

.. _body_location:

I. Body location
================

.. note::
    **Linked contact modules**
    
    For this selection, the program expects a linked contact module. The module will be flagged if there is no contact module. (Some discussion has happened about how the program will prompt the user for this to be made clear. The important thing to note is that *only* this module will have a "save and add linked contact module" type of button in addition to the regular set of save buttons.)

Choose from the :ref:`location_list` or navigate the image view window to select a body location.

.. warning::
    **To include here:**
    
    * how to navigate the image view
        
        * selecting, zooming, flipping images, 'link' button
        * **(overlapping regions?)**
        
    * how to access the locations text list in the dropdown box, and how to add them to the top window
    * how to interact with sub-menus, how the columns are set up in the lower window
        
        * exists **only** relative to the selection in the locations list window
        
    * mutually exclusive location options within an instance of the module

.. _body_anchored_location:

II. Body-anchored location
==========================

.. note::
    **Linked contact modules**
    
    The program expects there to be no associated contact module for this type of location. If there is one, it will be flagged.

Select a reference location from the :ref:`location_list`. 

Then select the appropriate reference to that location. **(max one from each axis, not required to choose one from each)**

.. list-table::
   :widths: 30 30 30
   :header-rows: 1

   * - Horizontal axis
     - Vertical axis
     - Sagittal axis
   * - **Ipsilateral to**
     - **Above**
     - **In front of**
   * -   Far
     -   Far
     -   Far
   * -   Med.
     -   Med.
     -   Med.
   * -   Close
     -   Close
     -   Close
   * - **Contralateral to**
     - **Below**
     - **Behind**
   * -   Far
     -   Far
     -   Far
   * -   Med.
     -   Med.
     -   Med.
   * -   Close
     -   Close
     -   Close
    
.. warning::
    **Will this option allow selecting sub-areas as well? yes.** We use abbreviations for joints in Hand Config – this will also be the case for the Location sub-menus. This makes room for “Relation” to take up a third column for body-anchored signing space locations.

.. _purely_spatial_location:

2. Purely spatial location
``````````````````````````

.. note::
    **Linked contact modules**
    
    The program expects there to be no associated contact module for this type of location. If there is one, it will be flagged.

**Simple set of options, no additional images for this in the program.** The window with the body locations will be replaced with the applicable tree structure, so the module with this selection looks more like Movement. **(Does the same configuration of windows still apply, with two areas on the right side? There doesn't seem to be another necessary set of information, so I assume that it only shows the dropdown menu and the selected list item.)**

Make exactly one selection from each axis:

.. list-table::
   :widths: 30 30 30
   :header-rows: 1

   * - Horizontal axis
     - Vertical axis
     - Sagittal axis
   * - **Ipsi**
     - **High**
     - **In front**
   * -   Far
     - **Mid**
     -   Far
   * -   Med.
     - **Low**
     -   Med.
   * -   Close
     -
     -   Close
   * - **Central**
     - 
     -
   * - **Contra**
     -
     - **Behind**
   * -   Far
     -
     -   Far
   * -   Med.
     -
     -   Med.
   * -   Close
     -
     -   Close

**(Defaults may be set as central/mid/in front med., though I'm not sure this is decided concretely.)**

3. Axis of relation (between H1 and H2)
```````````````````````````````````````

**(Some cases where we anticipate that this will be useful: connected signs, and possibly classifier constructions.)** No mention of how this Location type is expected to interact with Contact.

Make up to one selection from each axis to describe the relationship between H1 and H2. You can also select the axis of relation itself without specifying the way the hands are arranged along that axis.

* **Horizontal**

    * H1 is to H1 side of H2
    * H1 is to H2 side of H2

* **Vertical**

    * H1 is above H2
    * H1 is below H2

* **Sagittal**

    * H1 is in front of H2
    * H1 is behind H2

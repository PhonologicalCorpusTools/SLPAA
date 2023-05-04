.. todo::
    text introductions for both location type sections
    note on connectedness
    finish the body location section
    default location type in global settings?
    "add/go to linked relation module" button?
    
.. comment::
    Outstanding issue: Allow any particular individual selection to be tagged as ‘major phonological location’ or ‘minor phonological location’ (e.g., if someone selects eyebrow / head, they can tag ‘head’ as the major phonological location and ‘eyebrow’ as the minor one). At the moment, we can only tag the whole module as a (major/minor) phonological or phonetic location.
    
.. _location_module:

***************
Location Module
***************

This :ref:`module` is used to code the **location** components of a sign. As many :ref:`instances<instance>` of this module as necessary can be called for any given sign coding. For more discussion on the use of modules in SLP-AA to encode information about signs, see :ref:`modularity`.

.. warning::
    **(For Kathleen and Oksana)**
    
    There should be some discussion somewhere around here for the difference between our broad use of 'location' vs. how the term is usually defined phonologically.

Select the hand(s) involved in this instance of the module.

.. note::
    **As a connected unit**
    
    (Add here) reference Morgan and link to the glossary entry :ref:`connected`.
    
    From system overview: this option is intended to accomplish a similar thing as in the movement module, in that it allows a single specification to be given for H1 while applying to both hands. But e.g. if the specification is ‘ipsilateral shoulder’ then it is interpreted as meaning that both hands are on the SAME shoulder, ipsilateral for H1 (as in `SINCE <https://asl-lex.org/visualization/?sign=since>`_ or `RESPONSIBILITY <https://asl-lex.org/visualization/?sign=responsibility>`_) – it could be used in conjunction with an axis of relation and / or a connected movement module, but it wouldn’t have to.

Module instances link to generic :ref:`x-slots<x_slot>` to record information about their timing relative to any others within a sign. For more information on the use of x-slots in SLP-AA, consult :ref:`timing_page`.

.. note::
    **Phonological locations**
    
    Each module instance can optionally be tagged as a phonological location, a phonetic location, or both of these at once. If it is selected to be a phonological location, it can optionally be further described as a major or minor phonological location. These selections will apply to the entire instance of the module.

There are three possible types of locations that can be described in this module. There are :ref:`Body and body-anchored locations<body_location_section>`, which have the same functionality in this module, and there are :ref:Purely spatial locations<purely_spatial_location>`.

Most Location options adhere to one of two models to describe the horizontal sides of the body, either **relative** (:ref:`ipsilateral`/:ref:`contralateral` side) or **absolute** (H1/H2 side). These are described in greater detail in :ref:`Symmetry<symmetry_section>`. These options can be toggled separately for different modules, and the relative set applies by default for Location. See the :ref:`global_settings` for how to change these options.

.. _body_location_section:

1. Body and body-anchored locations
```````````````````````````````````

**(Intro: what is a body/body-anchored location in general?)**

**(Explain differences between how the two function in the program: identical within the module, different implications for analysis. List possible uses for the distinction.)** Note that these movement types are functionally identical within an instance of Location, but differences surface in other ways, like how a linked instance of the :ref:`relation_module` might be coded. The distinction can also be helpful for searching and analysis.

.. note::
    **Linked modules**
    
    For these kinds of locations, the program expects a linked instance of the :ref:`relation_module`. This instance of the module will be flagged if it is unlinked. (Some discussion has happened about how the program will prompt the user for this to be made clear. The important thing to note is that *only* Location will have a "save and add linked relation module" type of button in addition to the regular set of save buttons.)
    
    These kinds of locations can also take a linked instance of the :ref:`hand_part_module` if desired.

Choose from the list of :ref:`predefined_locations` or navigate the image view window to select a body location.

.. warning::
    **To include here:**
    
    * how to navigate the image view
        
        * selecting, zooming, flipping images, 'link' button
        * **(overlapping regions?)**
        
    * how to access the locations text list in the dropdown box, and how to add them to the top window
    * how to interact with sub-menus, how the columns are set up in the lower window
        
        * these exist **only** relative to the selection in the locations list window
        
    * mutually exclusive location options within an instance of the module

.. _purely_spatial_location:

2. Purely spatial location
``````````````````````````

**(What this section is for/how it differs from body locations.)**

.. note::
    **Linked modules**
    
    The program expects there to be no associated :ref:`Hand Part<hand_part_module>` or :ref:`relation_module` for this type of location. If there is one, it will be flagged.

Make exactly one selection from each axis (each represented by a column in the table below), leaving no axis unspecified. Some axis locations allow an optional distance specification (close/medium/far) to add more detail about the degree of extension of the arms. **(Defaults may be central/mid/in front medium, though I'm not sure this is decided concretely.)**

Note that only one set of options for the horizontal axis will apply, depending on user preference, and the relative set applies by default for Location. See :ref:`Symmetry<symmetry_section>` for more information, and :ref:`global_settings` to change which set of options appears in each module.

.. list-table::
   :widths: 40 40 30 30
   :header-rows: 1

   * - Horizontal (relative)
     - Horizontal (absolute)
     - Vertical
     - Sagittal
   * - **Ipsi**
     - **H1 side**
     - **High**
     - **Distal**
   * -   Close
     -   Close
     - **Mid**
     -   Close
   * -   Medium
     -   Medium
     - **Low**
     -   Medium
   * -   Far
     -   Far
     -
     -   Far
   * - **Central**
     - **Central**
     - 
     -
   * - **Contra**
     - **H2 side**
     -
     - **Proximal**
   * -   Close
     -   Close
     -
     -   Close
   * -   Medium
     -   Medium
     -
     -   Medium
   * -   Far
     -   Far
     -
     -   Far

See :ref:`signing_space` for a visual description of the axis system.

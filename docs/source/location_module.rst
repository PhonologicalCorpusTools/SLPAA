.. todo::
    current version in the program combined with details from system overview
    table for location menu?
    
.. _location_module:

***************
Location Module
***************

This :ref:`module` is used to code the **location** components of a sign. As many :ref:`instances<instance>` of this module as necessary can be called for any given sign coding. For more discussion on the use of modules in SLP-AA to encode information about signs, see :ref:`modularity`. 

Select the hand(s) involved in this instance of the module.

Module instances link to generic :ref:`x-slots<x_slot>` to record information about their timing relative to any others within a sign. For more information on the use of x-slots in SLP-AA, consult :ref:`timing_page`.

.. _location_type:

1. Location type
`````````````````

**Location options: The highest node on the tree is an option to select whether the current module applies to a body location or a signing space location (either body-anchored or purely spatial). The biggest difference between these is how linked contact modules work.**

.. note::
    Each module instance can be tagged as a (major/minor) phonological location and/or as a phonetic location.

.. _body_location:

I. Body location
================

.. note::
    For this selection, the program expects a contact module. Some discussion has happened about how the program will prompt the user for this to be made clear.
    
    From the 'system overview' doc: It is possible to be body-anchored without having actual contact; it can be iconically anchored; lack of physical contact is still indicated in the ‘contact’ module

Choose from the body location list. The interactibility and design of this module is underway.

.. warning::
    To include here:
    
    - interaction with the module UI 
        - how to navigate the image view
            - selecting, zooming, flipping images, 'link' button
        - how to access the locations list and sub-menus
        
    - design
        - mutually exclusive location options within an instance of the module
        - **what the list of body locations is** -- use a table? 
        - sign examples, if any??

.. _signing_space_location:

II. Signing space location
==========================

.. note::
    The program expects there to be no associated contact module for this type of location. If there is one, it will be flagged.

**two distinct sub-options within this choice (available in each instance), necessary to choose one: body-anchored spatial location (body location as a reference point, and relation to that point), OR purely spatial location (indicated by position in terms of each axis, centered mid-body a little in front of the signer).**

.. _body_anchored_location:

a) Body-anchored location
~~~~~~~~~~~~~~~~~~~~~~~~~

Select a reference location on the body, just as above for a body location. Then select the appropriate reference to that location.

**Will this option allow selecting sub-areas as well?**

.. _purely_spatial_location:

b) Purely spatial location
~~~~~~~~~~~~~~~~~~~~~~~~~~

**simple set of options, no additional images for this in the program**


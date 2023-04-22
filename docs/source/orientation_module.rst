.. todo::
    relative orientation??
        - orientation + hand part together
        - requires at least one instance of Location
        - minimal pair for relative orientation: JUSTIFY and STOP
    screenshot of the module when it's ready

.. _orientation_module:

******************
Orientation Module
******************

This :ref:`module` is used to code the **hand orientation** components of a sign. As many :ref:`instances<instance>` of this module as necessary can be called for any given sign coding. For more discussion on the use of modules in SLP-AA to encode information about signs, see :ref:`modularity`. 

Select the hand(s) involved in this instance of the module.

Module instances link to generic :ref:`x-slots<x_slot>` to record information about their timing relative to any others within a sign. For more information on the use of x-slots in SLP-AA, consult :ref:`timing_page`.

.. _orientation_selection:

1. Absolute orientation
```````````````````````

Orientation modules can be :ref:`auto-generated<auto_gen>` based on the existing coded :ref:`Movement Modules<movement_module>` for that sign. You can change the program's :ref:`automated_processes` in the :ref:`global_settings`.

The orientation of the hand is described using only two specifications: the palm direction and the finger root direction. These terms will be further explained below in their respective sections. Both directions must be selected for a full and accurate coding of orientation.

Note that directions on the horizontal axis can be set to either be defined in **absolute** (H1 side / H2 side) or **relative** (:ref:`ipsilateral` / :ref:`contralateral`) directions for each module. The default option for Orientation is to use relative directions, but this can be changed in the :ref:`global_settings`. For more information about the horizontal axis, see :ref:`Symmetry<symmetry_section>`.

.. _palm_direction:

I. Palm direction
=================

Palm direction refers to the direction that the friction surface of the hand (minus the fingers) is facing. You can make at most one selection from each set of axis options. For more information about the spatial options available in SLP-AA, see :ref:`Axes<axes_entry>`.

Keep in mind that a single :ref:`instance` of the module is meant to convey only one orientation, so selecting a combination of axes should be interpreted as a diagonal or angled direction of orientation with all of the selections applying simultaneously. To instead indicate a sequence of orientations in different directions, create multiple instances of the Orientation module, associate them with separate (and sequential) :ref:`timing values<timing_page>`, and select the appropriate set of directions for each one.

.. list-table::
    :widths: 30 30 30
    :header-rows: 1

    * - Horizontal axis
      - Vertical axis
      - Sagittal axis
    * - **Ipsilateral**
      - **Up**
      - **Distal**
    * - **Contralateral**
      - **Down**
      - **Proximal**
    * -    OR
      -
      -
    * - **H1 side**
      -
      -
    * - **H2 side**
      -
      -
    
In the sign `GAME <https://asl-lex.org/visualization/?sign=game>`_, the palm direction would be coded as *proximal* for the duration of the sign.

.. _finger_root:

II. Finger root direction
=========================

Finger root direction refers to the direction that the fingertips would point in if they were fully extended; that is, it corresponds to the direction of the **proximal interphalangeal joints**. You can make at most one selection from each set of axis options. For more information about the spatial options available in SLP-AA, see :ref:`Axes<axes_entry>`.

Keep in mind that a single :ref:`instance` of the module is meant to convey only one orientation, so selecting a combination of axes should be interpreted as a diagonal or angled direction of orientation with all of the selections applying simultaneously. To instead indicate a sequence of orientations in different directions, create multiple instances of the Orientation module, associate them with separate (and sequential) :ref:`timing values<timing_page>`, and select the appropriate set of directions for each one.

.. list-table::
    :widths: 30 30 30
    :header-rows: 1

    * - Horizontal axis
      - Vertical axis
      - Sagittal axis
    * - **Ipsilateral**
      - **Up**
      - **Distal**
    * - **Contralateral**
      - **Down**
      - **Proximal**
    * - OR
      -
      -
    * - **H1 side**
      -
      -
    * - **H2 side**
      -
      -

In the sign `GAME <https://asl-lex.org/visualization/?sign=game>`_, the finger root direction would be coded as *contralateral* for both hands (with the relative set of axis endpoints) for the duration of the sign, or separate instances of the module for each hand can indicate that H1 is directed toward the *H2 side* and H2 is directed toward the *H1 side* (with the absolute set of axis endpoints).

**Give a sample coding to show how the whole orientation module would look for a certain sign.**

.. _relative_orientation:

2. Relative orientation
```````````````````````

**(Add here)**

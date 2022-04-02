.. |Movement module overview| image:: images/placeholder.png
    :width: 800
    :align: center
    :alt: Image description.

.. todo::
    build a targets for an x-slot glossary entry with the title _x-slot
    think about where and how detailed information for program behaviour will be represented
    create a dummy page to link to for the signing space description
    
.. comment::
    The places where I intend to add a link to another (currently non-existent) docs section are marked as a code block

.. _movement_module: 

***************
Movement Module
***************

The **movement module** is the first to be coded for each sign after :ref:`sign type<sign_type_module>`. The movement information is what is used to generate the appropriate number of :ref:`x-slots<x-slot>` for the sign. See the section on ``how x-slots are auto-generated`` **(program functionality page? auto-generation and autofilling?)**. 

|Movement module overview|

Any movement in a sign can be described as either a :ref:`perceptual_shape` or a :ref:`joint_specific_movement`. When there are different (simultaneous or sequential) movements within one sign, each individual movement must be given its own module. The timing of the module(s) will be made clear in the ``x-slot visualization``.

*More fine-grained articulatory detail can be added by specifying other joint movements involved in the production of each component ...*

.. _perceptual_shape_entry:

1. Movement type - Perceptual shape
````````````````````````````````````

.. _shape_entry:

I. Shape
=========

**(Describe the shape options, show some sample signs)**

.. _axis_direction_entry:

II. Axis direction
===================

An axis of movement (or a combination of axes) can be selected to describe the direction of any movement with perceptual shape. See ``the signing space`` for a visual description of these options. **(Link to a separate .rst file in the docs on planes, axes, and divisions of neutral space)** 

The axis direction encodes the endpoint of the movement relative to the starting point… **(use example signs)**

.. note::
    This seems to lend more to convention than explicit description. Stick to the available options and what happens when you select each one.

.. _plane_entry:

III. Plane
==========

**(Refer to the global options section for setting clockwise directionality. Note that the option to select a plane is not necessary for straight paths, but the option is not disabled for straight paths (?))** 

.. comment::
    Note for Nico: you can use a cross-reference to the global options in order to actual describe the default options
    e.g., "See :ref:`global_options` to set preferences." --Kathleen

.. _joint-specific_movement_entry:

2. Movement type - Joint-specific movements
```````````````````````````````````````````

...

.. _joint_movement_entry:

3. Joint movements
``````````````````

**(Important to mention: this section can freely combine with either movement type, the applicable joint movements for any joint-specific movement is auto-filled)**

.. _movement_characteristic_entry:

4. Movement characteristics
```````````````````````````

...

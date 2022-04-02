.. todo::
    insert image of the movement module
    think about where and how detailed information for program behaviour will be represented
    create a dummy page to link to for the signing space description
    
.. comment::
    The places where I intend to add a link to another (currently non-existent) docs section are marked as a code block
    
.. comment::
    I often use "describe" as a verb for adding detail about a sign. Would it be better to use e.g. "transcribe" or "code" instead?

.. _movement_module: 

***************
Movement Module
***************

The **movement module** is the first to be coded for each sign after the :ref:`sign type module<sign_type_module>`. The movement information is what is used to generate the appropriate number of :ref:`x-slots<x_slot>` for the sign. See the section on ``how x-slots are auto-generated`` **(program functionality page? auto-generation and autofilling?)** to learn more about this process. 

Here's how the movement window looks in the program: 

.. image:: images/placeholder.png
    :width: 800
    :align: center
    :alt: Image description.


Any movement in a sign can be described as either a :ref:`perceptual_shape` or a :ref:`joint_specific_movement`. When there are different (simultaneous or sequential) movements within one sign, each individual movement must be given its own module. The timing of the module(s) can be adjusted in the x-slot visualization.

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

.. warning::
    This seems to lend more to convention than explicit description. Stick to the available options and what happens in the program when you select them. Areas for flexibility of use can be mentioned after that.

.. _plane_entry:

III. Plane
==========

**(Refer to the global settings section for checking/changing clockwise directionality. Note that the option to select a plane is not necessary for straight paths, but the option is not disabled for straight paths (?))** 

.. comment::
    Note for Nico: you can use a cross-reference to the global options in order to actual describe the default options
    e.g., "See :ref:`global_settings` to set preferences." --Kathleen

.. _joint-specific_movement_entry:

2. Movement type - Joint-specific movements
```````````````````````````````````````````

...

.. _joint_movement_entry:

3. Joint movements
``````````````````

The **joint movements** section can be used to add more fine-grained detail about the specific joint articulations of the movement component described in the current module. This option is available for both :ref:`perceptual shapes<perceptual_shape>` and :ref:`joint-specific movements<joint_specific_movement>`. It is not necessary to manually code the joint movements that are predictable from any joint-specific movement, as this will be done ``automatically`` **(program functionality page? auto-generation and autofilling?)** by the program. **(add an example or two)**

**(A note on user flexibility: this section can encode the phonetics of proximalization/distalization, differences in sizes of the same perceptual shape based on the joints involved, etc.)**

.. _movement_characteristic_entry:

4. Movement characteristics
```````````````````````````

...

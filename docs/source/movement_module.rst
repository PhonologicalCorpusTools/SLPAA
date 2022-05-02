.. comment::
    The places where I intend to add a link to a currently non-existent docs section/page are marked as a code block temporarily
    
.. todo::
    enter examples: reuse signs from other docs pages where possible, and check the team meeting document
    add relevant information to the handshape change section
    finish writing up the joint activity section
    create some of the missing pages that would be linked here
    decide what kinds of information might go into a (possible) signing space description

.. _movement:

***************
Movement Module
***************

This module is used to code the movement components of a sign.

After creating a sign and entering the :ref:`sign-level information<sign_level_info>` and coding the :ref:`sign type module<sign_type>`, code the **movement module(s)** for the sign first before moving on to other ``sign modules`` **(link to a page on the idea of modularity?)**. The movement information is used by the program to generate the appropriate number of :ref:`x-slots<x_slot>` for the sign if ``auto-generation`` **(documentation on auto-generation and autofilling)** is enabled. Whether x-slots are created automatically or manually by the user, they are the timing basis that the ``sign modules`` build upon and so they must be specified first. (See the ``global options`` for how to change the program's default auto-generation behaviour.)

.. note::
    There is often some flexibility as to whether different components of movement can be counted as separate modules or part of the same one. At minimum, for signs with multiple (simultaneous and/or sequential) movements, give each separate movement type **(does this need a glossary entry?)** its own module. That is, code any :ref:`joint-specific movements<joint_specific_movement>` separately from any movements with :ref:`perceptual_shape`, as these are mutually exclusive by design. Likewise, a module designated as a :ref:`handshape_change` cannot also have specifications for a joint-specific movement or a movement with perceptual shape. 
 The timing of the modules can then be adjusted in the x-slot visualization of the ``sign summary window``. 

**(Give some example signs here with some broad discussion of which components of movement could (and must) be counted as a separate module.)**

.. _movement_type_entry:

1. Movement type
`````````````````

Select the movement type **(glossary entry?)** for the current module.

Keep in mind that you can add more detail on the joint articulations for any type of movement in the :ref:`joint activity<joint_activity_entry>` section of the module, and that the number of modules needed to describe a movement may depend on your choices in terms of its :ref:`movement characteristics<movement_chars>`.

.. _perceptual_shape_entry:

I. Perceptual shape
===================

Code the specifications for a movement with :ref:`perceptual_shape`. This could be the only movement in a sign, as in `NORTH<https://asl-lex.org/visualization/?sign=north>`_, or a single component of a more complex sign, like the vertical motions in this version of `MILK<https://asl-lex.org/visualization/?sign=milk_2>`_.

.. _shape_entry:

a) Shape
~~~~~~~~

Select the shape of the movement.

**(Note especially that combinations of straight movements will each get their own complete module, so code these in sequential order. Also note that the shape options are mutually exclusive, so something like circle+straight will need two sequential modules, each with perceptual shape. Does this case need the first shape signed to be the first coded as well? That seems intuitive to do anyway but I feel like it's also necessary for the x-slot linking process.)**

**(New shape labels will also be able to be created by the user.)**

.. note::
    Give at least one example for each shape option.

.. _axis_direction_entry:

b) Axis direction
~~~~~~~~~~~~~~~~~

Select an axis (or a combination of axes) that describe the direction of movement. 


For circular motions, select the direction that extends from the beginning of the movement toward the midpoint of the first cycle.

.. comment::
    See a description of the ``signing space`` for a visual representation of these options. (Link to a separate .rst file in the docs on planes, axes, and divisions of neutral space)

.. note::
    Insert examples here for a few signs. Include some options of how to deal with circles and loops, e.g. a pair of circles that have the *same* plane and clockwise directionality but *different* axis directions.

See the :ref:`global_settings` page for how to switch between ``relative directions`` **(glossary)** and ``absolute positions`` **(glossary)** across the ``line of bilateral symmetry`` **(I'm not sure if this is actually necessary, but I would like to include it for extra information! The terminology is taken from Battison, but I'm not thrilled about calling it a line)**.

.. _plane_entry:

c) Plane
~~~~~~~~

Select a plane (or a combination of planes) that fully encloses the movement described in the current module. For each selected plane, you can also choose a directionality.

This section is automatically specified by the program as 'not relevant' for movement modules with a 'straight' perceptual shape.

.. comment::
    See a description of the ``signing space`` for a visual representation of these options. (Link to a separate .rst file in the docs on planes, axes, and divisions of neutral space)

.. note::
    Insert a few sign examples for different shapes, and include at least one or two that uses a combination of planes to show how this should be interpreted.

See the :ref:`global_settings` page to find the default clockwise directionality for each plane, and how to change these. Also see :ref:`global_settings` for how to switch between ``relative directions`` **(glossary)** and ``absolute positions`` **(glossary)** across the ``line of bilateral symmetry`` **(see above)**.

.. _joint_specific_movement_entry:

II. Joint-specific movements
============================

...

.. _handshape_change_entry:

III. Handshape change
=====================

Code in this section whether the module describes a :ref:`handshape_change`. This selection cannot be combined with the selections for a :ref:`joint_specific_movement` or movement with :ref:`perceptual_shape`.



.. _joint_activity_entry:

2. Joint activity
``````````````````

Use the **joint activity** section to add more fine-grained detail about any joint movements related to the current module. If the module describes a :ref:`joint_specific_movement`, then the program will ``autofill`` **(program functionality page? auto-generation and autofilling?)** the joint movements that are predictable from the selections made earlier in the :ref:`movement type section<joint_specific_movement_entry>`. See :ref:`global_settings` for how to change the program's default autofill behaviour.

**(A note on user flexibility: this section can encode the phonetics of proximalization/distalization, differences in sizes of the same perceptual shape based on the joints involved, etc.)**

.. _movement_chars:

3. Movement characteristics
```````````````````````````

...

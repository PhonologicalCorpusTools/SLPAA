.. comment::
    The places where I intend to add a link to a currently non-existent docs section/page are marked as a code block temporarily
    
.. todo::
    add examples where indicated: reuse signs from other docs pages where possible, and check the shared files when needed
    finish writing up the joint activity section
    start movement characteristics description
    create a modularity page
    pick a (preliminary) name for the signing space page
    glossary entry for "module"?
    combinations of planes and axes

.. _movement:

***************
Movement Module
***************

This ``module`` **(glossary entry? if not then link to modularity page)** is used to code the movement components of a sign.

After creating a sign and entering the :ref:`sign-level information<sign_level_info>` and coding the :ref:`sign type module<sign_type>`, code the **movement module(s)** for the sign first before moving on to other ``sign modules``. The movement information is used by the program to generate the appropriate number of :ref:`x-slots<x_slot>` for the sign if ``auto-generation`` **(auto-generation and autofilling)** is enabled. Whether x-slots are created automatically or manually by the user, they are the timing basis that the ``sign modules`` build upon and so they must be specified first. (See the :ref:`global_settings` for how to change the program's default auto-generation behaviour.)

.. _movement_type_entry:

1. Movement type
`````````````````

Select the movement type for the current module.

.. note::
    There is often more flexibility as to whether different components of movement can be counted as separate modules or part of the same one. At minimum, for signs with multiple (simultaneous and/or sequential) movements, give each movement type its own module. That is, code any :ref:`joint_specific_movement` separately from any movement with :ref:`perceptual_shape`, as these are mutually exclusive by definition. You can then adjust the timing of each module with respect to the others in the ``x-slot visualization window``.
    
    Signs with complex movements like `MILK <https://asl-lex.org/visualization/?sign=milk_2>`_ and `EVERY_YEAR <https://www.signingsavvy.com/sign/EVERY+YEAR>`_ require at least two movement modules, including a perceptual shape and a joint-specific movement.
    
    Keep in mind that the number of modules needed to describe a movement may depend on your choices in terms of its :ref:`movement characteristics<movement_chars>`, and that you can add more detail on the joint articulations for any type of movement in the :ref:`joint activity<joint_activity_entry>` section.
    
.. comment::
    Some parts of this note may end up in the modularity page with a link here to see more, but I'm not sure yet where the cutoff should be.

.. _perceptual_shape_entry:

I. Perceptual shape
===================

Code the specifications for a movement with :ref:`perceptual_shape`. This could be the only movement in a sign, as in `BICYCLE <https://asl-lex.org/visualization/?sign=bicycle>`_, or a single component of a more complex sign, like the vertical motions in `MILK <https://asl-lex.org/visualization/?sign=milk_2>`_.

.. _shape_entry:

a) Shape
~~~~~~~~

Select the shape of the movement.

.. note::
    Give at least one example for each preset shape option.

Only one shape option can be specified per module. When you want to indicate multiple perceptual shapes in one sign, as you could for `SIGN_LANGUAGE <https://asl-lex.org/visualization/?sign=sign_language>`_, one way to code the full set of movements is to add as many modules as there are distinct shapes. The modules will be assigned to the ``x-slot visualization`` in the order in which they're coded, so it's important to start with the first movement in the sequence and continue in order. Another way to capture the full movement is to create a new shape label. This may be a useful option for shapes that reappear in many signs.

.. note::
    For the special case of shape combinations where multiple straight movements are signed in sequence, as in `CANCEL <https://www.handspeak.com/word/search/index.php?id=312>`_ or `SEMESTER <https://www.handspeak.com/word/search/index.php?id=4065>`_, you have the option to select that this movement 'interacts with a subsequent straight movement.' This will mean that, once you are finished with the current module, the program will create another movement module automatically for the next movement in the sequence with a 'straight' shape already specified.

.. _axis_direction_entry:

b) Axis direction
~~~~~~~~~~~~~~~~~

Select an axis (or a combination of axes) that describe the direction of movement. 

**(Our convention: for circular motions, select the direction that extends from the beginning of the movement toward the midpoint of the first cycle.)**

.. note::
    A combination of axes can be interpreted as ... **(not intended to be sequential)**

See a description of ``the signing space and the body`` for a visual representation of these options. **(Link to the file on planes/symmetry/anatomical position, etc)**. See the :ref:`global_settings` page for how to switch between ``relative directions`` and ``absolute positions``.

.. note::
    Insert examples here for a few signs. Include some options of how to deal with circles and loops, e.g. a pair of circles that have the *same* plane and clockwise directionality but *different* axis directions.

.. _plane_entry:

c) Plane
~~~~~~~~

Code the plane (or combination of planes) that fully encompasses the range of movement described in the current module. For each selected plane, you can also choose a circular directionality if desired.

.. note::
    A combination of planes can be interpreted as ... **(not intended to be sequential)**

This section is automatically specified by the program as 'not relevant' when the module includes a 'straight' perceptual shape, or when the axis direction is coded as 'not relevant' by the user.

See a description of ``the signing space and the body`` for a visual representation of these options. **(Link to the file on planes/symmetry/anatomical position, etc)**. See the :ref:`global_settings` page to find the default clockwise directionality for each plane, and how to change these.

.. note::
    Insert a few sign examples for different shapes

.. _joint_specific_movement_entry:

II. Joint-specific movements
============================

Code the specifications for a :ref:`joint_specific_movement`. This may be the only movement in a sign, as in `APPLE <https://asl-lex.org/visualization/?sign=apple>`_, or a single component of a more complex sign, like the closing and opening motions in `MILK <https://asl-lex.org/visualization/?sign=milk_2>`_.

...

.. _handshape_change_entry:

III. Handshape change
=====================

Select whether the sign uses a :ref:`handshape_change`. This can apply for fingerspellings, compound signs (as in `DESERT <https://asl-lex.org/visualization/?sign=desert>`_), initialized signs (as in `HIGH_SCHOOL <https://asl-lex.org/visualization/?sign=high_school>`_), or any other cases that involve a change in handshape during the production of the sign.

As with the other movement types, a module with this specification cannot be combined with the selections for a :ref:`joint_specific_movement` or a movement with :ref:`perceptual_shape`. To code any information about other movements in the sign, add additional movement module(s) with the appropriate movement type(s). You can then adjust the timing of each module with respect to the others in the ``x-slot visualization window``.

.. comment::
    Should I give examples here for lexicalized fingerspellings on a (circular) path? e.g. (I think?) the handspeak example of STYLE.

.. _joint_activity_entry:

2. Joint activity
``````````````````

Use the **joint activity** section to add more fine-grained detail about any joint movements related to the current module. If the module describes a :ref:`joint_specific_movement`, then the program will ``autofill`` **(auto-generation and autofilling)** the joint movements that are predictable from the selections made earlier within the :ref:`movement type section<joint_specific_movement_entry>`. See the :ref:`global_settings` for how to change the program's default autofill behaviour.

**(A note on user flexibility: this section can encode the phonetics of proximalization/distalization, differences in sizes of the same perceptual shape based on the joints involved, etc.)**

.. _movement_chars:

3. Movement characteristics
```````````````````````````

...

.. comment::
    The places where I intend to add a link to a currently non-existent docs section/page are marked as a code block temporarily
    For the moment, this includes the auto-generation page, the page on x-slots, and the sign summary window
    
.. todo::
    shape examples
    axis direction comparison
    combinations of planes and axes
        examples for these
    finish writing up the joint activity section
    
.. _movement:

***************
Movement Module
***************

This :ref:`module` is used to code the movement components of a sign.

.. note::
    If ``x-slots`` **(x-slot page)** and ``auto-generation`` **(auto-generation and autofilling)** are both enabled, then code the **movement module(s)** for the sign immediately after entering the :ref:`sign_level_info` and coding the :ref:`sign_type`. The movement information is used by the program to generate the appropriate number of x-slots for the sign, and then you'll be able to move on to other :ref:`sign modules<modularity>`.

    If ``x-slots`` **(x-slot page)** are enabled but they are created manually by the user, then they must be generated first before adding any modules to the sign.
    
    See :ref:`global_settings` for more about the default auto-generation behaviour, and how to change these options.

.. _movement_type_entry:

1. Movement type
`````````````````

Select the **movement type** for the current module.

.. note::
    There is often more flexibility as to whether different components of movement can be counted as separate modules or part of the same one. See the page on :ref:`modularity` for more in-depth discussion of this idea.
    
    At minimum, for signs with multiple (simultaneous and/or sequential) movements, give each movement type its own module. That is, code any :ref:`joint_specific_movement` separately from any movement with :ref:`perceptual_shape`, as these are mutually exclusive by definition. You can then adjust the timing of each module with respect to the others in the ``x-slot visualization window`` **(?)**.
    
    Signs with complex movements like `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_ and `EVERY_YEAR <https://www.signingsavvy.com/sign/EVERY+YEAR>`_ require at least two movement modules, including a perceptual shape and a joint-specific movement.
    
    Keep in mind that the number of :ref:`modules<module>` needed to describe a movement may depend on your choices in terms of :ref:`movement characteristics<movement_chars>`, and that you can add more detail on the joint articulations for any type of movement in the :ref:`joint activity<joint_activity_entry>` options of the module.
    
.. _perceptual_shape_entry:

I. Perceptual shape
===================

Code the specifications for a movement with :ref:`perceptual_shape`. This could be the only movement in a sign, as in `NORTH <https://asl-lex.org/visualization/?sign=north>`_, or a single component of a more complex sign, like the path movement in `FINGERSPELL <https://asl-lex.org/visualization/?sign=fingerspell>`_.

.. _shape_entry:

a) Shape
~~~~~~~~

Select the shape of the movement.

.. note::
    Give at least one example for each preset shape option.

Only one shape option can be specified per module. When you want to indicate multiple perceptual shapes in one sign, as you could for `SIGN_LANGUAGE <https://asl-lex.org/visualization/?sign=sign_language>`_, one way to code the full set of movements is to add as many modules as there are distinct shapes. The modules will be assigned to the ``x-slot visualization`` **(?)** in the order in which they're coded, so it's important to start with the first movement in the sequence and continue in order. Another way to capture the full movement is to create a new shape label. This may be a useful option for shapes that reappear in many signs.

.. note::
    For the special case of shape combinations where multiple straight movements are signed in sequence, as in `CANCEL <https://www.handspeak.com/word/search/index.php?id=312>`_ or `SEMESTER <https://www.handspeak.com/word/search/index.php?id=4065>`_, you have the option to select that this movement 'interacts with a subsequent straight movement.' Selecting this means that once you are finished with the current module, the program will create another movement module automatically for the next movement in the sequence with a 'straight' shape already specified.
    
    (In addition to being a little more expedient than adding the extra module(s) yourself, this method has the benefit of unifying all signs with multiple straight movements in an accessible way for searching and analysis later on.)

.. _axis_direction_entry:

b) Axis direction
~~~~~~~~~~~~~~~~~

Select an **axis direction** (or a combination of axis directions) that describe the direction of movement. 

See the :ref:`global_settings` page for how to switch between relative ipsi/contra and absolute left/right directions on the horizontal axis. See a description of :ref:`signing_space` for a visual representation of these options.

.. note::
    A combination of axes can be interpreted as ... **(not intended to be sequential in one module)**

It may seem redundant to choose an axis direction as well as a plane and clockwise direction for circular movements, but it is a useful feature for describing the timing distinction in pairs like `WHEELCHAIR <https://asl-lex.org/visualization/?sign=wheelchair>`_ and `BICYCLE <https://asl-lex.org/visualization/?sign=bicycle>`_. Notice that the plane and clockwise directionality are the same in both of these cases, but the location of each hand relative to the other is the same at every point in the sign for WHEELCHAIR while the relative locations of each hand are different for BICYCLE. See the section on :ref:`movement timing relation<signtype_movement_timing_relation>` for more discussion of this idea.

There are many possible ways to specify an axis direction for a circular movement. You could choose the direction of the end of the first half of the circle relative to the beginning point, or the first initial direction of motion at the starting point, or anything else that you can think of. The most important thing is to maintain a consistent standard for selecting direction for circular movements.

For example, if you were to choose to code the direction as the midpoint of the circle relative to the beginning, then codings for `WHEELCHAIR <https://asl-lex.org/visualization/?sign=wheelchair>`_ and `BICYCLE <https://asl-lex.org/visualization/?sign=bicycle>`_ could look like this:

**add images for this comparison**

Similarly, **SAMPLE SIGN (arc)** may look like ...

.. _plane_entry:

c) Plane
~~~~~~~~

Select the **plane** (or combination of planes) that fully encompasses the range of movement described in the current module. This section is automatically specified by the program as 'not relevant' when the module includes a 'straight' perceptual shape, or when the axis direction is coded as 'not relevant' by the user.

For each selected plane, you can also choose a circular directionality if desired. See the :ref:`global_settings` page for how to switch between relative ipsi/contra and absolute (counter-)clockwise directions for any circular shapes that involve the horizontal axis, as well as a definition of the default clockwise direction for each plane. See :ref:`signing_space` for a visual representation of these options.

.. note::
    A combination of planes can be interpreted as ... **(not intended to be sequential in one module)**

.. note::
    Insert a few sign examples for different shapes

.. _joint_specific_movement_entry:

II. Joint-specific movements
============================

Code the specifications for a :ref:`joint_specific_movement`. This may be the only movement in a sign, as in `APPLE <https://asl-lex.org/visualization/?sign=apple>`_, or a single component of a more complex sign, like the closing and opening motions in `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_.

Each joint-specific movement has two sub-options, which correspond to which direction the movement starts with. You can skip selecting the broader option
and go directly to selecting the sub-option; the broader option will show up as being selected. Similarly, the system does not require that you specify a sub-option, if for any reason it is preferable to leave the starting direction unspecified or if it is unknown. **[AP]: is this way too in-depth? Also is this accurate?** The appropriate joint activity will be autofilled in the :ref:`joint activity<joint_activity_entry>` section once you have selected a sub-option for direction. **should the description of what exactly gets autofilled be specified for each of these?** 

The joint-specific movement options are as follows: 

**Nodding/Un-nodding** 
- "Nodding" should be selected if the movement begins with a flexion of the wrist, such as `_CORN <>`. This is an example of a sign that contains both nodding and un-nodding, however this option should also be selected for signs where there is only a single nodding motion, such as ABLE **link**, or signs where there is a repeated, unidirectional nodding, such as YES **links**. 
- "Un-nodding" should be selected if the moevement begins with an extension of the wrist, or if it is the only movement involved, for example GIVE_UP **links**

**Pivoting**
- "Radial > ulnar" should be selected if the movement begins with a radial deviation, or if it is the only direction involved. 
- "Ulnar > radial" should be selected if the movement begins with an ulnar deviation, as in COOKIE **links**, or if it is the only direction involved.    


**Twisting**
- "Pronation" should be selected if the movement begins with pronation, or if it is the only direction involved, such as the subordinate hand of DIE **links**. Selecting this will autofill 
- "Supination" should be selected if the movement begins with supination, or if it is the only direction involved, such as CLAUSE and the dominant hand of DIE **links** 

**[proximal] - meaning?**

**Closing/Opening**
"Closing" should be selected if the sign begins with flexion of all joints of the selected finger(s), such as MILK_2 **link**, or if this is the only direction involved. 
"Opening" should be selected if the sign begins with extension of all joints of the selected finger(s), or if this is the only direction involved, such as BOWTIE **link**.


.. todo::
    Pinching/unpinching
    Pinching (Morgan 2017) [--> autofills to adduction of thumb base joint] e.g., TURTLE
    Unpinching [--> autofills to abduction of thumb base joint]
    Flattening/Straightening
    Flattening [--> autofills to flexion of [selected finger base joints]] e.g., HORSE
    Straightening [--> autofills to extension of [selected finger base joints]]




.. _handshape_change_entry:

III. Handshape change
=====================

Select whether the sign uses a :ref:`handshape_change`. This can apply for fingerspellings, compound signs (as in `DESERT <https://asl-lex.org/visualization/?sign=desert>`_), initialized signs (as in `HIGH_SCHOOL <https://asl-lex.org/visualization/?sign=high_school>`_), or any other cases that involve a change in handshape during the production of the sign.

.. note::
    As with the other movement types, a module with this specification cannot be combined with the selections for a :ref:`joint_specific_movement` or a movement with :ref:`perceptual_shape`. To code any information about other movements in the sign, add additional movement module(s) with the appropriate movement type(s). You can then adjust the timing of each module with respect to the others in the ``x-slot visualization window`` **(?)**.

    For instance, you can choose whether or not to indicate that a fingerspelling is signed along a path ...

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

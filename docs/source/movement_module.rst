.. comment::
    The places where I intend to add a link to a currently non-existent docs section/page are marked as a code block temporarily
    For the moment, this only includes the auto-generation page
    
.. todo::
    add axis direction sign examples
        finish axis direction for circular shapes
    add plane sign examples
    handshape change not completed
    joint activity description not completed
    movement characteristics not yet started
    at least one sample coding of the full set of movement modules for a sign
    
.. _movement:

***************
Movement Module
***************

This :ref:`module` is used to code the movement components of a sign. For more discussion on the use of modules in SLP-AA to encode information about signs, see :ref:`modularity`.

.. note::
    Depending on your choices of how to interact with the program, the step to start adding modules to a sign may come at different points in the coding process.
    
    If :ref:`x-slots<x_slot>` and ``auto-generation`` **(auto-generation and autofilling documentations)** are both enabled, then code the **movement module(s)** for the sign immediately after entering the :ref:`sign_level_info` and coding the :ref:`sign_type_module`. The movement information is used by the program to generate the appropriate number of x-slots for the sign, and then you'll be able to move on to other sign modules.

    If :ref:`x-slots<x_slot>` are enabled but ``auto-generation`` **(auto-generation and autofilling documentations)** is not, then you must add the appropriate number of x-slots first before adding any modules at all to the sign.

    See :ref:`global_settings` for more about the program's default behaviour, and how to change these options.

.. _movement_type_entry:

1. Movement type
`````````````````

Select the **movement type** for the current module.

.. note::
    There is often some flexibility as to whether different components of movement can be counted as separate modules or part of the same one. See :ref:`modularity` for more in-depth discussion of this idea.
    
    At minimum, for signs with multiple (simultaneous and/or sequential) movements, give each movement type its own module. That is, code any :ref:`joint_specific_movement` separately from any movement with :ref:`perceptual_shape`, as these are mutually exclusive by definition. You can then adjust the timing of each module with respect to the others in the :ref:`x-slot visualization window<sign_summary>`.
    
    This means that signs with complex movements like `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_ and `EVERY_YEAR <https://www.signingsavvy.com/sign/EVERY+YEAR>`_ require at least two movement modules, including a perceptual shape and a joint-specific movement.
    
    Keep in mind that the number of modules needed to describe a movement may depend on your choices in terms of :ref:`movement characteristics<movement_chars>`, and that you can add more detail on the joint articulations for any type of movement in the :ref:`joint activity<joint_activity_entry>` options of the module.

Movement type options include:

* :ref:`perceptual_shape`
* :ref:`joint_specific_movement`
* :ref:`handshape_change`

.. _perceptual_shape_entry:

I. Perceptual shape
===================

Code the specifications for a movement with :ref:`perceptual_shape`. This could be the only movement in a sign, as in `NORTH <https://asl-lex.org/visualization/?sign=north>`_, or a single component of a more complex sign, like the path movements in `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_.

.. _shape_entry:

a) Shape
~~~~~~~~

Select the shape of the movement.

Only one shape option can be specified per module. When you want to indicate multiple perceptual shapes in one sign, as you could for `SIGN_LANGUAGE <https://asl-lex.org/visualization/?sign=sign_language>`_, one way to code the full set of movements is to add as many modules as there are distinct shapes. The timing of each movement with respect to the others can then be seen in the :ref:`x-slot visualization window<sign_summary>`. The default list of perceptual shapes can also be edited by the user, so another way to capture the full movement of a new shape is to create a shape label. This may be a useful option for shapes that reappear in many signs.

For the special case of shape combinations where multiple straight movements are signed in a connected sequence, as in `CANCEL <https://www.handspeak.com/word/search/index.php?id=312>`_ or `SEMESTER <https://www.handspeak.com/word/search/index.php?id=4065>`_, you have the option to select that this movement 'interacts with a subsequent straight movement.' Selecting this means that once you are finished with the current module, the program will create another movement module automatically for the next movement in the sequence with a 'straight' shape already specified. **Note: What does this option mean specifically for searching/analysis?**

The default list of shape options is:

* **Straight**  

  * **Interacts with a subsequent straight movement** 
    
    * **Movement contours cross**, as in `CANCEL <https://www.handspeak.com/word/search/index.php?id=312>`_ or `HOSPITAL <https://asl-lex.org/visualization/?sign=hospital>`_  
    * **Subsequent movement starts at end of first**, as in `SEMESTER <https://www.handspeak.com/word/search/index.php?id=4065>`_ or `TRIANGLE <https://asl-lex.org/visualization/?sign=triangle>`_  
    * **Subsequent movement starts in same location as first**, as in (possibly) the second set of movements of `DAISY <https://www.handspeak.com/word/index.php?id=5824>`_  
    * **Subsequent movement ends in same location as first**, as in (possibly) the first set of movements of `SNOWSTORM <https://www.youtube.com/watch?v=KQLrgPdHRlQ&list=TLGGDt2--iXU7qQxNzAxMjAyMg>`_ **Note: Is this a stable link? Would it be possible to find something else?**  
        
  * **Doesn't interact with a subsequent straight movement**, as in `NORTH <https://asl-lex.org/visualization/?sign=north>`_ or `SCROLL_DOWN <https://asl-lex.org/visualization/?sign=scroll_down>`_
    
* **Arc**, as in `FOLD <https://asl-lex.org/visualization/?sign=fold>`_ or `SINCE <https://asl-lex.org/visualization/?sign=since>`_
* **Circle**, as in `DECORATE_2 <https://asl-lex.org/visualization/?sign=decorate_2>`_ or `REASON <https://www.handspeak.com/word/index.php?id=3974>`_
* **Zigzag**, as in `DRAW <https://asl-lex.org/visualization/?sign=draw>`_ or `WHALE <https://asl-lex.org/visualization/?sign=whale>`_
* **Loop (traveling circles)**, as in `ERASE_5 <https://asl-lex.org/visualization/?sign=erase_5>`_ or `CLOUD_1 <https://asl-lex.org/visualization/?sign=cloud_1>`_
* **None of these**

.. _axis_direction_entry:

b) Axis direction
~~~~~~~~~~~~~~~~~

Select an **axis direction** (or a combination of axis directions) that describe the direction of movement. 

Keep in mind that a single module is meant to convey only one direction of movement, so selecting a combination of axes should be interpreted as a diagonal or angled movement with all of the selected directions applying simultaneously. See the note on :ref:`combinations of axes<axes_entry>` for a visual description of how this works. For sequential movements in different directions, you should create multiple movement modules to be able to refer to the :ref:`x-slot visualization window<sign_summary>` for the temporal order of the movement sequence.

At most one direction can be selected for each axis, so that a total maximum of three directions can apply at once.

* Vertical axis:

    * **Up**
    * **Down**

* Mid-saggital axis:

    * **Distal**
    * **Proximal**
    
* Horizontal axis:

    * **Ipsilateral** (by default)
    * **Contralateral** (by default)
    
        * OR
    
    * **Left**
    * **Right**

* **Not relevant**

See the :ref:`global_settings` page for how to switch between relative ipsi/contra and absolute left/right directions on the horizontal axis. See :ref:`signing_space_page` for a visual representation of each of these options, and more information about the horizontal axis in particular.

.. note::

    **Axis direction for circular shapes**

    Choosing an axis direction is straightforward for straight shapes, but there is flexibility in choosing a direction for circular shapes. You could choose the direction of the end of the first half of the circle relative to the beginning point, or the first initial direction of motion at the starting point, and so on. The most important thing is to maintain a consistent standard for coding direction.

    It may seem redundant to choose an axis direction as well as a plane and clockwise direction for circular movements, but it is a useful feature for describing the timing distinction in pairs like `WHEELCHAIR <https://asl-lex.org/visualization/?sign=wheelchair>`_ and `BICYCLE <https://asl-lex.org/visualization/?sign=bicycle>`_. **Notice that the plane and clockwise directionality are the same in both of these cases, but the location of each hand relative to the other is the same at every point in the sign for WHEELCHAIR while the relative locations of each hand are different for BICYCLE. (Work on this wording)** See the section on :ref:`movement timing relations<signtype_movement_timing_relation>` for more discussion of this idea.

    For example, if you were to choose to code the direction as the midpoint of the circle relative to the beginning, then codings for `WHEELCHAIR <https://asl-lex.org/visualization/?sign=wheelchair>`_ and `BICYCLE <https://asl-lex.org/visualization/?sign=bicycle>`_ could look like this: **Note: I need a pair of signs with two hands moving in the same circular direction in the mid-saggital plane, where one sign has the hands moving in sync and the other has them out of sync. Is this the best pair for this? Can I find something slightly more similar?**

    **add images for this comparison**

    Similarly, **SAMPLE SIGN (arc)** may look like ...

.. _plane_entry:

c) Plane
~~~~~~~~

Select the **plane** (or combination of planes) that fully encompasses the range of movement described in the current module. For each selected plane, you can also choose a circular directionality if desired.

This section is automatically specified by the program as 'not relevant' when the module includes a 'straight' perceptual shape, or when the axis direction is coded as 'not relevant' by the user. 

Keep in mind that a single module is meant to convey only one direction of movement, so selecting a combination of planes should be interpreted as a diagonal or angled movement with all of the selected planes (and circular directions) applying simultaneously. See the notes on :ref:`combinations of planes<planes_entry>` and :ref:`angled circular directions<circular_directions>` for a visual description of how this works. For sequential movements in different directions, you should create multiple movement modules and assign them to the :ref:`x-slot visualization<sign_summary>` to record their temporal order.

At most one circular direction can be selected for each plane, so that a total maximum of three directions can apply at once. See :ref:`global_settings` for a definition of the default clockwise direction and what is meant by the 'top' of the circle for each plane.

* **Mid-saggital plane**

    * **Clockwise**
    * **Counter-clockwise**

* **Horizontal plane**

    * **Ipsilateral from the top of the circle** (by default)
    * **Contralateral from the top of the circle** (by default)
    
        * OR
    
    * **Clockwise**
    * **Counter-clockwise**

* **Vertical plane**

    * **Ipsilateral from the top of the circle** (by default)
    * **Contralateral from the top of the circle** (by default)
    
        * OR
    
    * **Clockwise**
    * **Counter-clockwise**

* **Not relevant**

See the :ref:`global_settings` page for how to switch between relative ipsi/contra and absolute left/right (counter-)clockwise directions for any circular shapes that involve the vertical or horizontal plane. See :ref:`signing_space_page` for a visual representation of all of these options, and for more information on the horizontal axis in particular.

.. _joint_specific_movement_entry:

II. Joint-specific movements
============================

Code the specifications for a :ref:`joint_specific_movement`. This may be the only movement in a sign, as in `APPLE <https://asl-lex.org/visualization/?sign=apple>`_, or a single component of a more complex sign, like the closing and opening motions in `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_.

Each joint-specific movement has two sub-options, which correspond to which direction the movement starts with. You can skip selecting the broader option
and go directly to selecting the sub-option; the broader option will show up as being selected. Similarly, the system does not require that you specify a sub-option, if for any reason it is preferable to leave the starting direction unspecified or if it is unknown. **[AP]: is this way too in-depth? Also is this accurate?** The appropriate joint activity will be autofilled in the :ref:`joint activity<joint_activity_entry>` section once you have selected a sub-option for direction. **should the description of what exactly gets autofilled be specified for each of these?** 

The joint-specific movement options are as follows: 

**Nodding/Un-nodding** 
- "Nodding" should be selected if the movement begins with a flexion of the wrist, such as `_CORN <>`. This is an example of a sign that contains both nodding and un-nodding, however this option should also be selected for signs where there is only a single nodding motion, such as ABLE **link**, or signs where there is a repeated, unidirectional nodding, such as YES **links**. 
- "Un-nodding" should be selected if the movement begins with an extension of the wrist, or if it is the only movement involved, for example GIVE_UP **links**

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
    As with the other movement types, a module with this specification cannot be combined with the selections for a :ref:`joint_specific_movement` or a movement with :ref:`perceptual_shape`. To code any information about other movements in the sign, add additional movement module(s) with the appropriate movement type(s). You can then adjust the timing of each module with respect to the others in the :ref:`x-slot visualization window<sign_summary>`.

    For instance, you can choose whether or not to indicate that a fingerspelling is signed along a path ... 
    
    **(Note: add an example of a quick handshape change in the middle of a sign? I seem to remember a handful of these, maybe for compounds)**

.. comment::
    Should I give examples here for lexicalized fingerspellings on a (circular) path? e.g. (I think?) the handspeak example of STYLE.

.. _joint_activity_entry:

2. Joint activity
``````````````````

Use the **joint activity** section to add more fine-grained detail about any joint movements related to the current module. If the module describes a :ref:`joint_specific_movement`, then the program will ``autofill`` **(auto-generation and autofilling documentations)** the joint movements that are predictable from the selections made earlier within the :ref:`movement type section<joint_specific_movement_entry>`. See the :ref:`global_settings` for how to change the program's default autofill behaviour.

**(A note on user flexibility: this section can encode the phonetics of proximalization/distalization, differences in sizes of the same perceptual shape based on the joints involved, etc.)**

.. _movement_chars:

3. Movement characteristics
```````````````````````````

...

.. todo::
    check against all of the places where docs information is stored
        -guidelines
        -system overview
        -to mention in docs
    joint activity description not completed
    movement characteristics not yet started
    at least one sample coding of the full set of movement modules for a sign (or is this covered in the other project materials?)
    fix references
    update / delete refs to “transcription process”
    
.. _movement:

***************
Movement Module
***************

This :ref:`module` is used to code the movement components of a sign. For more discussion on the use of modules in SLP-AA to encode information about signs, see :ref:`modularity`.

.. note::
    Depending on your choices of how to interact with the program, the step to start adding modules to a sign may come at different points in the coding process.
    
    If :ref:`x-slots<x_slot>` and :ref:`auto-generation<auto_gen>` are both enabled, then code the **movement module(s)** for the sign immediately after entering the :ref:`sign_level_info` and coding the :ref:`sign_type_module`. The movement information is used by the program to generate the appropriate number of x-slots for the sign, and then you'll be able to move on to other sign modules.

    If :ref:`x-slots<x_slot>` are enabled but :ref:`auto-generation<auto_gen>` is not, then you must add the appropriate number of x-slots first before adding any modules at all to the sign.

    See :ref:`global_settings` for more about the program's default behaviour, and how to change these options.

.. _movement_type_entry:

1. Movement type
`````````````````

Select the **movement type** for the current module. The three movement types are mutually exclusive within an instance of a module; that is, a single instance of the module can be specified for only one of these three types of movement. 

Movement type options include:

* :ref:`perceptual_shape`, as in `NORTH <https://asl-lex.org/visualization/?sign=north>`_
* :ref:`joint_specific_movement`, as in `APPLE <https://asl-lex.org/visualization/?sign=apple>`_
* :ref:`handshape_change`, as in `HIGH_SCHOOL <https://asl-lex.org/visualization/?sign=high_school>`_

.. note::
    There is often some flexibility as to whether different components of movement can be counted as separate modules or part of the same one. See :ref:`modularity` for more in-depth discussion of this idea.
    
    At a minimum, for signs with multiple (simultaneous and/or sequential) movements, give each movement type its own module. That is, code any :ref:`joint_specific_movement` separately from any movement with :ref:`perceptual_shape` as well as any :ref:`handshape_change`, as these are mutually exclusive by definition. You can then adjust the timing of each module with respect to the others in the :ref:`x-slot visualization window<sign_summary>`.
    
    This means that signs with complex movements like `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_ and `EVERY_YEAR <https://www.signingsavvy.com/sign/EVERY+YEAR>`_ require at least two movement modules, including a perceptual shape and a joint-specific movement.
    
    The number of modules needed to describe a movement may also depend on your choices in terms of :ref:`movement characteristics<movement_chars>` (e.g., how repetitions are coded). 

Note that in SLP-AA, we do not require users to classify movements into the traditional categories of ‘path’ / ‘major’ / ‘primary’ vs. ‘local’ / ‘minor’ / ‘secondary’ movements. Instead, we have classifications for 1) “perceptual shape movements” (e.g., straight, circle, arc), “joint-specific movements” (e.g., twisting, closing), and “handshape changes” (e.g., fingerspelling). As Napoli et al. (2011: 19) point out, “the actual distinction between primary and secondary movement is not uncontroversial and is far from simple.” For example, while wrist movements are typically considered local movements according to articulatory definitions of path and local movement categories (e.g., Brentari, 1998), some of them have been categorized as path movements (van der Kooij, 2002: 229; Sehyr et al., 2021: 269). Furthermore, forcing the choice between path and local movements at the level of phonetic transcription could mask empirical phenomena such as proximalization and distalization (Brentari, 1998), in which both path and local movements can be articulated by non-canonical joints. 

In response to these issues, our system allows any movement in which the hand or arm draws a perceptual shape in space to be classified as perceptual movement, with optional manual specifications of the exact (combination of) joints executing the movement under a separate “joint activity” section. For example, the sign `NORTH <https://asl-lex.org/visualization/?sign=north>`_ is canonically signed as a straight perceptual movement that is articulated at the shoulder. A distalized version of this sign might be produced with an "un-nodding" wrist movement. In such a case, one could code this either as a joint-specific wrist-nod movement OR one could preserve the 'phonological intention' of the perceptual straight movement and simply add the fact that it is articulated with wrist flexion in the :ref:`joint activity<joint_activity_entry>` section.

Traditional local movements (relating to particular joints) defined in the literature are listed under the joint-specific movement section, with the associated joint activities optionally auto-filled (e.g., the joint-specific movement of “closing” can auto-fill to flexion of finger joints in the “joint activity” section). 

Note that after the movement type selections have been made, there are separate additional sections for coding the :ref:`joint activity<joint_activity_entry>` and the :ref:`movement characteristics<movement_chars>`. 

.. _perceptual_shape_entry:

I. Perceptual shape
===================

Make your selections from this section if you are coding a movement with :ref:`perceptual_shape`. This could be the only movement in a sign, as in `NORTH <https://asl-lex.org/visualization/?sign=north>`_, or a single component of a more complex sign, like the path movements in `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_.

.. note::
    As with the other movement types, a module with this specification cannot be combined with the selections for a :ref:`handshape_change` or a movement with :ref:`joint_specific_movement`. To code any information about other movements in the sign, add additional movement module(s) with the appropriate movement type(s). You can then adjust the timing of each module with respect to the others in the :ref:`x-slot visualization window<sign_summary>`. For example, to code the sign `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_, one would need two separate instances of the movement module, one for the straight (perceptual shape) movement of the hands and one for the joint-specific opening and closing movements.

.. _shape_entry:

a) Shape
~~~~~~~~

Select the shape of the movement.

Only one shape option can be specified per module. When you want to indicate multiple perceptual shapes in one sign, as you could for `SIGN_LANGUAGE <https://asl-lex.org/visualization/?sign=sign_language>`_, one way to code the full set of movements is to add as many modules as there are distinct shapes. The timing of each movement with respect to the others can then be seen in the :ref:`x-slot visualization window<sign_summary>`. The default list of perceptual shapes can also be ``edited by the user`` **[ADD REF TO EDITING INFO]**, so another way to capture the full movement of a new shape is to create a shape label. This may be a useful option for shapes that reappear in many signs.

For the special case of shape combinations where multiple straight movements are signed in a connected sequence, as in `CANCEL <https://www.handspeak.com/word/search/index.php?id=312>`_ or `SEMESTER <https://www.handspeak.com/word/search/index.php?id=4065>`_, you have the option to select whether any given straight shape **interacts with a subsequent straight movement**, and then to code each of the straight lines using a separate module. Some signs may include multiple straight shapes that do not form a connected sequence, as in `ROOM <https://asl-lex.org/visualization/?sign=room>`_, in which case you can indicate that the first straight movement **does not interact with a subsequent straight movement**. This latter option is also used for signs that have only a single straight movement, such as `NORTH <https://asl-lex.org/visualization/?sign=north>`_, and for the final straight movement in a connected sequence. 

The default list of shape options is:

* **Straight**  

  * **Interacts with a subsequent straight movement** 
    
    * **Movement contours cross**, for cases of "X"-type shapes, as in `CANCEL <https://www.handspeak.com/word/search/index.php?id=312>`_ or `HOSPITAL <https://asl-lex.org/visualization/?sign=hospital>`_  
    * **Subsequent movement starts at end of first**, for cases of continuous / connected "V"-, "Z"-, or "7"-type shapes, as in `SEMESTER <https://www.handspeak.com/word/search/index.php?id=4065>`_ or `TRIANGLE <https://asl-lex.org/visualization/?sign=triangle>`_  (Note that there is also a separate 'zigzag' movement option, so care should be taken in terms of deciding when a movement is interpreted as a series of separate, connected straight movements vs. a single multiple-component movement.)
    * **Subsequent movement starts in same location as first**, as in the second set of movements of `DAISY <https://www.handspeak.com/word/index.php?id=5824>`_  
    * **Subsequent movement ends in same location as first**, as in the first set of movements of `SNOWSTORM <https://youtu.be/KQLrgPdHRlQ?t=4>`_   
        
  * **Doesn't interact with a subsequent straight movement**, as in `NORTH <https://asl-lex.org/visualization/?sign=north>`_ or `SCROLL_DOWN <https://asl-lex.org/visualization/?sign=scroll_down>`_ (Note that this option would also be used when coding the *final* movement of a series of interacting straight lines.)
    
* **Arc**, as in `FOLD <https://asl-lex.org/visualization/?sign=fold>`_ or `SINCE <https://asl-lex.org/visualization/?sign=since>`_
* **Circle**, as in `DECORATE_2 <https://asl-lex.org/visualization/?sign=decorate_2>`_ or `REASON <https://www.handspeak.com/word/index.php?id=3974>`_
* **Zigzag**, as in `DRAW <https://asl-lex.org/visualization/?sign=draw>`_ or `WHALE <https://asl-lex.org/visualization/?sign=whale>`_
* **Loop (traveling circles)**, as in `ERASE_5 <https://asl-lex.org/visualization/?sign=erase_5>`_ or `CLOUD_1 <https://asl-lex.org/visualization/?sign=cloud_1>`_
* **None of these**

.. _axis_direction_entry:

b) Axis direction
~~~~~~~~~~~~~~~~~

Select an **axis direction** (or a combination of axis directions) that describe the direction of movement. It is also possible to select an axis without a direction, which may be useful for coding an underspecified sign.

Keep in mind that a single module is meant to convey only one direction of movement, so selecting a combination of axes should be interpreted as a diagonal or angled movement with all of the selected directions applying simultaneously. See the note on :ref:`combinations of axes<combinations_axes>` for a visual description of how this works. For sequential movements along different axes, you should create multiple movement modules and use the :ref:`x-slot visualization window<sign_summary>` to assign a temporal order to the movement sequence.

At most one direction can be selected for each axis, so that a total maximum of three directions can apply at once within a module. For a movement that travels back and forth along both directions for a given axis, as in `WINDSHIELD_WIPERS <https://www.handspeak.com/word/index.php?id=3918>`_, you can either create a new module for each successive change in direction, or you can select that the movement is 'bidirectional' in the :ref:`movement characteristics<movement_chars>` options. In the case of bidirectional movements, you should establish a convention for selecting axis direction, such as always selecting the first direction of motion.

* **Vertical axis**

    * **Up**, as in `UMBRELLA <https://asl-lex.org/visualization/?sign=umbrella>`_ or `NORTH <https://asl-lex.org/visualization/?sign=north>`_
    * **Down**, as in `LOSE_GAME <https://asl-lex.org/visualization/?sign=lose_game>`_ or `DRAW <https://asl-lex.org/visualization/?sign=draw>`_

* **Mid-sagittal axis**

    * **Distal**, as in `NEXT <https://asl-lex.org/visualization/?sign=next>`_ or `SINCE <https://asl-lex.org/visualization/?sign=since>`_
    * **Proximal**, as in `BEFORE <https://asl-lex.org/visualization/?sign=before>`_ 
    
* **Horizontal axis**

    * **Ipsilateral** (by default), as in `SAUSAGE <https://asl-lex.org/visualization/?sign=sausage>`_
    * **Contralateral** (by default), as in `GAME <https://asl-lex.org/visualization/?sign=game>`_ 
    
        * OR
    
    * **Left**, as in the left hand of `SAUSAGE <https://asl-lex.org/visualization/?sign=sausage>`_, or as in `WEST <https://asl-lex.org/visualization/?sign=west>`_, where the absolute direction is encoded in the sign; the direction of the sign will be the same regardles of the signer's dominant hand.
    * **Right**, as in the left hand of `GAME <https://asl-lex.org/visualization/?sign=game>`_, or as in `EAST <https://asl-lex.org/visualization/?sign=east>`_, where the absolute direction is encoded in the sign; the direction of the sign will be the same regardles of the signer's dominant hand.

* **Not relevant**, as in `BOWTIE <https://asl-lex.org/visualization/?sign=bowtie>`_ [**REMOVE THIS?**]

See the :ref:`global_settings` page for how to switch between relative ipsi/contra and absolute left/right directions on the horizontal axis. See :ref:`signing_space_page` for a visual representation of each of these options, and more information about the horizontal axis in particular.

.. note::
    **Axis direction for circular shapes**

    Choosing an axis direction is straightforward for straight shapes, but there is flexibility in choosing a direction for circular shapes. You could choose the direction of the end of the first half of the circle relative to the beginning point, or the first initial direction of motion at the starting point, and so on. The most important thing is to maintain a consistent coding standard.

    Axis direction is a useful feature for recording the starting point of movement within a circle, and for specifying details related to the :ref:`movement relations<signtype_movement_relation>` of two-handed signs. For instance, `ROW <https://asl-lex.org/visualization/?sign=row>`_ is a two-handed sign where both hands are moving similarly in the same direction, and all aspects of movement are simultaneous and in sync. If axis direction is selected as the midpoint of the circle relative to the starting point, then a movement module to describe this sign could look like this:
    
    .. image:: images/mov_sample_sign_ROW.png
        :width: 750
        :align: center
        :alt: A movement module filled out with the specifications for both hands of ROW.
    
    Notice that it is possible for one module to describe both hands in this case, since the direction and location of each hand is the same relative to the other. 
    
    This would not be possible for a sign like `THEATER <https://asl-lex.org/visualization/?sign=theater>`_, a two-handed sign where both hands are moving similarly (as in, both are moving in circles) and in the same direction, but where all aspects of movement *except* location are simultaneous and in sync. Each hand needs to be specified separately, and they differ only in terms of their initial starting point within their respective circle, which is represented by axis direction. Again, the axis direction is selected as the midpoint of the circle relative to the starting point for each hand:
    
    .. image:: images/mov_sample_sign_THEATER_H1.png
        :width: 750
        :align: center
        :alt: A movement module filled out with the specifications for hand 1 of THEATER.
        
    .. image:: images/mov_sample_sign_THEATER_H2.png
        :width: 750
        :align: center
        :alt: A movement module filled out with the specifications for hand 2 of THEATER.
        
    The movements of both hands are identical in this coding other than for a single parameter. The differences in this sign between each hand are clear, and it is also possible to compare differences at the sign level between `ROW <https://asl-lex.org/visualization/?sign=row>`_ and `THEATER <https://asl-lex.org/visualization/?sign=theater>`_.

.. _plane_entry:

c) Plane
~~~~~~~~

In some cases, it is useful to specify not just the axis but also the **plane** (or combination of planes) that is relevant to describe the movement being coded in a particular module. For each selected plane, you can also choose a circular directionality if desired. See :ref:`circular directions<circular_directions>` for a definition of the default clockwise direction and what is meant by the 'top' of the circle for each plane. Any number of planes can be selected to apply to one movement, with or without an associated direction of movement.

This section is automatically specified by the program as 'not relevant' when the module includes a 'straight' perceptual shape, or when the axis direction is coded as 'not relevant' by the user. 

Keep in mind that a single module is meant to convey only one direction of movement, so selecting a combination of planes should be interpreted as a diagonal or angled movement with all of the selected planes (and circular directions, if applicable) applying simultaneously. See the description of :ref:`combinations of planes<planes_entry>` and :ref:`angled circular directions<circular_combinations>` for a visual description of how this works. For sequential movements in different planes, you should create multiple movement modules and use the :ref:`x-slot visualization window<sign_summary>` to assign a temporal order to the movement sequence.

At most one circular direction can be selected for each plane, so that a total maximum of three directions can apply at once within a module. For a movement that travels back and forth along both circular directions for a given plane, as in `WINDSHIELD_WIPERS <https://www.handspeak.com/word/index.php?id=3918>`_, you can either create a new module for each successive change in direction, or you can select that the movement is 'bidirectional' in the :ref:`movement characteristics<movement_chars>` options. In the case of bidirectional movements, you should establish a convention for selecting circular direction, such as always selecting the first direction of motion.

* **Mid-sagittal plane**

    * **Clockwise**, as in `BICYCLE <https://asl-lex.org/visualization/?sign=bicycle>`_ or `REASON <https://www.handspeak.com/word/index.php?id=3974>`_
    * **Counter-clockwise**, as in `BACK_UP <https://asl-lex.org/visualization/?sign=back_up>`_ or `ROW <https://asl-lex.org/visualization/?sign=row>`_

* **Horizontal plane**

    * **Ipsilateral from the top of the circle** (by default), as in `SWIM <https://asl-lex.org/visualization/?sign=swim>`_ or the left hand of `DECORATE_2 <https://asl-lex.org/visualization/?sign=decorate_2>`_
    * **Contralateral from the top of the circle** (by default), as in `CELEBRATE <https://asl-lex.org/visualization/?sign=celebrate>`_ or the right hand of `DECORATE_2 <https://asl-lex.org/visualization/?sign=decorate_2>`_
    
        * OR
    
    * **Clockwise**, as in left hand of `CELEBRATE <https://asl-lex.org/visualization/?sign=celebrate>`_ 
    * **Counter-clockwise**, as in `DECORATE_2 <https://asl-lex.org/visualization/?sign=decorate_2>`_ or the right hand of `CELEBRATE <https://asl-lex.org/visualization/?sign=celebrate>`_
    
* **Vertical plane**, as in `DRAW <https://asl-lex.org/visualization/?sign=draw>`_

    * **Ipsilateral from the top of the circle** (by default), as in `RAINBOW <https://asl-lex.org/visualization/?sign=rainbow>`_
    * **Contralateral from the top of the circle** (by default), as in `ENJOY <https://asl-lex.org/visualization/?sign=enjoy>`_
    
        * OR
    
    * **Clockwise**, as in `RAINBOW <https://asl-lex.org/visualization/?sign=rainbow>`_
    * **Counter-clockwise**, as in the right hand of `ENJOY <https://asl-lex.org/visualization/?sign=enjoy>`_

* **Not relevant**, as in `VALIDATE <https://asl-lex.org/visualization/?sign=validate>`_

See the :ref:`global_settings` page for how to switch between relative ipsi/contra and absolute left/right (counter-)clockwise directions for any circular shapes that involve the horizontal axis (i.e., those involving the vertical or horizontal planes). See :ref:`signing_space_page` for a visual representation of all of these options, and for more information on the horizontal axis in particular.

.. _joint_specific_movement_entry:

II. Joint-specific movements
============================

Make your selections from this section if you are coding a :ref:`joint_specific_movement`. This may be the only movement in a sign, as in `APPLE <https://asl-lex.org/visualization/?sign=apple>`_, or a single component of a more complex sign, like the closing and opening motions in `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_.

.. note::
    As with the other movement types, a module with this specification cannot be combined with the selections for a :ref:`handshape_change` or a movement with :ref:`perceptual_shape`. To code any information about other movements in the sign, add additional movement module(s) with the appropriate movement type(s). You can then adjust the timing of each module with respect to the others in the :ref:`x-slot visualization window<sign_summary>`. For example, to code the sign `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_, one would need two separate instances of the movement module, one for the straight (perceptual shape) movement of the hands and one for the joint-specific opening and closing movements.

Each joint-specific movement has two sub-options, which correspond to the two directions a movement can occur in. It is possible to use separate instances of the movement module for each direction, or to use one instance of the module and then code that movement as being 'bidirectional' in the :ref:`movement characteristics<movement_chars>` section. In the latter case, you would need to establish a convention such as explicitly selecting the direction that the movement *starts* with. All of our examples below assume this convention. 

As with all menus, selecting the sub-option will automatically select the broader option, saving a step of coding. Alternatively, the system does not require that you specify a sub-option, if for any reason it is preferable to leave the direction unspecified or if it is unknown. The appropriate joint activity can optionally be autofilled in the :ref:`joint activity<joint_activity_entry>` section once you have selected a sub-option for direction. Autofilling can be turned off in :ref:`global settings<global_settings>`.

The joint-specific movement options are as follows: 

:ref:`Nodding/Un-nodding<nodding_unnodding>`

* "Nodding" should be selected if the movement begins with a flexion of the wrist, such as `CORN_3 <https://asl-lex.org/visualization/?sign=corn_3>`_. This is an example of a sign that contains both nodding and un-nodding, however this option should also be selected for signs where there is only a single nodding motion, such as `CAN <https://asl-lex.org/visualization/?sign=can>`_, or signs where there is a repeated, unidirectional nodding, such as `YES <https://asl-lex.org/visualization/?sign=yes>`_. The :ref:`joint activity<joint_activity_entry>` section will be autofilled to *flexion* of the wrist. 
 
* "Un-nodding" should be selected if the movement begins with an extension of the wrist, or if it is the only movement involved, for example `GIVE_UP <https://asl-lex.org/visualization/?sign=give_up>`_. The :ref:`joint activity<joint_activity_entry>` section will be autofilled to *extension* of the wrist. 

:ref:`Pivoting<pivoting>`

* "To ulnar" should be selected if the movement begins with a pivot in the direction of the ulnar surface of the hand, as in `COOKIE <https://asl-lex.org/visualization/?sign=cookie>`_, or if it is the only direction involved. The :ref:`joint activity<joint_activity_entry>` section will be autofilled to *radial* deviation of the wrist.

* "To radial" should be selected if the movement begins with a pivot in the direction of the radial surface of the hand, or if it is the only direction involved. The :ref:`joint activity<joint_activity_entry>` section will be autofilled to *ulnar* deviation of the wrist.

:ref:`Twisting<twisting>`

* "Pronation" should be selected if the movement begins with pronation, or if it is the only direction involved, such as the subordinate hand of `DIE <https://asl-lex.org/visualization/?sign=die>`_. Selecting this will autofill to proximal radioulnar *pronation* in the :ref:`joint activity<joint_activity_entry>` section.
* "Supination" should be selected if the movement begins with supination, or if it is the only direction involved, such as `CLAUSE <https://asl-lex.org/visualization/?sign=clause>`_ and the dominant hand of `DIE <https://asl-lex.org/visualization/?sign=die>`_. Selecting this will autofill to proximal radioulnar *supination* in the :ref:`joint activity<joint_activity_entry>` section.

:ref:`Closing/Opening<closing_opening>`

* "Closing" should be selected if the movement begins with flexion of all joints of the selected finger(s), or if this is the only direction involved, such as `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_. The :ref:`joint activity<joint_activity_entry>` section will be autofilled to *flexion* of [selected finger, all joints].

* "Opening" should be selected if the movement begins with extension of all joints of the selected finger(s), or if this is the only direction involved, such as `BOWTIE <https://asl-lex.org/visualization/?sign=bowtie>`_. The :ref:`joint activity<joint_activity_entry>` section will be autofilled to *extension* of [selected finger, all joints].

:ref:`Pinching/Un-pinching<pinching_unpinching>`

* "Pinching" should be selected if the movement begins with adduction of the thumb base joint, such as `TURTLE <https://asl-lex.org/visualization/?sign=turtle>`_, or if it is the only direction involved. The :ref:`joint activity<joint_activity_entry>` section will be autofilled to *adduction* of thumb base joint.

* "Un-pinching" should be selected if the movement begins with abduction of the thumb base joint, or if it is the only direction involved, such as `DELETE <https://www.handspeak.com/word/index.php?id=554>`_. The :ref:`joint activity<joint_activity_entry>` section will be autofilled to *abduction* of thumb base joint.

:ref:`Flattening/Straightening<flattening_straightening>`

* "Flattening" should be selected if the movement begins with flexion of the base joints of the selected fingers, such as `HORSE <https://asl-lex.org/visualization/?sign=horse>`_, or if it is the only direction involved. The :ref:`joint activity<joint_activity_entry>` section will be autofilled to *flexion* of [selected finger base joints].

* "Straightening" should be selected if the movement begins with extension of the base joints of the selected fingers, or if it is the only direction involved. The :ref:`joint activity<joint_activity_entry>` section will be autofilled to *extension* of [selected finger base joints].

:ref:`Hooking/Un-hooking<hooking_unhooking>`

* "Hooking", or "clawing", should be selected if the movement begins with flexion of the non-base joints of the selected fingers,  or if it is the only direction involved, such as  `CLAUSE <https://asl-lex.org/visualization/?sign=clause>`_. The :ref:`joint activity<joint_activity_entry>` section will be autofilled to *flexion* of [selected finger non-base joints].

* "Un-hooking" should be selected if the movement begins with  extension of the non-base joints of the selected fingers, or if it is the only direction involved, such as `UPLOAD <https://asl-lex.org/visualization/?sign=upload>`_. The :ref:`joint activity<joint_activity_entry>` section will be autofilled to *extension* of [selected finger non-base joints].

:ref:`Spreading/Un-spreading<spreading_unspreading>`

* "Spreading" should be selected if the movement begins with the abduction of the base joints of the selected fingers, or if it is the only direction involved, such as `SEND <https://asl-lex.org/visualization/?sign=send>`_. The :ref:`joint activity<joint_activity_entry>` section will be autofilled to *abduction* of [selected finger base joints]. 

* "Un-spreading" should be selected if the movement begins with the adduction of the base joints of the selected fingers, or if it is the only direction involved, such as `RUN_OUT_OF <https://asl-lex.org/visualization/?sign=run_out_of>`_ or `SCISSORS <https://asl-lex.org/visualization/?sign=scissors>`_. The :ref:`joint activity<joint_activity_entry>` section will be autofilled to *abduction* of [selected finger base joints]. 

:ref:`Rubbing<rubbing>`

* "Thumb crosses over the palm" should be selected if the thumb crosses over the palm, as in `FEW <https://asl-lex.org/visualization/?sign=few>`_. The :ref:`joint activity<joint_activity_entry>` section will be autofilled to [complex/multi-joint].

* "Thumb moves away from palm" should be selected if the thumb moves away from the palm, as in `DOG <https://asl-lex.org/visualization/?sign=dog>`_. The :ref:`joint activity<joint_activity_entry>` section will be autofilled to [complex/multi-joint].

:ref:`Wiggling or fluttering<wiggling_fluttering>`

* This should be selected if the selected fingers wiggle, or flutter, such as in the signs `DIRTY <https://asl-lex.org/visualization/?sign=dirty>`_, `SALT <https://asl-lex.org/visualization/?sign=salt>`_, `BEACH <https://asl-lex.org/visualization/?sign=beach>`_. The :ref:`joint activity<joint_activity_entry>` section will be autofilled to both flexion and extension of the selected fingers' base joints.

The "none of these" option should be selected if joint-specific movement does not apply to the sign being coded. 

.. _handshape_change_entry:

III. Handshape change
=====================

Make your selections from this section if you are coding a :ref:`handshape_change`. 

.. note::
    As with the other movement types, a module with this specification cannot be combined with the selections for a :ref:`joint_specific_movement` or a movement with :ref:`perceptual_shape`. To code any information about other movements in the sign, add additional movement module(s) with the appropriate movement type(s). You can then adjust the timing of each module with respect to the others in the :ref:`x-slot visualization window<sign_summary>`. For example, to code the sign `WORKSHOP <https://asl-lex.org/visualization/?sign=workshop>`_, one would need two separate instances of the movement module, one for the circular (perceptual shape) movement of the hands and one for the handshape change from W to S.
    
No further details of the handshape change itself need to be provided in this section, because they can be better coded in the :ref:`hand_configuration_module`. It is left to the discretion of the user as to how exactly these two modules interact with each other. For example, in `STYLE <https://www.handspeak.com/word/index.php?id=4174>`_, one could code five movements (one perceptual shape of the circle that lasts the whole duration of the sign, plus one handshape change movement for each change between letters, S --> T, T --> Y, Y --> L, L --> E, each aligned with a timepoint within the whole duration of the sign), or code two movements (one perceptual shape of the circle that lasts the whole duration of the sign, plus one generic handshape change movement that also encompasses the duration of the sign). In either case, there would be five different hand configuration modules instantiated, one for each letter.

.. _joint_activity_entry:

2. Joint activity
``````````````````

Use the **joint activity** section to add more fine-grained detail about any joint movements related to the current module. If the module describes a :ref:`joint_specific_movement`, then the program can :ref:`autofill<auto_gen>` the joint movements that are predictable from the selections made earlier within its :ref:`movement type<joint_specific_movement_entry>` section. See the :ref:`global_settings` for how to change the program's default autofill behaviour.

**(A note on user flexibility: this section can encode the phonetics of proximalization/distalization, differences in sizes of the same perceptual shape based on the joints involved, etc.)**

.. _movement_chars:

3. Movement characteristics
```````````````````````````

...

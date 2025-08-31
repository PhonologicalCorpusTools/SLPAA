.. todo::
    note on connectedness
    work on movement type
        - fix references
        - update / delete refs to “transcription process”
    axis direction: change 'both hands move in opposite directions' to the new button menu
    joint activity
    movement characteristics
        
.. _movement_module:

***************
Movement Module
***************

This :ref:`module` is used to code the **movement** components of a sign. As many :ref:`instances<instance>` of this module as necessary can be called for any given sign coding. For more discussion on the use of modules in SLP-AA to encode information about signs, see :ref:`modularity`.

Hand Selection
`````````````````

Select the hand(s) involved in this instance of the module. For movements involving both hands, you can also optionally specify whether the movement described in this :ref:`instance` of the module is in phase or out of phase. If the hands are not out of phase, you can also choose to select if the hands are moving as a connected unit.

.. note::
    **Phasing**
    
    Conventionally, Movements are *in phase* if the hands have the same specifications for Movement at the same time, and are *out of phase* if the specifications are the same for each hand but with different timing. In either case, specifications from H1 will be predictable for H2 from the indication of phasing.
    
    For instance, following SLP-AA conventions, a two-handed :ref:`joint_specific_movement` (like `POPCORN <https://asl-lex.org/visualization/?sign=popcorn>`_) may use one category of movement (like :ref:`Closing/Opening<closing_opening>`) for both hands, though the specification for each hand within that category is *out of phase* with the other (as in, one hand is *closing* while the other one is *opening*).
    
    A two-handed :ref:`perceptual_shape` movement is *out of phase* if the hands reach different points of the perceptual shape at the same time, as in `PACK <https://asl-lex.org/visualization/?sign=pack>`_ or `THEATER <https://asl-lex.org/visualization/?sign=theater>`_. Conversely, the movement is *in phase* if both hands reach the same point of the perceptual shape at the same time, as in `ROW <https://asl-lex.org/visualization/?sign=row>`_ or `BLANKET <https://asl-lex.org/visualization/?sign=blanket>`_.
    
        In the following sample coding of the movement in `ROW <https://asl-lex.org/visualization/?sign=row>`_, all specifications for both hands are identical and the movement is in phase:

    .. image:: images/mov_sample_sign_ROW.png
        :width: 750
        :align: center
    
    The movement of both hands can easily be described together in one instance of Movement.
    
    The following sample coding of the movement in `THEATER <https://asl-lex.org/visualization/?sign=theater>`_ is similar except that the hands are indicated to be out of phase, since they reach the top of the circle at different times:

    .. image:: images/mov_sample_sign_THEATER.png
        :width: 750
        :align: center

    The movements of both hands can still be described together in one module instance as long as they are indicated to be out of phase. This allows for quicker sign coding while retaining key information for searching and analysis.
    
.. note::
    **Connectedness**

Hands are connected if undergo the same movement simultaneously
    **(Add short description here)**: reference Morgan's dissertation and/or book. Link to glossary term for :ref:`connected`.
    
Timing Selection
`````````````````

Module instances link to generic :ref:`x-slots<x_slot>` to record information about their timing relative to any others within a sign. For more information on the use of x-slots in SLP-AA, consult :ref:`timing_page`.
    
.. _movement_type_entry:

1. Movement type
`````````````````

Select the **movement type** for the current module. The three movement types are mutually exclusive within an instance of a module; that is, a single instance of the module can be specified for only one of these three types of movement.

.. note::
    **No movement**
    
    If any portion of a sign includes a prominent moment of intended stillness (for instance, `MISS <https://asl-lex.org/visualization/?sign=miss>`_ or `ONE <https://www.handspeak.com/word/index.php?id=1554>`_), select the 'No movement' option. When applicable, this is the only selection within the module as it is mutually exclusive with all other movement options. This selection can apply for only one portion of a sign which otherwise does have movement, which is what makes it useful above and beyond the 'no movement' options in :ref:`sign_type`.

Movement type options include:

* :ref:`perceptual_shape`, as in `NORTH <https://asl-lex.org/visualization/?sign=north>`_
* :ref:`joint_specific_movement`, as in `APPLE <https://asl-lex.org/visualization/?sign=apple>`_
* :ref:`handshape_change`, as in `HIGH_SCHOOL <https://asl-lex.org/visualization/?sign=high_school>`_

Note that in SLP-AA, we do not require users to classify movements into the traditional categories of ‘path’ / ‘major’ / ‘primary’ vs. ‘local’ / ‘minor’ / ‘secondary’ movements. Instead, we have classifications for “perceptual shape movements” (e.g., straight, circle, arc), “joint-specific movements” (e.g., twisting, closing), and “handshape changes” (e.g., fingerspelling). As Napoli et al. (2011: 19) point out, “the actual distinction between primary and secondary movement is not uncontroversial and is far from simple.” For example, while wrist movements are typically considered local movements according to articulatory definitions of path and local movement categories (e.g., Brentari, 1998), some of them have been categorized as path movements (van der Kooij, 2002: 229; Sehyr et al., 2021: 269). Furthermore, forcing the choice between path and local movements at the level of phonetic transcription could mask empirical phenomena such as proximalization and distalization (Brentari, 1998), in which both path and local movements can be articulated by non-canonical joints. 

In response to these issues, our system allows any movement in which the hand or arm draws a perceptual shape in space to be classified as perceptual movement, with optional manual specifications of the exact (combination of) joints executing the movement under a separate “joint activity” section. For example, the sign `NORTH <https://asl-lex.org/visualization/?sign=north>`_ is canonically signed as a straight perceptual movement that is articulated at the shoulder. A distalized version of this sign might be produced with an "un-nodding" wrist movement. In such a case, one could code this either as a joint-specific wrist-nod movement OR one could preserve the 'phonological intention' of the perceptual straight movement and simply add the fact that it is articulated with wrist flexion in the :ref:`joint activity<joint_activity_entry>` section.

Traditional local movements (relating to particular joints) defined in the literature are listed under the joint-specific movement section, with the associated joint activities optionally autofilled (e.g., the joint-specific movement of “closing” can autofill to flexion of finger joints in the “joint activity” section). 

Note that after the movement type selections have been made, there are separate additional sections for coding the :ref:`joint activity<joint_activity_entry>` and the :ref:`movement characteristics<movement_chars>`. 

.. note::
    There is often some flexibility as to whether different components of movement can be counted as separate modules or part of the same one. See :ref:`modularity` for more in-depth discussion of this idea.
    
    At minimum, for signs with multiple (simultaneous and/or sequential) movements, give each movement type its own module. That is, code any :ref:`joint_specific_movement` separately from any movement with :ref:`perceptual_shape` as well as any :ref:`handshape_change`, as these are mutually exclusive by definition. You can then adjust the timing of each module with respect to the others in the :ref:`x-slot visualization window<sign_summary>`.
    
    This means that signs with complex movements like `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_ and `EVERY_YEAR <https://www.signingsavvy.com/sign/EVERY+YEAR>`_ require at least two movement modules, including a perceptual shape and a joint-specific movement.
    
    The number of modules needed to describe a movement may also depend on your choices in terms of :ref:`movement characteristics<movement_chars>` (e.g., how repetitions are coded). 

.. _perceptual_shape_entry:

I. Perceptual shape
===================

Make your selections from this section if you are coding a movement with :ref:`perceptual_shape`. This could be the only movement in a sign, as in `NORTH <https://asl-lex.org/visualization/?sign=north>`_, or a single component of a more complex sign, like the path movements in `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_.

.. note::
    As with the other movement types, a module with this specification cannot be combined with the selections for a :ref:`handshape_change` or a movement with :ref:`joint_specific_movement`. To code any information about other movements in the sign, add additional movement module(s) with the appropriate movement type(s). You can then adjust the timing of each module with respect to the others in the :ref:`x-slot visualization window<sign_summary>`. For example, to code the sign `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_, one would need two separate instances of the movement module, one for the straight (perceptual shape) movement of the hands and one for the joint-specific opening and closing movements.

.. _shape_entry:

a) Shape
~~~~~~~~

Select the **shape** of the movement.

Only one shape option can be specified per module. When you want to indicate multiple perceptual shapes in one sign, as you could for `SIGN_LANGUAGE <https://asl-lex.org/visualization/?sign=sign_language>`_, one way to code the full set of movements is to add as many modules as there are distinct shapes. The timing of each movement with respect to the others can then be seen in the :ref:`x-slot visualization window<sign_summary>`. For perceptual shapes that do not fit into the default list, the **Other [specify]** option allows one to manually input a custom shape. 

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
* **Other [specify]**

.. _axis_direction_entry:

b) Axis direction
~~~~~~~~~~~~~~~~~

Select an **axis direction** (or a combination of axis directions) that describe the direction of movement. It is also possible to select an axis without a specific direction.

If the hands have opposite specifications for axis direction within every applicable axis, select the checkbox for *H1 and H2 move in opposite directions* and continue to fill out the instance of the module as it applies to H1. The axis direction for H2 can then be defined implicitly without coding another :ref:`instance` of Movement for each hand. This selection does not apply for signs where the hands move along different (sets of) axes, like `TAPE <https://asl-lex.org/visualization/?sign=tape>`_.

Keep in mind that a single :ref:`instance` of the module is meant to convey only one direction of movement, so selecting a combination of axes should be interpreted as a diagonal or angled movement with all of the selected directions applying simultaneously. See the section on :ref:`Angled axes<angled_axes>` for a visual description of how this works. To instead indicate a sequence of movements in different planes or directions, create multiple instances of the Movement module, associate them with separate (and sequential) :ref:`timing values<timing_page>`, and select the appropriate direction for each one.

At most one direction can be selected for each axis, so that a total maximum of three directions can apply at once within a module. For a movement that travels back and forth along both directions for a given axis, as in `WINDSHIELD_WIPERS <https://www.handspeak.com/word/index.php?id=3918>`_, you can either create a new module for each successive change in direction, or you can select that the movement is *bidirectional* in the :ref:`movement characteristics<movement_chars>` options. A bidirectional movement may have a specified first direction of motion or remain unspecified.

There are two ways of defining an axis in the software: :ref:`Absolute_entry` and :ref:`Relative_entry`

.. _Absolute_entry:

Absolute
^^^^^^^^^

Absolute axes are based on :ref:`cardinal axes` and the pertinent hand of the signer. Using absolute axes means that the description of a sign does not change depending on whether H1 is the left or right hand. 

* **Horizontal axis: absolute**

    * **Ipsilateral**, as in `SAUSAGE <https://asl-lex.org/visualization/?sign=sausage>`_
    * **Contralateral**, as in `GAME <https://asl-lex.org/visualization/?sign=game>`_ 
    
* **Vertical axis**

    * **Up**, as in `UMBRELLA <https://asl-lex.org/visualization/?sign=umbrella>`_ or `NORTH <https://asl-lex.org/visualization/?sign=north>`_
    * **Down**, as in `LOSE_GAME <https://asl-lex.org/visualization/?sign=lose_game>`_ or `DRAW <https://asl-lex.org/visualization/?sign=draw>`_
    
* **Sagittal axis**

    * **Distal**, as in `NEXT <https://asl-lex.org/visualization/?sign=next>`_ or `SINCE <https://asl-lex.org/visualization/?sign=since>`_
    * **Proximal**, as in `BEFORE <https://asl-lex.org/visualization/?sign=before>`_ 
    
* **Not relevant**, as in `ROW <https://asl-lex.org/visualization/?sign=row>`_. Axis direction is not relevant for this sign because the perceptual shape is *circle*, whereas axis direction is only relevant for other perceptual shapes.

See :ref:`signing_space_page` for a visual representation of these options.

.. warning::
    **(For Kathleen and Oksana)** - relevant to the note below
    
    From the 'to mention' doc: One example of where right-left rather than ipsi-contra distinction is useful, if not necessary, is indicating (referential?) signs, as described in Johnson & Liddell 2021 (p. 136-138). Maybe give this example?
    
    Resolved by giving examples of EAST and WEST? Reference J&L.
    
    (We don't use right and left for the absolute directions anymore, but the reference could still be helpful - Nico)

.. Relative_entry:

Relative
^^^^^^^^^

Relative axes are based on anatomical position; This set of axes can be easier in the case where movement is relative to a body part. For example, in `CHARGE_CARD <https://asl-lex.org/visualization/?sign=charge_card>`_, H1 can be said to be moving relative to H2 rather than absolute cardinal directions.

The default list of relative axes is:

* **Finger**
* **Hand**
* **Forearm**
* **Upper Arm**
* **Arm**

Therefore, using relative axes, `CHARGE_CARD <https://asl-lex.org/visualization/?sign=charge_card>`_ could be described as being relative to the hand, along to the finger end:

.. image:: images/charge_v2_example.png
    :width: 500
    :align: center

.. note::
    **Left and right vs. H1 and H2 side**
    
    In some circumstances, the direction of movement is lexically encoded to be towards a side of the body independent of the signer's handedness. This is the case for `WEST <https://asl-lex.org/visualization/?sign=west>`_, where the direction of movement is towards the signer's left (regardless of the signer's dominant hand), and `EAST <https://asl-lex.org/visualization/?sign=east>`_, where the direction of movement is towards the signer's right.
    
    Both of the models for the horizontal axis used in SLP-AA can describe the articulated movement in these (and any other) signs, but neither one can capture the the full implications of the lexical definition using only the phonetic descriptors available in Movement. For signs like this, it may be helpful to indicate the definition elsewhere in the sign coding, like in the notes of the :ref:`sign_level_info`.

.. _plane_entry:

c) Plane
~~~~~~~~

In some cases, it is useful to specify not just the axis but also the **plane** (or combination of planes) that is relevant to describe the movement being coded. For each selected plane, you can further specify a direction along the cardinal axis if desired.

If the hands have opposite specifications for circular direction within every applicable plane, select the checkbox for *H1 and H2 move in opposite directions* and continue to fill out the instance of the module as it applies to H1. The circular direction for H2 can then be defined implicitly without coding another :ref:`instance` of Movement for each hand.
    
Keep in mind that a single instance of the module is meant to convey only one direction of movement, so a selection of a combination of planes is interpreted as a diagonal or angled movement with all of the selected planes (and circular directions, if applicable) applying simultaneously. See the sections on :ref:`Angled planes<angled_planes>` and :ref:`Angled circular directions<angled_circles>` for a visual description of how this works. To instead indicate a sequence of movements in different planes or directions, create multiple instances of the Movement module, associate them with separate (and sequential) :ref:`timing values<timing_page>`, and select the appropriate direction for each one.

At most one circular direction can be selected for each plane, so that a total maximum of three directions can apply at once within a module. For a movement that travels back and forth along both circular directions for a given plane, as in `WINDSHIELD_WIPERS <https://www.handspeak.com/word/index.php?id=3918>`_, you can either create a new module for each successive change in direction, or you can select that the movement is *bidirectional* in the :ref:`movement characteristics<movement_chars>` options.

See :ref:`Circular directions<circular_directions>` for a description of what we define to be the 'top of a circle' for each plane.

Planes can be defined in the same way as axes: :ref:`Absolute_entry` and :ref:`Relative_entry`

Absolute
^^^^^^^^^

Select the plane which the sign moves along. See :ref:`_planes_entry` for a description of cardinal planes.

* **Horizontal plane**

    * **Ipsilateral from the top of the circle**, as in `SWIM <https://asl-lex.org/visualization/?sign=swim>`_ or the left hand of `DECORATE_2 <https://asl-lex.org/visualization/?sign=decorate_2>`_
    * **Contralateral from the top of the circle**, as in `CELEBRATE <https://asl-lex.org/visualization/?sign=celebrate>`_ or the right hand of `DECORATE_2 <https://asl-lex.org/visualization/?sign=decorate_2>`_

* **Vertical plane**
    
    * **Toward H1 side from the top of the circle**, as in `RAINBOW <https://asl-lex.org/visualization/?sign=rainbow>`_ or the left hand of `ENJOY <https://asl-lex.org/visualization/?sign=enjoy>`_
    * **Toward H2 side from the top of the circle**, as in the right hand of `ENJOY <https://asl-lex.org/visualization/?sign=enjoy>`_

* **Sagittal plane**

    * **Distal from the top of the circle**, as in `BICYCLE <https://asl-lex.org/visualization/?sign=bicycle>`_ or `REASON <https://www.handspeak.com/word/index.php?id=3974>`_
    * **Proximal from the top of the circle**, as in `BACK_UP <https://asl-lex.org/visualization/?sign=back_up>`_ or `ROW <https://asl-lex.org/visualization/?sign=row>`_

* **Not relevant**, as in `VALIDATE <https://asl-lex.org/visualization/?sign=validate>`_. Plane is not relevant for this sign because the perceptual shape is *straight*, whereas plane is only relevant for perceptual shapes that are not *straight*.

Relative
^^^^^^^^^

Similarly to :ref:`Relative_entry`, it may be easier to describe a plane relative to body parts rather than absolute cardinal axes. Each body part in the default list has 3 options to select from:

* **On plane of [body part]**
* **Perpendicular to plane of [body part], across length**
* **Perpendicular to plane of [body part], across width**


See :ref:`signing_space_page` for a visual representation of these options.

.. _joint_specific_movement_entry:

II. Joint-specific movements
============================

Make your selections from this section if you are coding a :ref:`joint_specific_movement`. This may be the only movement in a sign, as in `APPLE <https://asl-lex.org/visualization/?sign=apple>`_, or a single component of a more complex sign, like the closing and opening motions in `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_.

.. note::
    As with the other movement types, a module with this specification cannot be combined with the selections for a :ref:`handshape_change` or a movement with :ref:`perceptual_shape`. To code any information about other movements in the sign, add additional movement module(s) with the appropriate movement type(s). You can then adjust the timing of each module with respect to the others in the :ref:`x-slot visualization window<sign_summary>`. For example, to code the sign `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_, one would need two separate instances of the movement module, one for the straight (perceptual shape) movement of the hands and one for the joint-specific opening and closing movements.

Each joint-specific movement except for :ref:`Rubbing<rubbing>` has two sub-options, which correspond to the two directions a movement can occur in. It is possible to use separate instances of the movement module for each direction, or to use one instance of the module and then code that movement as being 'bidirectional' in the :ref:`movement characteristics<movement_chars>` section. In the latter case, you would need to establish a convention such as explicitly selecting the direction that the movement starts with. All of our examples below assume this convention. 

As with all menus, selecting the sub-option will automatically select the broader option, saving a step of coding. Alternatively, the system does not require that you specify a sub-option, if for any reason it is preferable to leave the direction unspecified or if it is unknown.
The joint-specific movement options are as follows: 

**TODO: move these to the glossary??**

:ref:`Nodding/Un-nodding<nodding_unnodding>`

* **Nodding** refers to movement beginning with a flexion of the wrist, such as `CORN_3 <https://asl-lex.org/visualization/?sign=corn_3>`_. This is an example of a sign that contains both nodding and un-nodding, however this option can also be selected for signs where there is only a single nodding motion, such as `CAN <https://asl-lex.org/visualization/?sign=can>`_, or signs where there is a repeated, unidirectional nodding, such as `YES <https://asl-lex.org/visualization/?sign=yes>`_.
 
* **Un-nodding** refers to movement beginning with an extension of the wrist, or if it is the only movement involved, for example `GIVE_UP <https://asl-lex.org/visualization/?sign=give_up>`_. 

:ref:`Pivoting<pivoting>`

* **Ulnar** refers to movement beginning with a pivot in the direction of the ulnar surface of the hand, as in `COOKIE <https://asl-lex.org/visualization/?sign=cookie>`_, or if it is the only direction involved.

* **Radial** refers to movement beginning with a pivot in the direction of the radial surface of the hand, or if it is the only direction involved.

:ref:`Twisting<twisting>`

* **Pronation** refers to movement beginning with pronation, or if it is the only direction involved, such as the subordinate hand of `DIE <https://asl-lex.org/visualization/?sign=die>`_.
* **Supination** refers to movement beginning with supination, or if it is the only direction involved, such as `CLAUSE <https://asl-lex.org/visualization/?sign=clause>`_ and the dominant hand of `DIE <https://asl-lex.org/visualization/?sign=die>`_.

:ref:`Closing/Opening<closing_opening>`

* **Closing** refers to movement beginning with flexion of all joints of the selected finger(s), or if this is the only direction involved, such as `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_.

* **Opening** refers to movement beginning with extension of all joints of the selected finger(s), or if this is the only direction involved, such as `BOWTIE <https://asl-lex.org/visualization/?sign=bowtie>`_.

:ref:`Pinching/Un-pinching<pinching_unpinching>`

* **Pinching** refers to movement beginning with adduction of the thumb base joint, such as `TURTLE <https://asl-lex.org/visualization/?sign=turtle>`_, or if it is the only direction involved.

* **Un-pinching** refers to movement beginning with abduction of the thumb base joint, or if it is the only direction involved, such as `DELETE <https://www.handspeak.com/word/index.php?id=554>`_.

:ref:`Flattening/Straightening<flattening_straightening>`

* **Flattening** refers to movement beginning with flexion of the base joints of the selected fingers, such as `HORSE <https://asl-lex.org/visualization/?sign=horse>`_, or if it is the only direction involved.

* **Straightening** refers to movement beginning with extension of the base joints of the selected fingers, or if it is the only direction involved.

:ref:`Hooking/Un-hooking<hooking_unhooking>`

* **Hooking**, or "clawing", refers to movement beginning with flexion of the non-base joints of the selected fingers,  or if it is the only direction involved, such as  `CLAUSE <https://asl-lex.org/visualization/?sign=clause>`_.

* **Un-hooking** refers to movement beginning with extension of the non-base joints of the selected fingers, or if it is the only direction involved, such as `UPLOAD <https://asl-lex.org/visualization/?sign=upload>`_.

:ref:`Spreading/Un-spreading<spreading_unspreading>`

* **Spreading** refers to movement beginning with the abduction of the base joints of the selected fingers, or if it is the only direction involved, such as `SEND <https://asl-lex.org/visualization/?sign=send>`_.

* **Un-spreading** refers to movement beginning with the adduction of the base joints of the selected fingers, or if it is the only direction involved, such as `RUN_OUT_OF <https://asl-lex.org/visualization/?sign=run_out_of>`_ or `SCISSORS <https://asl-lex.org/visualization/?sign=scissors>`_.

:ref:`Rubbing<rubbing>` 
Refers to movement in which an articulator makes contact as it moves across/along a location, such as `MONEY_2 <https://asl-lex.org/visualization/?sign=money_2>`_.
Further specifications include:

* **Articulator(s)** refers to which body part is moving.

    * **Thumb**
    * **Finger(s)**
    * **Other [specify]**

* **Location** refers to which body part the articulator is making contact while moving.

    * **Thumb**
    * **Finger(s)**
    * **Palm**
    * **Other [specify]**

* **Across**

    * **to radial side**
    * **to ulnar side**

* **Along**

    * **to fingertip end**
    * **to base end**

Using these specifications, `MONEY_2 <https://asl-lex.org/visualization/?sign=money_2>`_ could be described as having a **thumb** articulator moving **across** the **finger(s)** location:

.. image:: images/money_v2_example.png
    :width: 500
    :align: center

This description considers the rubbing to be bidirectional since there is no specified beginning direction, therefore *to the radial side* or *to the ulnar side* remain unselected.

:ref:`Wiggling or fluttering<wiggling_fluttering>`

* **Wiggling/Fluttering** refers to movement where selected fingers wiggle or flutter, such as in the signs `DIRTY <https://asl-lex.org/visualization/?sign=dirty>`_, `SALT <https://asl-lex.org/visualization/?sign=salt>`_, or `BEACH <https://asl-lex.org/visualization/?sign=beach>`_.

:ref:`Other [specify]<Other>`

* The **Other** option allows for a joint-specific movement that does not seem to correspond with any (single or combination) of the movements in the list above. One can type in the specific movement that is wanted. 

.. _handshape_change_entry:

III. Handshape change
=====================

Make your selections from this section if you are coding a :ref:`handshape_change`. 

.. note::
    As with the other movement types, a module with this specification cannot be combined with the selections for a :ref:`joint_specific_movement` or a movement with :ref:`perceptual_shape`. To code any information about other movements in the sign, add additional movement module(s) with the appropriate movement type(s). You can then adjust the timing of each module with respect to the others in the :ref:`x-slot visualization window<sign_summary>`. For example, to code the sign `WORKSHOP <https://asl-lex.org/visualization/?sign=workshop>`_, one would need two separate instances of the movement module, one for the circular (perceptual shape) movement of the hands and one for the handshape change from W to S.
    
No further details of the handshape change itself need to be provided in this section, because they can be better coded in the :ref:`hand_configuration_module`. It is left to the discretion of the user as to how exactly these two modules interact with each other. For example, in `STYLE <https://www.handspeak.com/word/index.php?id=4174>`_, one could code five movements (one perceptual shape of the circle that lasts the whole duration of the sign, plus one handshape change movement for each change between letters, S → T, T → Y, Y → L, L → E, each aligned with a timepoint within the whole duration of the sign), or code two movements (one perceptual shape of the circle that lasts the whole duration of the sign, plus one generic handshape change movement that also encompasses the duration of the sign). In either case, there would be five different hand configuration modules instantiated, one for each letter.

.. _joint_activity_entry:

2. Joint activity
``````````````````

Use the **joint activity** section to add more fine-grained detail about any joint movements related to the current module.

**(A note on user flexibility: this section can encode the phonetics of proximalization/distalization, differences in sizes of the same perceptual shape based on the joints involved, etc.)**

.. _movement_chars:

3. Movement characteristics
```````````````````````````

Select **Movement characteristics** to further specify details of a sign's movement. These describe the ways in which the sign moves rather than the movement itself.

.. _Repetition_entry:

I. Repetition
===================

Select whether the movement is **Unidirectional** or **Bidirectional**.

.. _Directionality_entry:

II. Directionality
===================

Select whether the movement is Unidirectional (moving in one direction along an axis), or Bidirectional (moving in both directions along an axis). 

.. note::
    **Lexical vs. Transitional**
    We leave it to the discretion of the coder whether transitional movement is considered in directionality. For example, `PIANO <https://asl-lex.org/visualization/?sign=piano>`_ is lexically bidirectional, since the fingers are fluttering as the hands move in both directions. 

    Meanwhile `FINGERSPELLING <https://asl-lex.org/visualization/?sign=fingerspelling>`_ is lexically undirectional, since the fingers are fluttering only while the hand moves :ref:`ipsilaterally<ipsilateral>`. However, technically, the sign does move in both directions since it moves :ref:`contralaterally<contralateral>` when transitioning back to the original position in order to repeat itself.

As mentioned in the :ref:`_axis_direction_entry`, a movement may have a specified first direction of motion or remain unspecified depending on whether a direction is checked off in the axis options. For example, `PIANO <https://asl-lex.org/visualization/?sign=piano>`_ does not have specified first direction, it can begin ipsilaterally or contralaterally, while `CROCODILE <https://asl-lex.org/visualization/?sign=crocodile>`_ is bidirectional with the first direction of motion being *vertical, up*

.. _add_chars_entry:
III. Additional Characteristics
===================

**Additional Characteristics** are descriptors of the movement. Each characteristic in the list has three scalar options from strongest to weakest, as well as an *other [specify]* option, for describing the movement of a sign. These adjectives can also be specified as to what they are *relative to*, for example whether the movement is small relative to the hand or relative to the body.

As with all menus, selecting the sub-option will automatically select the broader option, saving a step of coding.
The additional characteristic options are as follows:

* **Size**
* **Speed**
* **Force**
* **Tension**
* **Other [specify]**

.. todo::
    Some notes to use as starting points for some of these characteristics:
    ‘repeated in a different location’ — that would be used for what Hope Morgan calls “dispersed” signs, like HOME (https://asl-lex.org/visualization/?sign=home)
    'trill' -- this is for “small, rapidly repeated dynamic elements during the production of signs” (to quote Brentari 1996:45). This most typically happens with small joint-specific movements as in DIRTY (https://asl-lex.org/visualization/?sign=dirty), which is described as having the fingers ‘flutter’ in the dictionary.

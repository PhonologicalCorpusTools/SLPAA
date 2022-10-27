.. todo::
  update the screenshot of the selection window
  add notes for the (new!) automatic greying-out for impossible/unnecessary combinations
  is the movement direction relation section up to date?

.. _sign_type_module:

***********
Sign Type 
***********

This module is used to identify the overarching ‘kind’ of sign by selecting specifications for the behaviours of each hand (H1 & H2) in relation to each other. 

.. _signtype_one_hand: 

1. Number of hands: 1 hand
``````````````````````````

Select this if the sign involves only one hand. 

- "The hand moves" should be selected if the hand is involved in either a perceptual shape (e.g., `NORTH <https://asl-lex.org/visualization/?sign=north>`_) or a joint-specific movement (e.g., `APPLE <https://asl-lex.org/visualization/?sign=apple>`_, `STYLE <https://www.handspeak.com/word/search/index.php?id=4174>`_, `HIGH SCHOOL <https://asl-lex.org/visualization/?sign=high_school>`_)

- "The hand does not move" should be selected if the hand is not involved in any movement, such as `ONE <https://www.handspeak.com/word/search/index.php?id=1554>`_.

Note that if the forearm, elbow, or wrist of the H2 is involved, there are several ways this could be coded in SLP-AA, and users should define their own conventions for consistency. Some options are: (1) the user can decide to specify the sign as one-handed and include the use of H2 in the specifications of contact and location; (2) the user can specify the sign as one-handed and select "forearm involved" in the hand configuration module; or (3) the user can specify the sign as two-handed, also specifying that "only H1 moves". For example, the sign `CRACKER <https://asl-lex.org/visualization/?sign=cracker>`_ could be coded as (1) one-handed, with H1 making contact to H2 at the elbow; (2) one-handed, with "forearm involved" selected in the hand configuration module; or (3) two-handed, with only H1 specified as moving. The sign `TABLE <https://asl-lex.org/visualization/?sign=table>`_ could be coded with the same basic options, with the additional possibility of coding the contact that H2 makes with the elbow of H1 in a separate location module and contact module.

.. _signtype_two_hands:

2. Number of hands: 2 hands
```````````````````````````

Select this if both hands are involved in the sign. See note above if forearm, wrist, or elbow of the second hand are involved. 

.. _signtype_handshape_relation:

I. Handshape relation
=====================

- "H1 and H2 involve the same set(s) of handshapes" should be selected if all the handshapes used at any point during the sign are shared between both hands. This can be because the handshapes never change (e.g., `BICYCLE <https://asl-lex.org/visualization/?sign=bicycle>`_), or because the handshapes change but involve the same shapes on both hands. In the latter case, the handshapes can alternate (e.g., `MILK <https://asl-lex.org/visualization/?sign=milk_2>`_) or change at the same time as each other (e.g., `BOWTIE <https://asl-lex.org/visualization/?sign=bowtie>`_).

- "H1 and H2 involve different set(s) of handshapes" should be selected if the two hands have at least one different handshape from each other within the sign, that is, if a handshape that appears on one hand never appears on the other hand. This could be because they never have the same handshape (e.g., `SHOW <https://asl-lex.org/visualization/?sign=show>`_), or because they share a handshape at only one part of the sign (e.g., `EVERY-YEAR <https://www.signingsavvy.com/sign/EVERY+YEAR>`_ or `MOUNTAIN <https://www.handspeak.com/word/search/index.php?id=2686>`_). 

.. _signtype_contact_relation:

II. Contact relation
====================

- "H2 maintains contact with H1 throughout the sign" should be selected if the contact is maintained throughout the duration of the sign. This can happen when both hands move together, such as `SHOW <https://asl-lex.org/visualization/?sign=show>`_ or `CAREFUL <https://www.handspeak.com/word/search/index.php?id=328>`_, or when the two hands are stationary in space but involve local movements, as in `BOWTIE <https://asl-lex.org/visualization/?sign=bowtie>`_ or `HOLD HANDS <https://asl-lex.org/visualization/?sign=hold_hands>`_.

- "H1 and H2 do not maintain contact with each other" should be selected if contact is not maintained throughout the sign. This includes signs that have no contact between the hands (e.g., `STRUGGLE <https://asl-lex.org/visualization/?sign=struggle>`_, `BICYCLE <https://asl-lex.org/visualization/?sign=bicycle>`_, `MILK <https://asl-lex.org/visualization/?sign=milk_2>`_) and signs that have momentary contact which is not maintained throughout the sign, such as `CRUCIFY <https://www.handspeak.com/word/search/index.php?id=7840>`_.

.. _signtype_movement_relation: 

III. Movement relation
======================

- "Neither H1 nor H2 moves" should be selected if neither hand is involved in any movement, such as `SICK <https://asl-lex.org/visualization/?sign=sick>`_. [Note that for this example, the sign is ambiguous between having no lexical movement (only transitional movement), as we suggest here, or having a straight perceptual shape movement to reach the target locations. Users should have clear conventions about how to decide between the two.]

- "Only one hand moves" should be selected if only one hand is involved in movement. If selected, further specification is needed as described below about which hand is involved in the movement.

  - Only H1 moves (e.g., `WHEN <https://asl-lex.org/visualization/?sign=when>`_)
  - Only H2 moves (e.g., `SUPPORT <https://www.handspeak.com/word/search/index.php?id=2124>`_)

- "Both hands move" should be selected if both hands are involved in movement. If selected, further specification is needed as described below regarding the movement relations between the two hands. 

  - "H1 and H2 move differently from each other" should be selected if H1 and H2 have at least one movement that is not shared between the two hands. For example, `STALK <https://www.handspeak.com/word/search/index.php?id=4168)as>`_ and `RUN <https://www.handspeak.com/word/search/index.php?id=1859h>`_ are both examples of signs where both hands are involved in the same perceptual shape movement but only H1 has an additional joint-specific movement, which is not shared by H2. This option would also be relevant for a sign where the two hands have completely different movements (e.g., patting the head and rubbing the belly), but we don't know of any lexical examples of this sort.
  - "H1 and H2 move similarly to each other" should be selected if H1 and H2 share the same set of movements, regardless of direction and timing. For example, in `WHEELCHAIR <https://asl-lex.org/visualization/?sign=wheelchair>`_, both hands perform the same joint-specific movement and also happen to have the same direction and timing. In `COMPARE <https://www.handspeak.com/word/search/index.php?id=2563>`_, however, both hands perform the same joint-specific movement, but their orientations / directions of movement alternate in terms of timing. Similarly, in `COMMUNICATION <https://asl-lex.org/visualization/?sign=communication>`_, both hands perform the same perceptual shape movements. In `POPCORN <https://asl-lex.org/visualization/?sign=popcorn>`_, both hands perform the same perceptual shape and joint-specific movements. The alternation or lack thereof is specified below in the :ref:`Movement Timing Relation<signtype_movement_timing_relation>` section; all of these examples would be marked as having the two hands move similarly to each other. 

.. note::
  The following sections on :ref:`Movement Timing Relation<signtype_movement_timing_relation>` and :ref:`Inclusion of a Perceptual Shape<signtype_inclusion_of_perceptual_shape>` should be specified only for signs where H1 and H2 are specified as *‘moving similarly.’* 
      
.. _signtype_movement_timing_relation: 

a. Movement timing relation
~~~~~~~~~~~~~~~~~~~~~~~~~~~
  
  - "Sequential" should be selected if the hands do not move at the same time; when one hand is moving, the other is not. This occurs in signs such as `CRUCIFY <https://www.handspeak.com/word/search/index.php?id=7840>`_ and `HANDS <https://asl-lex.org/visualization/?sign=hands>`_.
      
  - "Simultaneous" should be selected if the hands move at the same time; when one hand is moving (in any way), the other is, too. Further specifications can be made below.
      
    - "Everything is mirrored / in phase" should be selected if location, handshape, and orientation are all mirrored / in phase (synchronized). Signs are considered to be mirrored / in phase when both hands have the same specification at the same time; signs are considered to be not mirrored / out of phase when the hands have opposite specifications at the same time; see :ref:`signing_space_page` for more information. 
            
      Some examples where everything is mirrored / in phase are: `WHEELCHAIR <https://asl-lex.org/visualization/?sign=wheelchair>`_, `CLOUD <https://asl-lex.org/visualization/?sign=cloud_1>`_, and `DECORATE <https://asl-lex.org/visualization/?sign=decorate_2>`_ (all three of which have circular perceptual shape movements) and `BOWTIE <https://asl-lex.org/visualization/?sign=bowtie>`_ (an unhooking joint-specific movement). For straight perceptual movements, the way directions are defined on the horizontal axis may be relevant. If the horizontal axis is defined in terms of relative directions, `FREE <https://www.handspeak.com/word/search/index.php?id=858>`_ would fall in this category (both hands are either contralateral or ipsilateral at the same time). If the horizontal axis is defined in terms of absolute directions, `WINDSHIELD WIPERS <https://www.handspeak.com/word/search/index.php?id=3918>`_ would fall in this category (both hands are either left or right at the same time). 
            
    - "Everything is mirrored / in phase except..." should be selected if at least one component is out of phase. The user can check as many as apply to the sign. 
      
      - "Location" should be selected for signs that are out of phase in terms of location, that is, if the two hands have the opposite specification for location at the same time (e.g., one hand is up while the other is down). For a circle, we consider location to be out of phase if the two hands would reach the top of the circle at *different* times. Some signs that fall under this category are: `POPCORN <https://asl-lex.org/visualization/?sign=popcorn>`_ (one hand is up while the other is down) and `EXPERIMENT <https://asl-lex.org/visualization/?sign=experiment>`_ or `SOCIAL <https://asl-lex.org/visualization/?sign=social>`_ (in both of the latter, the hands reach the top of their circles at different times). If the horizontal axis is defined in terms of relative directions, `WINDSHIELD WIPERS <https://www.handspeak.com/word/search/index.php?id=3918>`_ would fall in this category (one hand is ipsilateral while the other is contralateral). If the horizontal axis is defined in terms of absolute directions, `FREE <https://www.handspeak.com/word/search/index.php?id=858>`_ would fall in this category (one hand is right while the other is left).
                
      - "Handshape" should be selected for signs that are out of phase in terms of handshape, that is, if the two hands have different hand configurations at a given time. Some examples are: `POPCORN <https://asl-lex.org/visualization/?sign=popcorn>`_, `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_ (both signs involve two different hand configurations which are used by each hand at opposite times). 
                
      - "Orientation" should be selected for signs that are out of phase in terms of absolute orientation, that is, if the two hands have different orientations at a given time. Some examples are: `DIE <https://asl-lex.org/visualization/?sign=die>`_ (one palm is facing upward when the other is facing downward), `COMPARE <https://www.handspeak.com/word/search/index.php?id=2563>`_ (one palm faces proximally when the other faces distally), and `PAIN <https://asl-lex.org/visualization/?sign=pain>`_ (again, one palm faces proximally when the other faces distally). Note that this is typically a direct result of joint-specific movements going in different 'directions' at the same time, though such a difference is not intended to be additionally coded in the :ref:`Movement Direction Relation<signtype_movement_direction_relation>` section.

.. _signtype_inclusion_of_perceptual_shape: 

b. Inclusion of perceptual shape movement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- "The sign includes a perceptual shape movement" should be selected if at least one of the movements in the sign is a :ref:`perceptual_shape`. This enables the specification of directions within perceptual shape movements (:ref:`Movement Direction Relation<signtype_movement_direction_relation>`).

.. note::
  We currently allow the section :ref:`Movement Direction Relation<signtype_movement_direction_relation>` to be specified only for signs with a *perceptual shape* component to their movement. It is true that certain joint-specific movements do also have 'directions' to their movements (e.g., twisting can be either pronating or supinating; pivoting can be toward the ulnar or the radial side), but these are not specifically coded as 'directions' in the :ref:`movement`. Instead, these differences are more directly accounted for in the :ref:`Movement Timing Relation<signtype_movement_timing_relation>` section above, because they have direct consequences for whether the *orientations* or *handshapes* of the hands are synchronized / in phase / non-alternating or not (see examples such as `DIE <https://asl-lex.org/visualization/?sign=die>`_, `COMPARE <https://www.handspeak.com/word/search/index.php?id=2563>`_, `PAIN <https://asl-lex.org/visualization/?sign=pain>`_, or `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_ below). However, with perceptual shape movements, the direction and synchronization / phasing are potentially separable, such that both need to be specified. This is especially clear with circular movements, where for example we can have the possible combinations illustrated below. For each one, both the :ref:`Movement Direction Relation<signtype_movement_direction_relation>` and the :ref:`Movement Timing Relation<signtype_movement_timing_relation>` are specified. Note that the directions themselves are often dependent on whether the horizontal axis is treated relatively (ipsilateral / contralateral) or absolutely (right / left and clockwise / counterclockwise). The choices for direction parameters can be set in :ref:`global_settings`; the examples below show both possibilities.

  .. image:: images/signtype_circular_movements.png
   :width: 80%
   :align: center
  
  For completeness, consider the analogous situation for straight movements, which are somewhat more limited:

  .. image:: images/signtype_straight_movements.png
   :width: 80%
   :align: center
  
  Finally, note that another reason for **not** trying to code :ref:`Movement Direction Relation<signtype_movement_direction_relation>` for joint-specific movements is to avoid conflict in signs that have *both* perceptual shape movements and joint-specific movements. These types of movements have different types of consequences for other parameters, such as handshape, orientation, and location, all three of which can be coded separately in the :ref:`Movement Timing Relation<signtype_movement_timing_relation>` section. Currently, however, there is no way to specify a distinction between which movement element is being referred to in the :ref:`Movement Direction Relation<signtype_movement_direction_relation>`, as we assume only perceptual shape movements are coded here.

.. _signtype_movement_direction_relation:

c. Movement direction relation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  
- "H1 and H2 have the same direction of movement" should be selected if the two hands move in either the same absolute direction or relative direction during the perceptual shape movement(s), depending on the choices selected in :ref:`global_settings`. This option would also apply if there are multiple perceptual shape movements and the hands move in the same directions in **all** of them. 
      
     - If the user has chosen relative directions on the horizontal axis, this option would be selected for signs where both hands move ipsilaterally or contralaterally, such as `CRUCIFY <https://www.handspeak.com/word/search/index.php?id=7840>`_ (each hand moves contralaterally to touch the opposite palm) or `FREE <https://www.handspeak.com/word/search/index.php?id=858>`_ (each hand moves ipsilaterally, separating away from each other), or both hands circle in the same direction, as in `CLOUD <https://asl-lex.org/visualization/?sign=cloud_1>`_ and `EXPERIMENT <https://asl-lex.org/visualization/?sign=experiment>`_ (in both signs, from the *top* of each hand's circle, both hands start the circle in a contralateral direction).  Note that other minimal differences among these signs are covered by the :ref:`Movement Timing Relation<signtype_movement_timing_relation>` section above.

     - If the user has chosen absolute directions on the horizontal axis, this option would be selected for signs where both hands move rightward and leftward together, such as `WINDSHIELD WIPERS <https://www.handspeak.com/word/search/index.php?id=3918>`_ or both hands move clockwise/counterclockwise, such as `SOCIAL <https://asl-lex.org/visualization/?sign=social>`_ or `DECORATE <https://asl-lex.org/visualization/?sign=decorate_2>`_. Note that perspective choices for definitions of clockwise / counterclockwise can also be specified in :ref:`global_settings`. Again, other minimal differences among these signs are covered by the :ref:`Movement Timing Relation<signtype_movement_timing_relation>` section above.
      
     - Finally, this option would also apply in cases that do not include the horizontal axis, like `BICYCLE <https://asl-lex.org/visualization/?sign=bicycle>`_ or `WHEELCHAIR <https://asl-lex.org/visualization/?sign=wheelchair>`_, where both hands are moving clockwise on the sagittal plane (though again, they differ according to their :ref:`Movement Timing Relation<signtype_movement_timing_relation>`).
 
- "H1 and H2 have different directions of movement" should be selected if the two hands move in either different absolute directions or different relative directions during the perceptual shape movement(s), depending on the choices selected in :ref:`global_settings`. This option would also apply if there are multiple perceptual shape movements and the hands move in different directions in at least one of them. 
      
     - If the user has chosen relative directions on the horizontal axis, this option would be selected for signs where one hand moves ipsilaterally and one hand moves contralaterally, as in `SOCIAL <https://asl-lex.org/visualization/?sign=social>`_ (from the top of the circle, the upper hand moves contralaterally and the lower hand moves ipsilaterally), `DECORATE <https://asl-lex.org/visualization/?sign=decorate_2>`_ (from the top of the circle, the upper hand moves contralaterally and the lower hand moves ipsilaterally), and `WINDSHIELD WIPERS <https://www.handspeak.com/word/search/index.php?id=3918>`_ (when one hand is moving ipsilaterally, the other is moving contralaterally and vice versa). Again, other minimal differences among these signs are covered by the :ref:`Movement Timing Relation<signtype_movement_timing_relation>` section above.
      
     - If the user has chosen absolute directions on the horizontal axis, this option would be selected for signs where one hand moves right and one hand moves left, such as `CRUCIFY <https://www.handspeak.com/word/search/index.php?id=7840>`_ (the right hand moves to the left; the left hand moves to the right) or `FREE <https://www.handspeak.com/word/search/index.php?id=858>`_ (the right hand moves rightward and the left hand moves leftward, separating away from each other), or the hands circle in the opposite direction, as in `CLOUD <https://asl-lex.org/visualization/?sign=cloud_1>`_ and `EXPERIMENT <https://asl-lex.org/visualization/?sign=experiment>`_ (in both signs, the right hand moves counterclockwise but the left hand moves clockwise).  Again, other minimal differences among these signs are covered by the :ref:`Movement Timing Relation<signtype_movement_timing_relation>` section above.
      
     - Finally, this option would also apply in cases that do not include the horizontal axis, such as `COMMUNICATION <https://asl-lex.org/visualization/?sign=communication>`_ (when one hand is moving distally, the other is moving proximally and vice versa).

**[Needs to be updated with new sign type layout]**
Example coding for the sign `COMPARE <https://www.handspeak.com/word/search/index.php?id=2563>`_:

   .. image:: images/signtype_COMPARE.png
      :width: 80%
      :align: center


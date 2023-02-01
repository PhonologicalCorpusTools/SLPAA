.. todo::
  fill out bilateral symmetry
      - add glossary item
  fill out connectedness
      - add glossary item
  update the screenshot of the selection window
      - wait until bilateral symmetry and connectedness are implemented
  check over movement direction relation
  check over what's mentioned in 'to mention in docs' for sign type

.. _sign_type_module:

*********
Sign Type 
*********

This :ref:`module` is used to identify the overarching ‘kind’ of sign by selecting specifications for the behaviours of each hand (H1 & H2) both separately and in relation to each other, if applicable. 

This module is atypical in that only one :ref:`instance` can be called for each sign, and the information coded within it applies to the sign as a whole. For more discussion on the use of modules in SLP-AA to encode information about signs, see :ref:`modularity`.

.. _signtype_one_hand: 

1. Number of hands: 1 hand
``````````````````````````

Select this if the sign involves only one hand. 

* "The hand moves" should be selected if the hand is involved in either a :ref:`perceptual_shape` (e.g., `NORTH <https://asl-lex.org/visualization/?sign=north>`_), a :ref:`joint_specific_movement` (e.g., `APPLE <https://asl-lex.org/visualization/?sign=apple>`_), or a :ref:`handshape change` (e.g., `STYLE <https://www.handspeak.com/word/search/index.php?id=4174>`_, `HIGH SCHOOL <https://asl-lex.org/visualization/?sign=high_school>`_).

* "The hand does not move" should be selected if the hand is not involved in any movement, such as `MISS <https://asl-lex.org/visualization/?sign=miss>`_ or `ONE <https://www.handspeak.com/word/search/index.php?id=1554>`_.

.. note::
    **How to address a stationary H2 involved in a sign**
    
    If the forearm, elbow, or wrist of the H2 is involved in a sign where H2 does not participate in movement, there are several ways this could be coded in SLP-AA. Users should define their own conventions for consistency. Some options are:
    
    # The user can decide to specify the sign as one-handed in Sign Type and still include the use of H2 in the specifications of contact and location, or
    # The user can specify the sign as one-handed in Sign Type and still select "forearm involved" in the hand configuration module for H1, or 
    # The user can specify the sign as two-handed, also specifying that "only H1 moves". 
    
    For example, the sign `CRACKER <https://asl-lex.org/visualization/?sign=cracker>`_ could be coded as one-handed, with H1 making contact to H2 at the elbow; one-handed, with "forearm involved" selected in the hand configuration module; or two-handed, with only H1 specified as moving. The sign `TABLE <https://asl-lex.org/visualization/?sign=table>`_ could be coded with the same basic options, with the additional possibility of coding the contact that H2 makes with the elbow of H1 in a separate location module and contact module.

.. _signtype_two_hands:

2. Number of hands: 2 hands
```````````````````````````

Select this if both hands are involved in the sign. See the note above if only the forearm, wrist, or elbow of the second hand is involved. 

.. _signtype_handshape_relation:

I. Handshape relation
=====================

* "H1 and H2 involve the same set(s) of handshapes" should be selected if all the handshapes used at any point during the sign are shared between both hands. This can be because the handshapes never change (e.g., `BICYCLE <https://asl-lex.org/visualization/?sign=bicycle>`_), or because the handshapes change but involve the same shapes on both hands. In the latter case, the handshapes can alternate (e.g., `MILK <https://asl-lex.org/visualization/?sign=milk_2>`_) or change at the same time as each other (e.g., `BOWTIE <https://asl-lex.org/visualization/?sign=bowtie>`_).

* "H1 and H2 involve different set(s) of handshapes" should be selected if the two hands have at least one different handshape from each other within the sign, that is, if a handshape that appears on one hand never appears on the other hand. This could be because they never have the same handshape (e.g., `SHOW <https://asl-lex.org/visualization/?sign=show>`_), or because they share a handshape at only one part of the sign (e.g., `EVERY-YEAR <https://www.signingsavvy.com/sign/EVERY+YEAR>`_ or `MOUNTAIN <https://www.handspeak.com/word/search/index.php?id=2686>`_).

.. note::
    **Handshape relation and hand configuration phasing**
    
    When the option for "H1 and H2 involve different set(s) of handshapes" is selected, the program automatically makes the hand configuration phasing option inaccessible in the :ref:`Movement Timing Relation<signtype_movement_timing_relation>` section.

.. _signtype_contact_relation:

II. Contact relation
====================

* "H2 maintains contact with H1 throughout the sign" should be selected if the contact is maintained throughout the duration of the sign. This can happen when both hands move together, such as `SHOW <https://asl-lex.org/visualization/?sign=show>`_ or `CAREFUL <https://www.handspeak.com/word/search/index.php?id=328>`_, or when the two hands are stationary in space but involve local movements, as in `BOWTIE <https://asl-lex.org/visualization/?sign=bowtie>`_ or `HOLD HANDS <https://asl-lex.org/visualization/?sign=hold_hands>`_.

* "H1 and H2 do not maintain contact with each other" should be selected if contact is not maintained throughout the sign. This includes signs that have no contact between the hands (e.g., `STRUGGLE <https://asl-lex.org/visualization/?sign=struggle>`_, `BICYCLE <https://asl-lex.org/visualization/?sign=bicycle>`_, `MILK <https://asl-lex.org/visualization/?sign=milk_2>`_) and signs that have momentary contact which is not maintained throughout the sign, such as `CRUCIFY <https://www.handspeak.com/word/search/index.php?id=7840>`_.

.. _bilateral_symmetry_relation:

III. Bilateral symmetry relation
================================

(new section)

.. comment::
    due to the natural bilateral symmetry of the human body. (It's possible that similar ambiguity could exist in either the vertical or sagittal axis in some cases, but we focus only on the horizontal axis since it has the benefit of a clear axis midpoint and grounding in physiology.)

.. _connectedness_relation:

IV. Connectedness relation
==========================

(new section)

.. _signtype_movement_relation: 

V. Movement relation
====================

* "Neither H1 nor H2 moves" should be selected if neither hand is involved in any movement, such as `SICK <https://asl-lex.org/visualization/?sign=sick>`_. [Note that for this example, the sign is ambiguous between having no lexical movement (only transitional movement), as we suggest here, or having a straight perceptual shape movement to reach the target locations. Users should have clear conventions about how to decide between the two.]

* "Only one hand moves" should be selected if only one hand is involved in movement. If selected, further specification is needed as described below about which hand is involved in the movement.

    * Only H1 moves (e.g., `WHEN <https://asl-lex.org/visualization/?sign=when>`_)
    * Only H2 moves (e.g., `SUPPORT <https://www.handspeak.com/word/search/index.php?id=2124>`_)

* "Both hands move" should be selected if both hands are involved in movement. If selected, further specification is needed as described below regarding the movement relations between the two hands. 

    * "H1 and H2 move differently from each other" should be selected if H1 and H2 have at least one movement that is not shared between the two hands. For example, `STALK <https://www.handspeak.com/word/search/index.php?id=4168)as>`_ and `RUN <https://www.handspeak.com/word/search/index.php?id=1859h>`_ are both examples of signs where both hands are involved in the same perceptual shape movement but only H1 has an additional joint-specific movement, which is not shared by H2. This option would also be relevant for a sign where the two hands have completely different movements (e.g., patting the head and rubbing the belly), but we don't know of any lexical examples of this sort.
    
    * "H1 and H2 move similarly to each other" should be selected if H1 and H2 share the same set of movements, regardless of direction and timing. For example, in `WHEELCHAIR <https://asl-lex.org/visualization/?sign=wheelchair>`_, both hands perform the same joint-specific movement and also happen to have the same direction and timing. In `COMPARE <https://www.handspeak.com/word/search/index.php?id=2563>`_, however, both hands perform the same joint-specific movement, but their orientations / directions of movement alternate in terms of timing. Similarly, in `COMMUNICATION <https://asl-lex.org/visualization/?sign=communication>`_, both hands perform the same perceptual shape movements. In `POPCORN <https://asl-lex.org/visualization/?sign=popcorn>`_, both hands perform the same perceptual shape and joint-specific movements. The alternation or lack thereof is specified below in the :ref:`Movement Timing Relation<signtype_movement_timing_relation>` section; all of these examples would be marked as having the two hands move similarly to each other. 

.. note::
  The following sections on :ref:`Movement Timing Relation<signtype_movement_timing_relation>` and :ref:`Inclusion of a Perceptual Shape<signtype_inclusion_of_perceptual_shape>` should be specified only for signs where H1 and H2 are specified as *‘moving similarly.’* 
      
.. _signtype_movement_timing_relation: 

a. Movement timing relation
~~~~~~~~~~~~~~~~~~~~~~~~~~~
  
* "Sequential" should be selected if the hands do not move at the same time; when one hand is moving, the other is not. This occurs in signs such as `CRUCIFY <https://www.handspeak.com/word/search/index.php?id=7840>`_ and `HANDS <https://asl-lex.org/visualization/?sign=hands>`_.
      
* "Simultaneous" should be selected if the hands move at the same time; when one hand is moving (in any way), the other is, too. Further specifications can be made below.
      
    * "Everything is in phase" should be selected if all parameters (location, handshape, and orientation) are in phase for this sign. 

Signs are considered to be **in phase** for a given parameter when both hands have the same specification for that parameter at the same time; likewise, signs are considered to be **out of phase** for a given parameter when the hands have opposite specifications for that parameter at the same time.
            
Some examples where everything is in phase are `WHEELCHAIR <https://asl-lex.org/visualization/?sign=wheelchair>`_ and `BOWTIE <https://asl-lex.org/visualization/?sign=bowtie>`_.

.. note::
    **Phasing and symmetry**
    
    Phasing becomes more ambiguous in the horizontal axis due to the complication of symmetry.
    
    Depending on definition, it could be equally valid that both hands located on the signer's dominant or subordinate side have the "same" location, or that both hands located on their own ipsilateral or contralateral side (relative to the midline of the body) have the "same" location. In order to remain explicit as to what this means and allow for precise analysis, SLP-AA allows for users to select whether the horizontal axis is defined for each module with **absolute** (toward H1 or H2 side) or **relative** (ipsi-contra) directions. For the absolute interpretation, the hands located together on the signer's dominant or subordinate side (such as `SINCE <https://asl-lex.org/visualization/?sign=since>`_) have the "same" location, and the hands mirrored across the midline (such as `ROW <https://asl-lex.org/visualization/?sign=row>`_) have different locations. For the relative interpretation, the hands mirrored across the midline have the "same" direction and the hands located on the signer's dominant or subordinate side have different locations.
    
    This also means that the interpretation of phasing for both location and orientation may depend on the user's preferences for horizontal axis directions. If the horizontal axis is defined in terms of relative directions, `FREE <https://www.handspeak.com/word/search/index.php?id=858>`_ would be considered "in phase" for location, as both hands have the **same specification** (contralateral or ipsilateral) at the same time. If the horizontal axis is defined in terms of absolute directions, `WINDSHIELD WIPERS <https://www.handspeak.com/word/search/index.php?id=3918>`_ would be considered "in phase" for location, as both hands have the **same specification** (H1 or H2 side) at the same time. See the illustration below for more information.
    
    .. image:: images/signtype_straight_movements.png
       :width: 80%
       :align: center
    
    The horizontal axis options can be set for each module independently. For more information, see :ref:`global_settings`.

* "Everything is in phase except..." should be selected if at least one component is out of phase. The user can check as many parameters as apply to the sign. 
      
    * "Location" should be selected for signs that are out of phase in terms of location, that is, if the two hands have the opposite specification for location at the same time (e.g., one hand is up while the other is down). For a circle, we consider location to be out of phase if the two hands would reach the :ref:`top of the circle<circular_directions>` at *different* times. Some signs that fall under this category are: `POPCORN <https://asl-lex.org/visualization/?sign=popcorn>`_ (one hand is up while the other is down) and `EXPERIMENT <https://asl-lex.org/visualization/?sign=experiment>`_ or `SOCIAL <https://asl-lex.org/visualization/?sign=social>`_ (in both of the latter, the hands reach the top of their circles at different times). If the horizontal axis is defined in terms of relative directions, `WINDSHIELD WIPERS <https://www.handspeak.com/word/search/index.php?id=3918>`_ would fall in this category (one hand is ipsilateral while the other is contralateral). If the horizontal axis is defined in terms of absolute directions, `FREE <https://www.handspeak.com/word/search/index.php?id=858>`_ would fall in this category (one hand is right while the other is left). See illustration above. 
    
    * "Handshape" should be selected for signs that are out of phase in terms of handshape. That is, the two hands have different hand configurations at a given time. Some examples are: `POPCORN <https://asl-lex.org/visualization/?sign=popcorn>`_, `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_ (both signs involve two different hand configurations which are used by each hand at opposite times). Note that this option is only applicable as long as both hands use the same set of hand configurations throughout the production of the sign.
    
    * "Orientation" should be selected for signs that are out of phase in terms of absolute orientation, that is, if the two hands have different orientations at a given time. Some examples are: `DIE <https://asl-lex.org/visualization/?sign=die>`_ (one palm is facing upward when the other is facing downward), `COMPARE <https://www.handspeak.com/word/search/index.php?id=2563>`_ (one palm faces proximally when the other faces distally), and `PAIN <https://asl-lex.org/visualization/?sign=pain>`_ (again, one palm faces proximally when the other faces distally). Note that this is typically a direct result of joint-specific movements going in different 'directions' at the same time, though such a difference is not intended to be additionally coded in the :ref:`Movement Direction Relation<signtype_movement_direction_relation>` section.

Note that if an element has been selected as being 'out of phase' in the sign type module, the system will expect there to be a corresponding movement module in which the movements of the two hands are the same, but out of phase with each other, and will prompt the user to include such a module. See more in the :ref:`movement_module` section. This allows the user to code the movements in signs like both `FREE <https://www.handspeak.com/word/search/index.php?id=858>`_ and `WINDSHIELD WIPERS <https://www.handspeak.com/word/search/index.php?id=3918>`_ using a single movement module for both hands (to capture the fact that the basic movements of the two hands are the same) while still specifying that the result is a location (or handshape, or orientation) that is out of phase.

.. _signtype_inclusion_of_perceptual_shape: 

b. Inclusion of non-straight perceptual shape movement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* "The sign includes a non-straight perceptual shape movement" should be selected if at least one of the movements in the sign is a :ref:`perceptual_shape` that is not a straight line (e.g., it's a circle, arc, zigzag, or loop). This enables the specification of circular directions (e.g., clockwise, counterclockwise) within perceptual shape movements (:ref:`Movement Direction Relation<signtype_movement_direction_relation>`).

.. note::
    **Note on the restriction to perceptual shape movements other than 'straight'**
    
    We currently allow the section :ref:`Movement Direction Relation<signtype_movement_direction_relation>` to be specified only for signs with a *non-straight perceptual shape* component to their movement. 
    
    It is true that straight perceptual movements and certain joint-specific movements do also have 'directions' to their movements (e.g., a straight movement can be up or down; twisting can be either pronating or supinating; pivoting can be toward the ulnar or the radial side). However, these differences are more directly accounted for in the :ref:`Movement Timing Relation<signtype_movement_timing_relation>` section above, because they have direct consequences for whether or not the *locations* (for straight movements), *orientations* (for joint-specific movements like twisting), or *handshapes* (for joint-specific movements like flexion) of the hands are in phase. See examples such as `FREE <https://www.handspeak.com/word/search/index.php?id=858>`_, `WINDSHIELD WIPERS <https://www.handspeak.com/word/search/index.php?id=3918>`_, `DIE <https://asl-lex.org/visualization/?sign=die>`_, `COMPARE <https://www.handspeak.com/word/search/index.php?id=2563>`_, `PAIN <https://asl-lex.org/visualization/?sign=pain>`_, or `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_ below. 
    
    However, with non-straight perceptual shape movements, the direction and phasing of the movements of each hand are potentially separable, such that both need to be specified to accurately capture the descriptions of hand timing and direction. This is especially clear with circular movements, where for example we can have the full set of possible combinations illustrated below. For each one, both the :ref:`Movement Direction Relation<signtype_movement_direction_relation>` and the :ref:`Movement Timing Relation<signtype_movement_timing_relation>` are specified. Note that the directions themselves are often dependent on whether the horizontal axis is treated relatively (ipsilateral/contralateral) or absolutely (toward H1/H2 and clockwise/counterclockwise). The choices for the direction parameters can be set for Movement in the :ref:`global_settings`; the examples below show both possibilities.
    
    .. image:: images/signtype_circular_movements.png
        :width: 80%
        :align: center
       
    Keep in mind that for circles, phasing for location is defined only based on whether or not the hands reach the :ref:`top of the circle<circular_directions>` at the same moment, regardless of whether or not the hands are interpreted to be moving in the same direction. Notice in the illustration above that phasing for location for these (circle perceptual shape) signs is independent of the choice for horizontal axis directions.
    
    Finally, note that another reason for **not** trying to code :ref:`Movement Direction Relation<signtype_movement_direction_relation>` for non-circular movement shapes is to avoid conflict in signs that have *both* perceptual shape movements and joint-specific movements. These types of movements have different types of consequences for other parameters, such as handshape, orientation, and location, all three of which can be coded separately in the :ref:`Movement Timing Relation<signtype_movement_timing_relation>` section. Currently, however, there is no way to specify a distinction between which movement element is being referenced in the :ref:`Movement Direction Relation<signtype_movement_direction_relation>`, as we assume only perceptual shape movements are coded here.

.. _signtype_movement_direction_relation:

c. Movement direction relation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  
* "H1 and H2 have the same direction of movement" should be selected if the two hands move in either the same absolute direction or relative direction during the non-straight perceptual shape movement, depending on the choices selected by the user in :ref:`global_settings`. If there are multiple perceptual shape movements in one sign, this option would only apply if the hands move in the same directions for **all** of them. 
      
     * If the user has chosen relative directions on the horizontal axis, this option would be selected for signs where both hands circle in the same direction, as in `CLOUD <https://asl-lex.org/visualization/?sign=cloud_1>`_ and `EXPERIMENT <https://asl-lex.org/visualization/?sign=experiment>`_ (in both signs, both hands move in a contralateral direction from the :ref:`top of the circle<circular_directions>`).  Note that other minimal differences among these signs are covered by the :ref:`Movement Timing Relation<signtype_movement_timing_relation>` section above.

     * If the user has chosen absolute directions on the horizontal axis, this option would be selected for signs where both hands move clockwise/counterclockwise, such as `SOCIAL <https://asl-lex.org/visualization/?sign=social>`_ or `DECORATE <https://asl-lex.org/visualization/?sign=decorate_2>`_. Note that perspective choices for definitions of clockwise / counterclockwise can also be specified in :ref:`global_settings`. Again, other minimal differences among these signs are covered by the :ref:`Movement Timing Relation<signtype_movement_timing_relation>` section above.
      
     * Finally, this option would also apply in cases that do not include the horizontal axis, like `BICYCLE <https://asl-lex.org/visualization/?sign=bicycle>`_ or `WHEELCHAIR <https://asl-lex.org/visualization/?sign=wheelchair>`_, where both hands are moving clockwise on the sagittal plane (though again, they differ according to their :ref:`Movement Timing Relation<signtype_movement_timing_relation>`).
 
* "H1 and H2 have different directions of movement" should be selected if the two hands move in either different absolute directions or different relative directions during the non-straight perceptual shape movement(s), depending on the choices selected in :ref:`global_settings`. This option would also apply if there are multiple perceptual shape movements and the hands move in different directions in at least one of them.
      
     * If the user has chosen relative directions on the horizontal axis, this option would be selected for signs where one hand moves ipsilaterally and one hand moves contralaterally, as in `SOCIAL <https://asl-lex.org/visualization/?sign=social>`_ (from the top of the circle, the upper hand moves contralaterally and the lower hand moves ipsilaterally) or `DECORATE <https://asl-lex.org/visualization/?sign=decorate_2>`_ (from the top of the circle, the upper hand moves contralaterally and the lower hand moves ipsilaterally). Again, other minimal differences among these signs are covered by the :ref:`Movement Timing Relation<signtype_movement_timing_relation>` section above.
      
     * If the user has chosen absolute directions on the horizontal axis, this option would be selected for signs where the hands circle in the opposite direction, as in `CLOUD <https://asl-lex.org/visualization/?sign=cloud_1>`_ and `EXPERIMENT <https://asl-lex.org/visualization/?sign=experiment>`_ (in both signs, the right hand moves counterclockwise but the left hand moves clockwise).  Again, other minimal differences among these signs are covered by the :ref:`Movement Timing Relation<signtype_movement_timing_relation>` section above.
      
     * Finally, this option would also apply in cases that do not include the horizontal axis. This would involve the two hands moving in circles in opposite directions on the sagittal plane. We do not know of any such cases, as they are biomechanically difficult. 

**[Needs to be updated with new sign type layout]**
Example coding for the sign `COMPARE <https://www.handspeak.com/word/search/index.php?id=2563>`_:

   .. image:: images/signtype_COMPARE.png
      :width: 80%
      :align: center

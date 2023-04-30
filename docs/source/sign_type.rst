.. todo::
    slightly altered screenshot with sequential/simultaneous

.. _sign_type:

*********
Sign Type
*********

This selection window is used to identify the highest-category sign characteristics by specifying the behaviours of each hand (H1 & H2) both separately and in relation to each other, if applicable. The information coded in this window applies to the sign as a whole, similarly to :ref:`sign_level_info`.

.. _signtype_one_hand: 

1. Number of hands: 1 hand
``````````````````````````

Select this if the sign involves only one hand. 

* "The hand moves" should be selected if the hand is involved in either a :ref:`perceptual_shape` movement (e.g., `NORTH <https://asl-lex.org/visualization/?sign=north>`_), a :ref:`joint_specific_movement` (e.g., `APPLE <https://asl-lex.org/visualization/?sign=apple>`_), or a :ref:`handshape_change` (e.g., `STYLE <https://www.handspeak.com/word/search/index.php?id=4174>`_, `HIGH SCHOOL <https://asl-lex.org/visualization/?sign=high_school>`_).

* "The hand does not move" should be selected if the hand is not involved in any movement, such as `MISS <https://asl-lex.org/visualization/?sign=miss>`_ or `ONE <https://www.handspeak.com/word/search/index.php?id=1554>`_.

.. note::
    **How to address a stationary H2 involved in a sign**
    
    If the forearm, elbow, or wrist of the H2 is involved in a sign where H2 does not participate in movement, there are several ways this could be coded in SLP-AA. Users should decide on their own conventions for consistency. Some options are:
    
        #. The user can specify the sign as one-handed and still include the use of H2 in specifications of the :ref:`location_module` and the :ref:`contact_module`, or
        #. The user can specify the sign as one-handed and still select "forearm involved" in the :ref:`hand_configuration_module` for H1, or 
        #. The user can specify the sign as two-handed, also specifying that "only H1 moves".
    
    For example, the sign `CRACKER <https://asl-lex.org/visualization/?sign=cracker>`_ could be coded as one-handed, with H1 making contact to H2 at the elbow; one-handed, with "forearm involved" selected using the :ref:`hand_configuration_module`; or two-handed, with only H1 specified as moving. The sign `TABLE <https://asl-lex.org/visualization/?sign=table>`_ could be coded with the same basic options, with the additional possibility of coding the contact that H2 makes with the elbow of H1 in linked instances of the :ref:`location_module` and the :ref:`contact_module`.

.. _signtype_two_hands:

2. Number of hands: 2 hands
```````````````````````````

Select this if both hands are involved in the sign. See the note above if only the forearm, wrist, or elbow of the second hand is involved. 

.. _signtype_handshape_relation:

I. Hand configuration relation
==============================

* "H1 and H2 use the same set(s) of hand configurations" should be selected if all the hand configurations used at any point during the sign are shared between both hands. This can be because the hand configurations never change (e.g., `BICYCLE <https://asl-lex.org/visualization/?sign=bicycle>`_), or because the hand configurations change but involve the same configurations on both hands (e.g., `POPCORN <https://asl-lex.org/visualization/?sign=popcorn>`_). In the latter case, the hand configurations can alternate (e.g., `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_) or change at the same time as each other (e.g., `BOWTIE <https://asl-lex.org/visualization/?sign=bowtie>`_).

* "H1 and H2 use different set(s) of hand configurations" should be selected if the two hands have at least one different hand configuration from each other within the sign; that is, a hand configuration that appears on one hand never appears on the other hand. This could be because they never have the same hand configuration, such as `SHOW <https://asl-lex.org/visualization/?sign=show>`_, or because they share a hand configuration for only part of the sign, such as `EVERY YEAR <https://www.signingsavvy.com/sign/EVERY+YEAR>`_ or `MOUNTAIN <https://www.handspeak.com/word/search/index.php?id=2686>`_.

.. _signtype_contact_relation:

II. Contact relation
====================

* "H1 and H2 maintain contact throughout sign" should be selected if the contact is maintained between both hands throughout the duration of the sign. This can happen when both hands move together, such as `SHOW <https://asl-lex.org/visualization/?sign=show>`_ or `CAREFUL <https://www.handspeak.com/word/search/index.php?id=328>`_, or when the two hands are stationary in space but involve :ref:`joint_specific_movement`, as in `BOWTIE <https://asl-lex.org/visualization/?sign=bowtie>`_ or `HOLD HANDS <https://asl-lex.org/visualization/?sign=hold_hands>`_.

* "H1 and H2 do not maintain contact" should be selected if contact is not maintained throughout the sign. This includes signs that have no contact between the hands (e.g., `STRUGGLE <https://asl-lex.org/visualization/?sign=struggle>`_, `BICYCLE <https://asl-lex.org/visualization/?sign=bicycle>`_, or `MILK_2 <https://asl-lex.org/visualization/?sign=milk_2>`_) and signs that have momentary contact which is not maintained throughout the sign, such as `CRUCIFY <https://www.handspeak.com/word/search/index.php?id=7840>`_.

.. _bilateral_symmetry_relation:

III. Bilateral symmetry relation
================================

* "H1 and H2 are bilaterally symmetric" should be selected if the hands are mirrored across the midline of the body in all of hand configuration, orientation, movement, location, and contact for the duration of the sign. That is, every aspect of one hand is identical across the midline of the body for the other hand at each moment (e.g. `STARBUCKS <https://asl-lex.org/visualization/?sign=starbucks>`_, `SHIRT_2 <https://asl-lex.org/visualization/?sign=shirt_2>`_, or `WHEELCHAIR <https://asl-lex.org/visualization/?sign=wheelchair>`_).

* "H1 and H2 are not bilaterally symmetric" should be selected if any aspect of the sign for one hand is not mirrored for the other hand at any moment. This could be because the set of movements are not shared between the two hands (e.g. `STALK <https://www.handspeak.com/word/4168/>`_), the set of hand configurations are not shared between the two hands (e.g. `SHOW <https://asl-lex.org/visualization/?sign=show>`_), the hands move in different **relative** directions (e.g. `WINDSHIELD WIPERS <https://www.handspeak.com/word/3918/>`_, see :ref:`Symmetry<symmetry_section>` for more information), the hands move out of phase (e.g. `THEATER <https://asl-lex.org/visualization/?sign=theater>`_), the hands are not positioned horizontally to each other (e.g. `FOLLOW_1 <https://asl-lex.org/visualization/?sign=follow_1>`_, `GET <https://asl-lex.org/visualization/?sign=get>`_, or `HIPPO <https://asl-lex.org/visualization/?sign=hippo>`_), one part of the duration of the sign is not symmetric in some way (e.g. `SIGN_LANGUAGE <https://asl-lex.org/visualization/?sign=sign_language>`_), and so on.

.. note::
    **Incompatible specifications in Sign Type**
    
    There are many ways for a sign to fail to be bilaterally symmetric that also overlap with other selections in Sign Type. It is impossible for a selection of "H1 and H2 are bilaterally symmetric" to combine with any of: 
    
        * "H1 and H2 use different set(s) of hand configurations"
        * "Only 1 hand moves"
        * "H1 and H2 move differently"
        * "Sequential" movements

.. _signtype_movement_relation: 

IV. Movement relation
=====================

* "Neither hand moves" should be selected if neither hand is involved in any movement, such as `SICK <https://asl-lex.org/visualization/?sign=sick>`_. Note that for this example, the sign is ambiguous between having no lexical movement (only transitional movement), as we suggest here, or using a :ref:`perceptual_shape` movement to reach the target locations. Users should have clear conventions about how to decide between the two.

* "Only 1 hand moves" should be selected if only one hand is involved in movement. If selected, further specification is needed as described below about which hand is involved in the movement.

    * Only H1 moves (e.g., `WHEN <https://asl-lex.org/visualization/?sign=when>`_)
    * Only H2 moves (e.g., `SUPPORT <https://www.handspeak.com/word/search/index.php?id=2124>`_)

* "Both hands move" should be selected if both hands are involved in movement. If selected, further specification is needed as described below regarding the movement relations between the two hands. 

    * "H1 and H2 move differently" should be selected if H1 and H2 have at least one movement that is not shared between the two hands. That is, there is at least one instance of the :ref:`movement_module` that cannot be shared between both hands. `STALK <https://www.handspeak.com/word/search/index.php?id=4168)as>`_ and `RUN <https://www.handspeak.com/word/search/index.php?id=1859h>`_ are both examples of signs where both hands are involved in the same :ref:`perceptual_shape` movement, but only H1 has an additional :ref:`joint_specific_movement` which is not shared by H2. This option would also be relevant for a sign where the two hands have completely different movements (e.g., patting the head and rubbing the belly), but we don't know of any lexical examples of this sort.
    
    * "H1 and H2 move similarly" should be selected if H1 and H2 share the same set of movements (and would be able to be described entirely in shared instances of the :ref:`movement_module`), regardless of direction and timing. This applies to the highest category of movement within its :ref:`Movement type<movement_type_entry>` category, even if more refined details are different for each hand's movement. For example, both hands perform the same basic joint-specific movement in `WHEELCHAIR <https://asl-lex.org/visualization/?sign=wheelchair>`_ and `COMPARE <https://www.handspeak.com/word/search/index.php?id=2563>`_, even if their orientations or directions of movement may or may not be the same. Similarly, in `COMMUNICATION <https://asl-lex.org/visualization/?sign=communication>`_, both hands perform the same perceptual shape movements. In `POPCORN <https://asl-lex.org/visualization/?sign=popcorn>`_, both hands perform the same perceptual shape and joint-specific movements. All of these are signs in which both hands move similarly.
    
        * "Sequential" should be selected if the hands do not move at the same time at any point in the sign. When one hand is moving, the other is not. This occurs in signs such as `CRUCIFY <https://www.handspeak.com/word/search/index.php?id=7840>`_ and `HANDS <https://asl-lex.org/visualization/?sign=hands>`_.
         
        * "Simultaneous" should be selected if the hands move at the same time(s) throughout the production of the sign. When one hand is moving (in any way), the other is also moving.

Example coding for the sign `COMPARE <https://www.handspeak.com/word/search/index.php?id=2563>`_:

**(update with sequential/simultaneous)**

   .. image:: images/signtype_COMPARE.png
      :width: 70%
      :align: center

.. _sign_type_module:

***********
Sign Type
***********

This module is where users identify the overarching ‘kind’ of sign by selecting specifications for the behaviours of each hand (H1 & H2) in relation to each other. 


I.II. =====
abc ~~~~~~~~~

.. _signtype_number_hands: 

Number of hands
`````````````````

1. 1 hand
=========
Select this if the sign only involved one hand, regardless of movement, contact etc. 

- "The hand moves" is selected if the hand is involved in either a perceptual shape [`NORTH <https://asl-lex.org/visualization/?sign=north>`_] or a joint-specific movement [`APPLE <https://asl-lex.org/visualization/?sign=apple>`_] **also includes finger spelled signs?** if yes, give example. 

- "The hand does not move" is selected if the hand is not nvolved in any movement, such as [`ONE <https://www.handspeak.com/word/search/index.php?id=1554>`_].

2. 2 hands
=========
Select this if both **hands** are involved in the sign in some way. **(add a note about what to do if the ARM is involved, such as WHALE, CRACKER, TRASH, and even TIME, where the wrist is involved. Signs where the forearm is parallel to the ground, this selection will be available in PDHS module)**

I. Handshape relation
~~~~~~~~~~~~~~~~~~~~~~

- "H1 and H2 involve the same set(s) of handshapes" should be selected if the sets of handshapes used at any point during the sign are the same on both hands. This can be because the shapes never change (e.g., `BICYCLE <https://asl-lex.org/visualization/?sign=bicycle>`_), because the shapes alternate (e.g., `MILK <https://asl-lex.org/visualization/?sign=milk_2>`_), or because the shapes change at the same time as each other (e.g., `BOWTIE <https://asl-lex.org/visualization/?sign=bowtie>`_).


- "H1 and H2 involve different set(s) of handshapes" should be selected if the two hands have different handshapes from each other in at least one part of the sign. This could be because they never have the same handshape (e.g., `SHOW <https://asl-lex.org/visualization/?sign=show>`_), or because they share a handshape at only one part of the sign (e.g., `EVERY-YEAR <https://www.signingsavvy.com/sign/EVERY+YEAR>`_ or `MOUNTAIN <https://www.handspeak.com/word/search/index.php?id=2686>`_). 



II. Contact relation
~~~~~~~~~~~~~~~~~~~~~~
- "H2 maintains contact with H1 throughout the sign" should be selected if the contact is maintained throughout the duration of the sign, such as [`SHOW <https://asl-lex.org/visualization/?sign=show>`_, `CAREFUL <https://www.handspeak.com/word/search/index.php?id=328>`_, `BOWTIE <https://asl-lex.org/visualization/?sign=bowtie>`_, `HOLD HANDS <https://asl-lex.org/visualization/?sign=hold_hands>`_]

- "H1 and H2 do not maintain contact with each other" should be selected if the contact is not maintained throughout the sign, such as signs that have no contact between the hands [`STRUGGLE <https://asl-lex.org/visualization/?sign=struggle>`_, `BICYCLE <https://asl-lex.org/visualization/?sign=bicycle>`_, `MILK <https://asl-lex.org/visualization/?sign=milk_2>`_] and signs that have momentary contact at a certain point in the sign [`CRUCIFY <https://www.handspeak.com/word/search/index.php?id=7840>`_].


.. _signtype_movement_relation: 

III. Movement relation
~~~~~~~~~~~~~~~~~~~~~~

a) "Neither H1 nor H2 moves" should be selected if neither hand is involved in any movement (perceptual shape or joint-specific), such as [`SICK <https://asl-lex.org/visualization/?sign=sick>`_] 

b) "Only one hand moves" should be selected if only one hand is involved in a perceptual shape or joint-specific movement. If selected, further specification is needed below about which hand is involved in the movement.

  - Only H1 moves [`WHEN <https://asl-lex.org/visualization/?sign=when>`_]
  - Only H2 moves [this version of `SUPPORT <https://www.handspeak.com/word/search/index.php?id=2124>`_]

c) "Both hands move" should be selected if both hands are involved in perceptual shape and/or joint-specific movement. If selected, further specification is needed below regarding the movement relations between the two hands. 

  - "H1 and H2 move differently from each other" should be selected if H1 and H2 have different movements________ regardless of direction, for example [`STALK <https://www.handspeak.com/word/search/index.php?id=4168)as>`_]
  - "H1 and H2 move similarly to each other" is selected if H1 and H2 have the same movement regardless of direction, for example [`COMMUNICATION <https://asl-lex.org/visualization/?sign=communication>`_]. An example of a sign under this category that dose not involve any perceptual shape component: [`COMPARE <https://www.handspeak.com/word/search/index.php?id=2563>`_]. 


Movement direction relation and movement timing relation are specified only for signs where H1 and H2 *‘move similarly.’* Movement direction relation is relevant only for signs with a *perceptual shape* component to their movement. 

The classification of examples is dependent on whether the horizontal axis is treated absolutely (right / left and clockwise / counterclockwise) or relatively (ipsilateral / contralateral) - the examples here assume a relative horizontal axis. The choices for direction parameters can be set in :ref:`global_settings`. 


  - **Movement direction relation:**
  
      - "H1 and H2 have the same direction of movement" should be selected if the two hands move in either the same absolute direction or relative direction, depending on the choices selected in :ref:`global_settings`. Some exmaples of signs encompassed by this selection, keeping in mind a relative horizontal axis, are [BICYCLE, EXPERIMENT, CRUCIFY, FREE]. If the user has chosen absolute directions, this option could be selected for signs where both hands move rightward and leftward [`WINDSHIELD WIPERS <https://www.handspeak.com/word/search/index.php?id=3918>`_] or both hands are moving clockwise [`WHEELCHAIR <https://asl-lex.org/visualization/?sign=wheelchair>`_]. Note that choices for definitions of clockwise / counterclockwise can also be specified in :ref:`global_settings`.
 
      - "H1 and H2 have different directions of movement" should be selected if the two hands move in either different absolute directions or different relative directions, depending on the choices selected in :ref:`global_settings`. Some exmaples of signs encompassed by this selection, keeping in mind a relative horizontal axis, are [`SOCIAL <https://asl-lex.org/visualization/?sign=social>`_, `DECORATE_2 <https://asl-lex.org/visualization/?sign=decorate_2>`_, `WINDSHIELD WIPERS <https://www.handspeak.com/word/search/index.php?id=3918>`_, `COMMUNICATION <https://asl-lex.org/visualization/?sign=communication>`_]
      
      - "Not relevant" should be selected if the sign does not have a perceptual shape component to its movement [e.g., BOWTIE, MANY, COMPARE]
      
  - **Movement timing relation:**
  
      - "Sequential" should be selected if the hands do not move at the same time; when one hand is moving, the other is not, such as [CRUCIFY, HANDS]
      - "Simultaneous" should be selected if the hands move at the same time; when one hand is moving (in any way), the other is too. Further specifications can be made below.
            - "Everything is mirrored / in phase" should be selected if location, handshape, and orientation are all mirrored/in phase. Signs are considered to be mirrored / in phase when both hands have the same specification at the same time; signs are considered to be not mirrored / out of phase when the hands have opposite specifications at the same time; see :ref:`where will this information be?` **edit ref link** for more information. Some examples under this category are: [WHEELCHAIR, DRESSER, FREE, BOWTIE]
            - "Everything is mirrored / in phase except..." should be selected if some components are in phase but at least one component is out of phase. The user can check as many as apply to the sign. 
      
                - "Location" should be selected for signs that are out of phase in terms of location, that is, if the two hands have the opposite specification for location at the same time (e.g., one hand is up while the other is down). For a circle, we consider location to be out of phase if the two hands would reach the top of the circle (as defined above) at the *different* times. Note that :ref:`global_settings` for absolute vs. relative directions apply here. Some signs that fall under this category, keeping in mind a relative horizontal axis, are: [POPCORN, WINDSHIELD WIPERS, EXPERIMENT, MILK_2]
                
                - "Handshape" should be selected for signs that are out of phase in terms of handshape, that is, if the two hands have different hand configurations at a given time. Some examples are: [POPCORN, MILK_2]
                - "Orientation" should be selected for signs that are out of phase in terms of handshape, that is, if the two hands have different orientations at a given time. Some examples are: [DIE, PAIN, COMPARE].


**add screenshot of sign type module filled out for particular example of a sign**

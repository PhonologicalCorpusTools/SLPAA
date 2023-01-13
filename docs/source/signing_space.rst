.. todo::
    update to reflect that absolute/relative is now specific to the module type!
    copy sign examples for plane/circular directionality
    replace current placeholders with diagrams
        - summary image
        - top of a circle/circular directions
        - multiple sets of axes superimposed on one image
        - multiple sets of planes superimposed on one image
    add references
        - Johnson & Liddell
        - (potentially) Battison
        - Canadian ASL dictionary?
    update FOCUS to show expanded trees

.. comment:: 
    The documentations guidelines outline the information to be represented on this page as a general explanation of body geography, symmetry, planes, axes, the 'top' of a circle in each plane, anatomical position, and ipsi-contra definitions.
    
.. comment::
    From sign type: "Everything is mirrored / in phase" should be selected if location, handshape, and orientation are all mirrored / in phase (synchronized). Signs are considered to be mirrored / in phase when both hands have the same specification at the same time; signs are considered to be not mirrored / out of phase when the hands have opposite specifications at the same time; see :ref:`signing_space_page` for more information.

.. _signing_space_page:

***********************
Symmetry, Planes & Axes
***********************

This page will describe and define the terminology used throughout SLP-AA and here in its documentations in reference to the signing space on and surrounding the body. There is a fairly high level of complexity when dealing with motion in three-dimensional space, but our aim is that the visual and textual descriptions provided here will help to reduce any difficulty in interpreting the program's options and adapting them to the requirements of the individual user. 

The program relies on a system of axes and planes to frame three-dimensional space, and these are positioned relative to whichever arbitrary point makes the most sense for each sign component. This system is reapplied in several areas of the program, so many elements operate in the same way and knowing how to use one component will usually also help with being able to understand others.

.. note::
    SLP-AA incorporates the use of :ref:`modules<module>` to code sign aspects like handshape, location, movement, absolute orientation, and so on. For more discussion on the use of modules in SLP-AA to encode information about signs, see :ref:`modularity`.

.. _axes_entry:

1. Axes
````````

.. _axes_section:

I. Cardinal axis system
=======================

The system of axes is based on a set of three :ref:`cardinal_axes`: the **horizontal**, **vertical**, and **sagittal** axes. 

These axes can be described in reference to any given point on the signer's body or in the general signing space, depending on what is required for the situation. The vertical axis extends in a straight line up and down, the horizontal extends to the left and right, and the sagittal axis extends forwards and backwards. These can be seen here, labelled with SLP-AA's :ref:`default direction settings<axis_default>`:

.. image:: images/shared_axes.png
    :width: 750
    :align: left

There is a good amount of flexibility in the program for users to decide on an interpretation of the axis system that suits their needs. The axes can be defined relative to the positioning of the signer's body or the direction that they're facing, or to a relevant part of the body. The central point of origin can be adapted as necessary for the situation and the user's definition, as long as the cardinal axes are always oriented in the same way relative to each other.

.. image:: images/placeholder.png
    :width: 750
    :align: left

**(Multiple sets of axes superimposed to show that they can shift as needed)**

.. comment:
    (Description from before, potentially useful but less relevant with the sets of axes thing) It is also possible to select other directions in the program, rather than choosing strictly from the set of cardinal axes. Multiple selections within one module can be combined together to result in angled axes, as will be explained below in :ref:`directions in combinations of axes<angled_axes>`.

.. _axis_directions:

II. Axis directions
===================

.. _axis_default:

a) Cardinal directions
~~~~~~~~~~~~~~~~~~~~~~

The pairs of endpoint directions for each axis are outlined here with sign examples involving a :ref:`perceptual_shape` traced out in the given direction. The axis system applies for every sign component, not just for movement. These examples are meant to clearly display what is meant by each direction label. See the note below for examples that include this system in terms of location and orientation. 

Keep in mind that it is possible to select only the axis itself without a specific endpoint direction wherever a selection for an axis or direction applies in the program. The endpoints/directions for the vertical and sagittal axes are consistent wherever they appear. 

* **Vertical axis**

    * **Up**, as in `UMBRELLA <https://asl-lex.org/visualization/?sign=umbrella>`_ or `NORTH <https://asl-lex.org/visualization/?sign=north>`_
    * **Down**, as in `LOSE_GAME <https://asl-lex.org/visualization/?sign=lose_game>`_ or `DRAW <https://asl-lex.org/visualization/?sign=draw>`_

* **Sagittal axis**

    * **Distal**, as in `NEXT <https://asl-lex.org/visualization/?sign=next>`_ or `SINCE <https://asl-lex.org/visualization/?sign=since>`_
    * **Proximal**, as in `BEFORE <https://asl-lex.org/visualization/?sign=before>`_ 
    
The directions for the horizontal axis, however, depend on the preferences of the user. These adhere to one of two models for the horizontal axis, described in greater detail in the :ref:`next section<axis_symmetry>`. These can be toggled separately for different module types; see the :ref:`global_settings` for how to change these options and which model applies by default for each module type.
    
* **Horizontal axis: relative** [Default]

    * **Ipsilateral**, as in `SAUSAGE <https://asl-lex.org/visualization/?sign=sausage>`_
    * **Contralateral**, as in `GAME <https://asl-lex.org/visualization/?sign=game>`_ 

OR

* **Horizontal axis: absolute**
    
    * **Toward H1**, as in the right hand of `SAUSAGE <https://asl-lex.org/visualization/?sign=sausage>`_ or the left hand of `GAME <https://asl-lex.org/visualization/?sign=game>`_
    * **Toward H2**, as in the left hand of `SAUSAGE <https://asl-lex.org/visualization/?sign=sausage>`_ or the right hand of `GAME <https://asl-lex.org/visualization/?sign=game>`_

.. warning::
    **Under construction - will show additional examples for location and orientation as indicated above**
    
    There are several places throughout the program where similar or identical terms are used for slightly different contexts. Take care to note the sign component that any given word is meant to be describing to be sure that your choice is accurate.
    
Assuming that the horizontal axis is defined in relative directions, the words :ref:`ipsilateral` and :ref:`contralateral` can be applied for any (or all) of the movement direction, location, or hand orientation descriptions of a sign:
    
    * In `RAINBOW <https://asl-lex.org/visualization/?sign=rainbow>`_, the dominant hand moves in the ipsilateral **direction** (toward the signer's right, in this case), and it changes **location** from the contralateral to the ipsilateral side of the body. The **orientation** of the hand changes in the production of the sign, starting with the finger roots pointing down and the palm facing the ipsilateral direction and finishing with the finger roots pointing up and the palm facing the contralateral direction.
    
        * ``[ADD SAMPLE TRANSCRIPTION WITH THESE DETAILS]``
    
    * In `SLICE_2 <https://asl-lex.org/visualization/?sign=slice_2>`_, the dominant hand moves in a proximal and ipsilateral **direction** (toward the signer's right, in this case), but its **location** starts on the contralateral side and ends at the midline of the body without ever crossing over to the ipsilateral side. The **orientation** of the hand is unchanging, with the finger roots angled in the distal and contralateral directions and the palm angled to face the proximal and contralateral directions.
    
        * ``[ADD SAMPLE TRANSCRIPTION WITH THESE DETAILS]``
    
    These descriptions may be confusing at first glance. Familiarising yourself with each of the modules' functionalities will help with developing clear and precise transcriptions that take advantage of the high level of detail that is possible to record with the program.

.. _axis_symmetry:

b) Symmetry in the horizontal axis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Update sign type so that the most detailed descriptions are left there, including sign examples. (I'm not actually sure if this section is necessary here at all! It's possible that another note in the axis direction section would be enough.)**

.. _angled_axes:

c) Directions in combinations of axes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes the axis direction of a perceptual shape is traced along an **angled path** rather than one of the :ref:`cardinal_axes`, as in `FOCUS <https://asl-lex.org/visualization/?sign=focus>`_ and `SNOW_2 <https://asl-lex.org/visualization/?sign=snow_2>`_. In this case, the angled path is made up of a combination of two or all three of the cardinal axes. See the following illustration for how this works:

.. image:: images/mov_combinations_of_axes.png
    :width: 750
    :align: left

In these examples, the sign includes the black line traced out in an angled direction. The angled line can be "flattened" into each of its component cardinal axes, and then the resulting axis directions are simpler to record and analyze. The information to record in the program for this example should then be the directions indicated for the coloured lines along each of their respective cardinal axes.

Here is a possible coding of `FOCUS <https://asl-lex.org/visualization/?sign=focus>`_, highlighting its two component axis directions within one module:

.. image:: images/mov_sample_sign_FOCUS.png
    :width: 750
    :align: left

When multiple directions are selected within one module, this is always interpreted as an angled direction with all selections applying simultaneously (as selected by the associated :ref:`timing values<timing_page>`). To instead indicate a sequence of directions, create multiple instances of the module, associate them with separate (and sequential) :ref:`timing values<timing_page>` and select the appropriate direction for each one.

.. comment::
    From the 'to mention' doc: It might be useful to give some examples of how our perceptual movement direction combination (e.g., up-ipsi, etc.) correspond to Johnson & Liddell’s (2021) vertical and horizontal “directions of bearing” (p.140-141, fig. 8-9). 

.. _planes_entry:

2. Planes
``````````

.. _planes_section:

I. Cardinal plane system
========================

We can also describe a set of :ref:`cardinal_planes`, where each plane is formed by a pair of the :ref:`cardinal_axes`: described above. **...**

.. comment::
    These are the **horizontal**, **vertical**, and **sagittal** planes, shown here:

.. image:: images/shared_planes.png
    :width: 750
    :align: left

There is a good amount of flexibility in the program for users to decide on an interpretation of the plane system that suits their needs. The planes can be defined relative to the positioning of the signer's body or the direction that they're facing, or to a relevant part of the body. The central point of origin can be adapted as necessary for the situation and the user's definition, as long as the cardinal planes are always oriented in the same way relative to each other.

**(In our system: the kind of information that can be recorded with only the 'axis direction' and 'plane' options.)** `WHALE <https://asl-lex.org/visualization/?sign=whale>`_

.. image:: images/placeholder.png
    :width: 750
    :align: left

**(Multiple sets of planes superimposed to show that they can shift as needed)** 

.. _angled_planes:

a) Combinations of planes
~~~~~~~~~~~~~~~~~~~~~~~~~

**Describe angled planes here for non-straight shapes, particularly without circular direction.** 

Planes on an angle are made up of component combinations of two or all three of the cardinal planes. 

Sometimes the axis direction of a perceptual shape is traced along an **angled path** rather than one of the :ref:`cardinal_axes`, as in `FOCUS <https://asl-lex.org/visualization/?sign=focus>`_ and `SNOW_2 <https://asl-lex.org/visualization/?sign=snow_2>`_. In this case, the angled path is made up of a combination of two or all three of the cardinal axes. See the following illustration for how this works:

Here is a possible coding of `SIGN <>`_, highlighting its two component planes within one module:

.. image:: images/placeholder.png
    :width: 750
    :align: left

.. comment::
    When multiple planes are selected within one module, this is always interpreted as an angled plane with all selections applying simultaneously. To instead indicate a sequence of ``movements`` in different planes, create multiple instances of the module, associate them with separate (and sequential) :ref:`timing values<timing_page>` and select the appropriate plane for each one.

.. _circular_directions:

II. Circular directions
=======================

**Note that horizontal movements are dependent on the system for horizontal axis movements, so the choice for absolute or relative directions will have an impact here as well.** Introduce the concept of defining circular direction relative to (axis) direction through a single immutable point: in this case, our fixed reference point

.. _plane_default:

a) Default directions
~~~~~~~~~~~~~~~~~~~~~

**State the point on a circle in each plane that we define to be the top of a circle in that plane. Note especially that this notion is independent from movement. Then introduce the idea of circular directionality (in movement) as defined by the (axis) direction of movement through the topmost point for that plane. Needs a set of diagrams. Follow the order as required in the next section: describe the sagittal plane, then vertical, then horizontal.**

.. image:: images/placeholder.png
    :width: 750
    :align: left

**Definition (and possibly illustration) of default directions, in reference to the top of the circle. Start with the sagittal plane to describe the simple case, then the vertical, then horizontal. Note: it might be best to copy over the images from sign type for the vertical plane.**

.. _plane_symmetry:

b) Symmetry in planes involving the horizontal axis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Complications from the horizontal axis in particular, i.e. for the vertical and horizontal planes and any combinations involving these, the left/right system, interchangeability of the two horizontal systems, more implications for 'same' direction in sign type.**

.. _angled_circles:

c) Circular shapes in combinations of planes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes circular shapes are traced within an **angled plane** rather than one of the :ref:`cardinal planes`, as in `SOCIALIZE <https://www.handspeak.com/word/index.php?id=2014>`_ and `TWIRL <https://asl-lex.org/visualization/?sign=twirl>`_. In this case, code the orientation of the plane of movement by finding the applicable component planes (as described :ref:`above<angled_planes>`), and then continue to code the direction within the angled plane by selecting the component directions as they would be within the component (cardinal) planes. See the following illustration for how this works:

.. image:: images/mov_combinations_of_planes.png
    :width: 750
    :align: left

In this example, the sign includes the black circle traced out in an angled plane. The idea is that the angled circle could be "flattened" into each of its components, and then the resulting circular directions are simpler to record and analyze. Then the information to record in the program for this example should be each of directionalities indicated for the coloured circles, which are situated in cardinal planes.

Here is a possible coding of a movement module for `SOCIALIZE <https://www.handspeak.com/word/index.php?id=2014>`_, highlighting the combined circular direction components:

.. image:: images/mov_sample_sign_SOCIALIZE.png
    :width: 750
    :align: left

Note that the axis direction as selected here describes the position of each hand at the midpoint of its first circle relative to its position at the beginning of the movement, though there are other possibilities for how to specify this. (See the note on :ref:`axis direction for circular shapes<axis_direction_entry>` for more information).

.. note::
    Absolute vs. relative orientation of planes for `WASH_FACE_1 <https://asl-lex.org/visualization/?sign=wash_face_1>`_

.. _body_location_relative:

3. Body-anchored locations
``````````````````````````

**This section will describe how the information on the rest of this page applies to body-anchored locations in particular (both the 'on-body locations' and the signing space option defined in terms of a body location).**

.. warning::
    Depending on how the location documentations are set up, this section may be irrelevant here. I expect that it will get cut out and left permanently over there.

.. comment::
    {Introduction to the particular difficulties introduced with horizontal symmetry over any other kind}
    
    -->    {The (set of) sagittal plane(s) as normal to the horizontal axis}
        
    {Anatomical symmetry across the "midline," or whatever terminology}
    
    -->    Terminology: Line of bi-lateral symmetry (from Battison), or plane of horizontal symmetry, or plane of bisection, or other. Specifically the **mid-sagittal** plane, rather than any given sagittal plane. (i.e. symmetry in terms of actual physical symmetry)
    
    {Why the discrepancy? --> Difficulties in articulation mechanisms, anatomical limitations AND strengths}
    
    -->    Comment on low instances of simultaneous movement along sufficiently different axes and/or planes for each hand, and link this to difficulties wrapping our heads around complex combinations of movement in the mid-sagittal plane (the only one that does not involve the horizontal axis). Like trying to pat your head and rub your stomach, it takes more concentration and effort than moving in what we can easily conceptualize as the 'same' direction, with all of the baggage that that generalization comes along with. (Also link this to our broad categories in sign type for moving 'similarly' vs. 'differently' and how the 'simultaneous except handshape/location/orientation' options are more likely to apply with only minimal/predictable differences, e.g. simple alternation.)
    
.. _symmetry_review:

4. The signing space
====================

**Detailed summary for quick reference, consisting mostly of a set of visuals and sign examples.**

**Quick and simple review of everything mentioned so far in terms of the basics of planes and axes, i.e. put these together with detailed illustrating images and just go for an overview of our cartesian system and the labels for each component. Focus on the competing options for describing horizontal symmetry. Hopefully this will be a good way to easily reference the important information without digging through the whole page.**

.. image:: images/placeholder.png
    :width: 750
    :align: left

.. comment::
    This placeholder should be replaced with a detailed image that shows a full summary of the set of cardinal axes and planes with all possible directions labelled appropriately (including both sets of options for directions involving the horizontal axis), preferably with a demonstrated reference to the direction of the signer's body. This might be easiest to accomplish if we use a still image and superimpose the relevant information over top of it.
    

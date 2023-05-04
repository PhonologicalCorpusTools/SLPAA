.. todo::
    change everything here to conform to new Relation module
        this may require a lot of restructuring, so I haven't bothered to number the sections as they are now

.. comment::
    Signs with a contact module include a subset of Brentari’s (1998) ‘tracing’ signs, like `BLACK <https://asl-lex.org/visualization/?sign=black>`_ (no contact – this would be coded as ‘body anchored’ in location + ‘near contact’ in the contact module) and `LONG <https://asl-lex.org/visualization/?sign=long>`_.

.. _relation_module:

***************
Relation Module
***************

This :ref:`module` is used to code the ``contact`` **(give some thought to what would go here)** components of a sign. As many :ref:`instances<instance>` of this module as necessary can be called for any given sign coding. For more discussion on the use of modules in SLP-AA to encode information about signs, see :ref:`modularity`.

This module is atypical in that it does not necessarily apply to the hands.

Module instances link to generic :ref:`x-slots<x_slot>` to record information about their timing relative to any others within a sign. For more information on the use of x-slots in SLP-AA, consult :ref:`timing_page`.

.. _rel_module_selection:

?. Linking existing module instances
````````````````````````````````````

**Linking modules:** List of instances of Location coded already. Also allow 'not linked to a location module' e.g. to code contact between hands in neutral space for signs like `DESTROY <https://asl-lex.org/visualization/?sign=destroy>`_.

.. _contact_entry:

?. Contact
```````````

**Contact options:**

* Contact
* No contact

.. _contact_manner:

I. Contact Manner
=================

**Contact manner:** Only if Contact and if this instance of the module is linked to an interval/intervals, not single points in time. All selected instances will have the same value. To record different values, generate separate instances of the module.

* **Holding**, as in `DIRTY <https://asl-lex.org/visualization/?sign=dirty>`_, `APPLE <https://asl-lex.org/visualization/?sign=apple>`_, or `SHOW <https://asl-lex.org/visualization/?sign=show>`_
* **Continuous**, as in `NICE <https://asl-lex.org/visualization/?sign=nice>`_
* **Intermittent**, as in `SALT <https://asl-lex.org/visualization/?sign=salt>`_ or `BEACH <https://asl-lex.org/visualization/?sign=beach>`_

.. _relation_x_y:

?. Relation between X and Y
```````````````````````````

**(Intro: what this can be used for)**

.. warning::
    **This section is broader than it was when it was first introduced to describe the relation between the hands only. At the time, it was thought that it could be useful in particular for connected signs, and possibly classifier constructions. Those should still be mentioned here.**

.. _direction_of_relation:

I. Direction of relation
========================

Make up to one selection from each axis to describe the relationship between your choices of X and Y. You can also select the axis of relation itself without specifying a direction.

(Give an example of a body-anchored location to show how this works, preferably using an 'aligned with' option. Maybe BLACK using: vertically aligned with eyebrows, and distal+close but with no contact.)

* **Horizontal**

    * X is ipsilateral to Y
    * X is contralateral to Y
    * X is aligned with Y

* **Vertical**

    * X is above Y
    * X is below Y
    * X is aligned with Y

* **Sagittal**

    * X is more distal than Y
    * X is more proximal than Y
    * X is aligned with Y

.. _distance_of_relation:

II. Distance of relation
========================

You can include an optional distance specification for each axis that is applicable to the relation between X and Y. A maximum of one selection can be made from each axis (represented by a column in the table below), though it is not required to make a specification from every axis:

.. list-table::
    :widths: 30 30 30
    :header-rows: 1

    * - Horizontal axis
      - Vertical axis
      - Sagittal axis
    * - Close
      - Close
      - Close
    * - Medium
      - Medium
      - Medium
    * - Far
      - Far
      - Far

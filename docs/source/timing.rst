.. todo::
    Subjects to tackle:
        Global options for timing
            No x-slots, manual, or automatic
            If x-slots, then which subdivisions can be available
        Editing existing module specifications
            Changing x-slot associations for a module in an existing sign
            Does this complicate linked modules? or are they independent in timing?
        Expected program behaviour
            Adding/editing/removing (# of) x-slots in an existing sign
            Changing x-slot settings partway through creating a corpus
        Refer to the 'Timing Options' and 'Update to timing options' sections in the system overview

.. _timing_page:

****************
Timing & X-Slots
****************

**Introduction.** Link to: :ref:`x_slot` glossary entry, :ref:`setting_preferences` (options with respect to generation of x-slots as well as subdivisions), :ref:`automated_processes`, and mention timing as relevant to selecting sign type options (simultaneous or sequential) and movement phasing options (in phase/out of phase).

**New!** X-slots can represent either syllables or segments.

.. _adding_x_slots:

1. Generating and linking x-slots
`````````````````````````````````

**Description** You can choose whether the number of x-slots is manually specified by the user for each sign before coding, or if it will be automatically determined by the program based on the movement modules, or you can choose to disable the use of x-slots completely.

.. comment::
    "Explain what an x-slot does/does not represent. Explain partial x-slots at the end, and internal divisions within complete x-slots (what works best here for concrete examples? contact/location/handpart?). Focus on functionality first, then give some examples of why these features may be useful for specific signs." This is less relevant now that there will be a glossary entry for x-slots

.. warning::
    **Under construction** - this was cut out from the movement documentations

    Depending on your choices of how to interact with x-slots, the step to start adding modules to a sign may come at different points in the coding process.
    
    If :ref:`x-slots<x_slot>` and :ref:`auto-generation<auto_gen>` are both enabled, then code the **movement module(s)** for the sign immediately after entering the :ref:`sign_level_info` and coding the :ref:`sign_type`. The movement information is used by the program to generate the appropriate number of x-slots for the sign, and then you'll be able to move on to other sign modules.

    If :ref:`x-slots<x_slot>` are enabled but :ref:`auto-generation<auto_gen>` is not, then you must add the appropriate number of x-slots first before adding any modules at all to the sign.

    See :ref:`global_settings` for more about the program's default behaviour, and how to change these options.

.. _x_slot_visual:

2. Visual representation
````````````````````````

.. _sign_summary:

I. The sign summary window
==========================

(Describe what this looks like and how to interact with it. Note how to make it show up if it doesn't seem to be visible in the program window. Include an image of a sample sign summary visualization, preferably with multiple modules with an interesting timing configuration and some modules that apply to both hands. Maybe contrast this with how the same sign would look without x-slots enabled.)

Note that the program will generate a single instance of a module when you create one that applies to both hands, though it will be represented with two 'boxes' in the sign summary. Any future edits to either appearance will also apply to the other, as these are only a single instance of the module in actuality.

.. _move_timing_selection:

II. X-slot selection
====================

.. note::
    This whole section will apply for every module type except nonmanuals, which will need more detail.

.. warning::
    **Under construction**
    
    (Add descriptions for how to interact with the x-slot field within a module.) Assume that x-slots are enabled, and this section can be skipped if they are not. Add a screenshot for context. Important notes: no overlapping points or regions, must make at least one selection, points vs. intervals, functionally identical timing selections(?) ← I meant choosing 'whole sign' vs 'first x-slot' for signs with exactly one x-slot, but now I'm wondering how different everything is on the back end if you want to do extra clicking for smaller intervals than necessary in general (e.g. always choosing the first and second half of each x-slot instead of the whole thing).

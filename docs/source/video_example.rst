.. video_example:

************************
Embedding Video Examples
************************

There are two ways to embed video in readthedocs. 


.. _youtube: 

From YouTube
============
You can use a "raw" block of html code. 

The code looks like this:

.. code-block:: rst

  .. raw:: html

      <div style="position: relative; padding-bottom: 56.25%; margin-bottom: 2em; height: 0; overflow: hidden; max-width: 100%; height: auto;">
          <iframe src="https://www.youtube.com/watch?v=KMYN4djSq7o" frameborder="0" allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
      </div>
      
The results look like this:


.. raw:: html

    <div style="position: relative; padding-bottom: 56.25%; margin-bottom: 2em; height: 0; overflow: hidden; max-width: 100%; height: auto;">
        <iframe src="https://www.youtube.com/watch?v=KMYN4djSq7o" frameborder="0" allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
    </div>

.. _github:

Linking to a video we host on github
====================================

`A sample video <https://github.com/PhonologicalCorpusTools/SLPAA/tree/main/docs/source/images/samplevideo.mp4/>`_

or 

If we're hosting the video ourselves it can be embedded similarly to how we do images. Readthedocs seems to really want to display text, so you can either add alt text with a description of the video, or explicitly include alt text but leave it blank if you don't want a description/caption to show.

.. image:: images/samplevideo.mp4
        :width: 60
        :align: left
        :alt: A sample video
|
|
|
|
|

.. image:: images/samplevideo.mp4
        :width: 60
        :align: left
        :alt: 
|
|
|
|
|
        
This doesn't seem to work:

.. code-block:: rst

  .. video:: images/samplevideo.mp4
          :width: 60
          :align: left
          :alt: A sample video

Linking to a video that's hosted on github and uploaded to readthedocs
===================================

TODO

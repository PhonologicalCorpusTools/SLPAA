.. video_example:

************************
Embedding Video Examples (internal tutorial)
************************

There are two ways to embed video in readthedocs. 


.. _youtube: 

From YouTube
============
You can use a "raw" block of html code. 

The code looks like this (note the use of "/embed/" rather than "/watch?v="

.. code-block:: rst

  .. raw:: html

      <div style="position: relative; padding-bottom: 56.25%; margin-bottom: 2em; height: 0; overflow: hidden; max-width: 100%; height: auto;">
          <iframe src="https://www.youtube.com/embed/KMYN4djSq7o" frameborder="0" allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
      </div>
      
The results look like this:


.. raw:: html

    <div style="position: relative; padding-bottom: 56.25%; margin-bottom: 2em; height: 0; overflow: hidden; max-width: 100%; height: auto;">
        <iframe src="https://www.youtube.com/embed/KMYN4djSq7o" frameborder="0" allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
    </div>

.. _github:

Linking to a video we host on github (which gets automatically uploaded to readthedocs)
====================================

If we're hosting the video ourselves and you try to embed it similarly to how we do images, you'll get a screenshot from the video, and a text string, both of which link to the video (which will play separately, not embedded in the doc). Readthedocs seems to really want to display text (if there's no alt text it will just display the link path) so you can either add alt text with a description of the video...

.. code-block:: rst

  .. image:: images/samplevideo.mp4
          :width: 60
          :align: left
          :alt: A sample video

.. image:: images/samplevideo.mp4
        :width: 60
        :align: left
        :alt: A sample video
|
|
|
|
|
... or explicitly include alt text but leave it blank if you don't want a description/caption to show.

.. code-block:: rst

  .. image:: images/samplevideo.mp4
          :width: 60
          :align: left
          :alt: 

.. image:: images/samplevideo.mp4
        :width: 60
        :align: left
        :alt: 
|
|
|
|
|
        
I haven't been able to find an explicit video-embedding function yet, so (eg) this doesn't seem to work:

.. code-block:: rst

  .. video:: images/samplevideo.mp4
          :width: 60
          :align: left
          :alt: A sample video
          
Test

.. raw:: html

  <video controls src="images/samplevideo.mp4"></video>


  <video controls src="images/samplevideo2.mp4"></video>


Sources
========

* https://github.com/readthedocs/readthedocs.org/issues/879
* https://groups.google.com/g/sphinx-users/c/_z00m3zoRAY?pli=1
* https://stackoverflow.com/questions/48820321/how-to-force-a-file-mp4-to-transfer-from-github-to-readthedocs


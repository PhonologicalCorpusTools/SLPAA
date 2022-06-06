.. video_example:

************************
Embedding Video Examples (internal tutorial)
************************

There are two ways to embed video in readthedocs. 


.. _youtube: 

Method 1: From YouTube
======================
You can use a "raw" block of html code, which looks like this:

.. code-block:: rst

  .. raw:: html

      <div style="position: relative; padding-bottom: 56.25%; margin-bottom: 2em; height: 0; overflow: hidden; max-width: 100%; height: auto;">
          <iframe src="https://www.youtube.com/embed/KMYN4djSq7o" frameborder="0" allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
      </div>

Note (a) the use of "/embed/" rather than "/watch?v=", and (b) the various parameters that can be adjusted (like max-width, eg, which could be specified in percentage of page width *or* pixels).

The results look like this:

.. raw:: html

    <div style="position: relative; padding-bottom: 56.25%; margin-bottom: 2em; height: 0; overflow: hidden; max-width: 100%; height: auto;">
        <iframe src="https://www.youtube.com/embed/KMYN4djSq7o" frameborder="0" allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
    </div>

.. _github:

Method 2: Stored on github and readthedocs
====================================

Again, we can use raw html here, but to embed a video stored on the same file system rather than from YouTube. Note that if you want to use this method, the video will have to live in the "/_static" directory on github so that it gets uploaded to readthedocs properly (readthedocs doesn't know to look for files referenced in <video> html tags, but it *does* know to upload everything in /_static no matter what.

.. code-block:: rst

  .. raw:: html
  
    <video controls src="_static/samplevideo2.mp4" width="120"></video>
  

.. raw:: html

  <video controls src="_static/samplevideo2.mp4" width="120"></video>
  
More info on the html video tag (changing sizes, controls, etc) `here <https://www.w3schools.com/html/html5_video.asp>`_.


Method 3: Not really embedding but figured I'd include it anyway
==========================================

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
     

Sources
========

* https://github.com/readthedocs/readthedocs.org/issues/879
* https://groups.google.com/g/sphinx-users/c/_z00m3zoRAY?pli=1
* https://www.w3schools.com/html/html5_video.asp


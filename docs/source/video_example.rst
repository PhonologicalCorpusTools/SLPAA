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

A video we host ourselves on github
===================================
If we're hosting the video ourselves it can be embedded similarly to how we do images.

.. image:: images/samplevideo.mp4
        :width: 60
        :align: left
        :alt: A sample video
        
This doesn't seem to work:

.. raw:: rst

  .. video:: images/samplevideo.mp4
          :width: 60
          :align: left
          :alt: A sample video

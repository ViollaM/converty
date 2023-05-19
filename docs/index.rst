.. Converty documentation master file, created by
   sphinx-quickstart on Fri May 19 19:08:25 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Converty's documentation!
====================================

This is a Telegram bot that can convert files quickly and conveniently.

Main commands
-------------

- **/start**: getting started with the bot
- **/help**: displaying a list of available commands and their description
- **/make <format>**: creates a file of the specified format from uploaded files
- **/reset**: reset uploaded files
- **/stop**: stop using the bot

Supported conversion formats
----------------------------

.. table:: Supported formats

    +-------------+--------------+
    | Input type  | Output type  |
    +=============+==============+
    | images      | pdf          |
    +-------------+--------------+
    | pdf         | images       |
    +-------------+--------------+
    | files       | zip          |
    +-------------+--------------+
    | zip         | files        |
    +-------------+--------------+

   
.. toctree::
    :maxdepth: 2
    :caption: Contents:
   
        Technical documentation <techDoc>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

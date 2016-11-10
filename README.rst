sitebuilder
===========
GTK frontend to Python script. 

The script has a gaudy name meaning 'conversions and maintenance of HTML files in websites'.

.. figure:: https://raw.githubusercontent.com/rcrowther/sitebuilder/master/text/sitebuilder_target.jpg
    :width: 160 px
    :alt: gsitebuilder screenshot
    :align: center

    Pick folders...

.. figure:: https://raw.githubusercontent.com/rcrowther/sitebuilder/master/text/sitebuilder_js.jpg
    :width: 160 px
    :alt: gsitebuilder screenshot
    :align: center

    ...and fix

The script can work in a given directory, or recursively down from that directory.


Usage
~~~~~
Install the gsettings schema using Meson, then::

    ./gsitebuilder.py


Headers
~~~~~~~~
The script can place 'header' markup after a <body> tag (i.e. for navbar/sidebar or citation purposes). 

The script can remove/replace current 'header' elements which follow 'body' tags.


Indexes
~~~~~~~
Builds an index to the contents of a folder. Various options offered, including 'ignore' if an index exists.

Indexes ignore Linux/Mac hidden files (not starting with '.' or '~'). Only regular files ending with '.htm' or 'html', are placed in an
index. The title of the index is taken from the folder name. Links written in various styles, short/relative et. Text in the links is file basenames with underscores replaced by spaces.
 
Index entries are sorted. The current layout separates links into two separate lists, folders and regular files. Within each list, names starting
with a symbol come first, followed by names starting with a number,
followed by names starting with an alphabetic character. Each 
sub-category is internally sorted.


CSS/JS Link rewriting
~~~~~~~~~~~~~~~~~~~~~
The script can rewrite links to static resources.

The script detects CSS/JS elements, and can delete, or replace/append with new CSS/JS elements.


Img 'src' rewriting
~~~~~~~~~~~~~~~~~~~~~
The script can replace image 'src' attributes with new path roots. The image 'src' basename is preserved.


This is version 1, not because it is matured, but because it is a complete and incompatible rewrite of the earlier version. Maybe the commandline will return, but I'm not rushing...

    :copyright: 2016 Rob Crowther
    :license: GPL, see LICENSE for details.

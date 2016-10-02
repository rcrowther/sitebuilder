sitebuilder
===========
Gaudy name for conversions of html files to place in websites.

The script works recursively from a given directory.


Usage
~~~~~
From the commandline::

    ./sitebuilder.py <options> -d /.../inputFile

Options include::

  -h, --help           show this help message and exit
  -d FILE, --dir=FILE  directory to start
  -i, --indexes        generate HTML indexes in every visited folder
  -l, --links          rewrite urls in links and images. Overwrites existing
                       urls.
  -n, --navbars        insert navbars into pages
  -N, --forcenavbars   Slow! Risky! insert navbars into pages, attempting to
                       remove previous bars
  -s, --shorturls      for indexes, generate urls as short (no -index.htm-
                       extensions to directories, no extensions on files)





Indexes
~~~~~~~
An index can be built to the contents of a folder.

The script will not build an index if a file 'index.*' exists. Once an 
index is created it will not be replaced. To rebuild an index the 
existing 'index,htm' must be deleted.

Only visible directories (not starting with '.' or '~') are placed in an
index. Only regular files ending with '.htm' or 'html', are placed in an
index.The title of the index is taken from the folder name. Declared
navbar information is also written into the page. Links written to an
index are relative. Text in the links is file basenames with underscores
replaced by spaces.
 
Index entries are sorted. The current layout separates folders from 
regular files, in two separate lists. Within each list, names starting
with a symbol come first, followed by names starting with a number,
followed by names starting with an alphabetic character. Each 
sub-category is internally sorted.

The links in an index can be modified by,


'-s': short urls
---------------
Links are formatted as short urls. The server or content manager 
configuration must support short urls to work. If '/plants' contains
'/plants/weeds/ragwort.htm', the default link is::

    <a href="/plants/weeds/ragwort.htm">ragwort</a>

using the short option::

    <a href="/plants/weeds/ragwort">ragwort</a>

'-s' also affects directory links. If '/plants' contains
'/plants/weeds' and '/plants/shrubs', the default link in the 'plants'
index, to 'weeds', is::

    <a href="/plants/weeds/index.htm">weeds</a>

using the short option::

    <a href="/plants/weeds/">weeds</a>
    
which presumes a server/content manager can guess to look for an
'index.htm' file.



Link rewriting
~~~~~~~~~~~~~~
The script can rewrite links to static resources.

Warning: link detection is risky.

The script detects 'src' attributes, or 'href' attributes with links
ending in '.js' or '.css'. The base name is extracted from matching
links, and added to a root path stated in the script (these links would 
usually be absolute).

 

Navbars
~~~~~~~~
WARNING: The markup text must be sequential in the file, no newlines.

The script can place header or navbar markup after a <body> tag. 

The text used is set in the variable::

    bodyHeaderMarkup = ...

The code defends against inserting the markup if a <header> or <nav> tag
exists. So it will not repeatedly insert if the script is run multiple
times.

Navbars are not automatically built, because website top level folders
may contain folders for static files, protected folders, etc.
  

'-N': forced navbar insertion
-----------------------------
Replace a navbar.

Since detection of HTML elements is risky without a parser, this action
has an explicit option. 


    :copyright: 2016 Rob Crowther
    :license: GPL, see LICENSE for details.

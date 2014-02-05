VisTrails MTA Example
=====================

An example vistrail that uses New York MTA data. 

About
-----

The Wall Street Journal published a story in 2011 that examined MetroCard usage as the cost of fares changed.  The original work was created by Albert Sun and Andrew Grossman and published at [http://graphicsweb.wsj.com/documents/MTAFARES1108/](http://graphicsweb.wsj.com/documents/MTAFARES1108/) on October 17, 2011. To do this, they used the publicly available [fare data](http://mta.info/developers/fare.html) from the [Metropolitan Transportation Authority](http://mta.info/) (MTA).  Their results were an interesting snapshot of usage patterns in the six months before and after the fare change.  Because this data is made available on a weekly basis, it is possible to analyze more recent data as it becomes available.  In addition, we can restrict views to specific lines or compare different ranges of time.  By completing this analysis in VisTrails, it becomes much easier to do these types of explorations.


Installation
------------

This example will soon be available in the [VisTrails repository](http://github.com/vistrails/vistrails) and will also be included in future releases.  These instructions are provided for users that wish to explore the example with the current (as of 2/5/2014) release (2.1.1). You will need [VisTrails 2.1.1](http://www.vistrails.org/index.php/Downloads/) for this example. The vistrail is mta.vt, but because it uses new and revised VisTrails packages, this repository also contains those three VisTrails packages:

1. HTTP
2. tabledata
3. gmaps

Note that HTTP and tabledata have been renamed HTTP\_new and tabledata\_new to minimize conflicts. To install these three packages, copy them into your ~/.vistrails/userpackages directory. Then, in the Module Packages panel of the VisTrails Preferences window,

1. *Disable* the HTTP and tabledata packages.
2. *Enable* the HTTP\_new, tabledata\_new, and the gmaps packages.

You should then be able to load and run the mta.vt example. It is very important to disable the old packages!

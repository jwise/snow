`snow`: a programmatic interface to snow reports
================================================

The `snow` package provides a programmatic interface for scraping snow
reports.  As it turns out, OpenSnow isn't, and it seems that ski resorts
don't provide APIs with all the data you might want.  A secondary (primary?)
goal is to provide an excuse for me to learn BeautifulSoup...

Currently, `snow` supports only the Vail Resorts in Tahoe.  Other resorts
may be implemented as time -- or pull requests -- permit.

`snow` resort implementations should try to adhere to a standard-ish API --
ideally, all modules should provide at least one function, `snow_report()`,
which returns a dictionary kind of like the one that `heavenly` returns. 
Features should be added in a way that will effectively generalize to other
resorts, if possible.

Currently, it's possible to do things like:

    >>> r = heavenly.snow_report()
    >>> print [run for run,details in r['runs'].items() if details['open']]
    [u'Tamarack Return', u'California Tr.-Up', u"Orion's", u'California Trail', u'Big Dipper-Upper', u'Sledding', u'Big Dipper-Lower', u'Comet']
    >>> print [lift for lift,details in r['lifts'].items() if details['open']]
    [u'Gondola', u'Red Fir Mitey Mite', u'Tamarack Express', u'Dipper Express', u'Bear Cave Carpet', u'Comet Express', u'Big Easy']
    >>> print r['stats']
    {'runs': {'total': 97, 'open': 7}, 'percent': 7, 'acres': {'total': 4800, 'open': 44}}

Other interesting wrapper utilities would be tracking tools to inform new
lifts open and as new terrain opens, and provide appropriate messages;
comparison tools to see which resorts got the most powder overnight; and
`.login`-friendly tools that download and cache, and inform when the user
should ragequit work and hit the slopes.


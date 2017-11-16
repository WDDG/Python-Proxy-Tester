import re
string = "[815ms] omgit369!a34:57OMGIT@178.236.224.0:33128 (http://www.adidas.com/ -> http://www.adidas.com/us/) -- OK (200)"

try:
    found = re.search(r'\[(.+?)ms', string).group(1)
    print found
except AttributeError:
    print "not found"



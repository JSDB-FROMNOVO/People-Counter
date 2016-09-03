import simplejson as json

def parser():
    vendors = {}
    with open("oui.txt") as f:
	for i in xrange(5):
            f.next()
	counter = 0
	private = False
	for line in f:
	    if private:
		private = False
	    if (counter % 6) == 0:
		key = str(line[:6])
		val = str(line[22:-2])   
		#v[str(line[:6])] = str(line[22:-2])
		vendors[key] = val
		if line[22:-2] == "Private":
		    counter += 4
		    private = True
	    	    continue
	    counter += 1
    #return json.dumps(vendors, indent=4 * ' ')
    return vendors

#vendors = parser()	
#print vendors

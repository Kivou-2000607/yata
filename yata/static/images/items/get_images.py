import os
import numpy

from random import randint
def random_number(length=3):
    return randint(10**(length-1), (10**(length)-1))
    
fetch = numpy.arange(910,998)
for i in fetch:
    print( "get image:", i+1 )
    if not os.path.isfile( "{}/large.png".format( i+1 ) ):

        random = random_number( length=5 )
        url = "https://www.torn.com/images/items/{}/large.png".format( i+1 )
        print( url )
        
        os.system( "rm -fr {}".format( i+1 ) )
        os.system( "mkdir {}".format( i+1 ) )
        os.system( "wget --tries=1 {}?{}".format( url, random ) )
        os.system( "mv large.png?{} {}/large.png".format( random, i+1 ) )
        print( "" )

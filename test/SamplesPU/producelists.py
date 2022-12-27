from Samples import MINIAOD as MINIAOD

import subprocess

for s in MINIAOD:
    #with open(, 'w' ) as f:
    command = " ".join( ['das_client','--limit=0' , '--query="file' , 'dataset=%s"'%(s.DSName)] )
    print "%s > %s.list" % ( command  ,  s.Name )
        #f.write( subprocess.check_output( [command] ) )


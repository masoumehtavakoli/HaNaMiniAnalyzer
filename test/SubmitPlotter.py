eras=["All"]
eras.extend( [ "era"+c for c in ["B", "C","D","E","F","G","H" ] ] )

puScenarios = { "pcc" :[95,105,5]  ,
                "bestFit":[95,105,5]  ,
                "latest":[84,117,1] }

for era in eras:
    for puScenario in puScenarios:
        variation = puScenarios[puScenario]
        xsecs = "%d-%d:%d" % ( variation[0] , variation[1] , variation[2] )
        lxbatch = "bsub -q 1nh -J {pu:s}_{era:s}[{xsecs:s}] -env \"all\" -o {pu:s}_{era:s}_%I.out Plotter.py {pu:s} {era:s}".format( pu=puScenario , era=era , xsecs=xsecs )
        print lxbatch

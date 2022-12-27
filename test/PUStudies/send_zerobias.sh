#!/bin/bash

#big picture plots
scp *.png helfaham@server02.fynu.ucl.ac.be:~/public_html/pileup/UL/2018/ZeroBias

#correlation plots
scp ./corr/*.png helfaham@server02.fynu.ucl.ac.be:~/public_html/pileup/UL/2018/ZeroBias/corr_plots

#FitRes
scp ./FitRes/new_test_plots/All/*.png helfaham@server02.fynu.ucl.ac.be:~/public_html/pileup/UL/2018/ZeroBias/vars_All
scp ./FitRes/new_test_plots/eraA/*.png helfaham@server02.fynu.ucl.ac.be:~/public_html/pileup/UL/2018/ZeroBias/vars_eraA
scp ./FitRes/new_test_plots/eraB/*.png helfaham@server02.fynu.ucl.ac.be:~/public_html/pileup/UL/2018/ZeroBias/vars_eraB

#Gaussfits
scp ./gaussfits/*_All_test.png helfaham@server02.fynu.ucl.ac.be:~/public_html/pileup/UL/2018/ZeroBias/gaussfits_All
scp ./gaussfits/*_eraA_test.png helfaham@server02.fynu.ucl.ac.be:~/public_html/pileup/UL/2018/ZeroBias/gaussfits_eraA
scp ./gaussfits/*_eraB_test.png helfaham@server02.fynu.ucl.ac.be:~/public_html/pileup/UL/2018/ZeroBias/gaussfits_eraB

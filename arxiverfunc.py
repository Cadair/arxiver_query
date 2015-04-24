#!/anaconda/bin/python
import urllib
import os
import sys
import random
from numpy import *
from scipy import misc
from matplotlib import rc
rc('text', usetex=True)
rc('font',**{'family':'serif','serif':['serif']})
import matplotlib.pyplot as pl
import unicodedata
import re
import time
import logging


def arxiverprocess(idname):

    # Make and delete temp dir
    os.system('rm -rf temp')
    os.system('mkdir temp')

    #idname = "1306.3227"

    logging.info('PROCESSING PAPER...')

    # If there are papers with problems, they can go here
    exceptions = []
    specfigs = []

    # Write out the IDs of papers where authors specify figures
    specfigout = open('specifiedfigs.txt','a')

    # START PROCESSING
    print idname

    arxiverflag = False
    ipip = -1

    # Create variables as necessary
    outname = 'temp/'+idname
    source = 'http://arxiv.org/e-print/'+idname
    linkformat = idname

    # Get tarball
    logging.info("Downloading paper...")
    out = open(outname,'w')
    out.write(urllib.urlopen(source).read())
    out.flush()

    # Comment out temporarily for testing
    os.system('tar --directory temp -xvf %s' % outname)

    ## Go hunting for arXiver comments in TeX files
    texfiles =  os.popen('find temp -name "*.tex"')
    for x in texfiles:
        logging.info("********")
        logging.info('Searching %s for author comments...' % x)

        # Process tex and look for comment
        for line in open(x.strip(),'rU'):
            if '@arxiver' in line:

                # Process comment
                specfigs = line.split('@arxiver{')[1].split('}')[0].split(',')

    	# Strip any whitespace from the figure names 14/08/14 VAM
    	for xfig in range(0,len(specfigs)):
    		specfigs[xfig] = specfigs[xfig].strip()
    	
        # Check fig length
        if len(specfigs) > 0:
            #print 'Figures specified by author found!'
            arxiverflag = True
            specfigout.write('%s %s\n' % (idname,','.join(specfigs)))
            specfigout.flush()

    # Convert eps to jpg
    # Check if jpg, or eps, or pdf, or png
    fignames = []
    figtype = None

    # Look for all types of images
    # PDF
    figs =  os.popen('find temp -name "*.pdf"')
    for x in figs:
        fignames.append(x.strip())

    figs =  os.popen('find temp -name "*.eps"')
    for x in figs:
        fignames.append(x.strip())

    figs =  os.popen('find temp -name "*.ps"')
    for x in figs:
        fignames.append(x.strip())

    figs =  os.popen('find temp -name "*.jpg"')
    for x in figs:
        fignames.append(x.strip())

    figs =  os.popen('find temp -name "*.png"')
    for x in figs:
        fignames.append(x.strip())

                    
    # Now that images are found
    figures = []

    if len(fignames) == 0:
        final = ['temp/arxiver.png']

    else:

        # For each figure in list
        for i in range(0,len(fignames)):
            fname = fignames[i]
            figtype = fname.split('.')[-1]

            # Ignore "whitespace" figures!
            if 'whitespace' in fname:
                continue

            # check for arxiverflag
            if arxiverflag == True:

                # Only consider figures of use
                if fname.split('/')[-1] not in specfigs:
                    continue

                else:
                    ipip+=1

            else:
                ipip = i

            if figtype == 'pdf':

                    # Convert to jpg
                    retval = 0
                    retval = os.system('pdfcrop %s' % fname)
                    if (retval < 0):
                        continue
                    retval = os.system('convert -resize 1024 -density 200 -background white -flatten %s temp/%s_f%i.jpg' % (fname.split('.pdf')[0]+'-crop.pdf',linkformat,(ipip+1)))
                    #retval = os.system('sips -Z 1024 -s format jpeg %s --out temp/%s_f%i.jpg' % (fname.split('.pdf')[0]+'-crop.pdf',linkformat,(ipip+1)))
                    if (retval < 0):
                        continue
                    figures.append('temp/%s_f%i.jpg' % (linkformat,(ipip+1)))
                    
            elif figtype == 'eps':

                    # Convert to jpg
                    retval = 0
                    retval = os.system('ps2pdf -dEPSCrop %s %s' % (fname,(fname.split('.eps')[0]+'.pdf')))
                    if (retval < 0):
                        continue
                    retval = os.system('pdfcrop %s' % (fname.split('.eps')[0]+'.pdf'))
                    if (retval < 0):
                        continue
                    retval = os.system('convert -resize 1024 -density 200 -background white -flatten %s temp/%s_f%i.jpg' % (fname.split('.eps')[0]+'-crop.pdf',linkformat,(ipip+1)))
                    #retval = os.system('sips -Z 1024 -s format jpeg %s --out temp/%s_f%i.jpg' % (fname.split('.eps')[0]+'-crop.pdf',linkformat,(ipip+1)))
                    if (retval < 0):
                        continue
                    figures.append('temp/%s_f%i.jpg' % (linkformat,(ipip+1)))
                    
            elif figtype == 'ps':
                
                    # Convert to jpg
                    retval = 0
                    retval = os.system('ps2eps -B -C < %s > temp/f%i.eps' % (fname,(ipip+1)))
                    if (retval < 0):
                        continue
                    retval = os.system('ps2pdf -dEPSCrop temp/f%i.eps temp/f%i.pdf' % ((ipip+1),(ipip+1)))
                    if (retval < 0):
                        continue
                    retval = os.system('pdfcrop temp/f%i.pdf' % (ipip+1))
                    if (retval < 0):
                        continue
                    retval = os.system('convert -resize 1024 -density 200 -background white -flatten temp/f%i-crop.pdf temp/%s_f%i.jpg' % ((ipip+1),linkformat,(ipip+1)))
                    #retval = os.system('sips -Z 1024 -s format jpeg temp/f%i-crop.pdf --out temp/%s_f%i.jpg' % ((ipip+1),linkformat,(ipip+1)))
                    if (retval < 0):
                        continue
                    figures.append('temp/%s_f%i.jpg' % (linkformat,(ipip+1)))

            elif figtype == 'png':

                    # Convert to jpg
                    retval = 0
                    retval = os.system('convert -resize 1024 -density 200 -background white -flatten %s temp/%s_f%i.jpg' % (fname,linkformat,(ipip+1)))
                    #retval = os.system('sips -Z 1024 -s format jpeg %s --out temp/%s_f%i.jpg' % (fname,linkformat,(i+1)))
                    if (retval < 0):
                        continue
                    figures.append('temp/%s_f%i.jpg' % (linkformat,(ipip+1)))

            elif figtype == 'jpg':

                    # Change name of jpg
                    os.system('mv %s temp/%s_f%i.jpg' % (fname,linkformat,(ipip+1)))
                    figures.append('temp/%s_f%i.jpg' % (linkformat,(ipip+1)))

    # redo figures array (accounting for missing fs that don't convert properly)
    lefigures = []
    for x in range(1,len(figures)+1):
        test = os.popen('ls temp/%s_f%i.jpg' % (linkformat,x))
        ys = []
        for y in test:
            ys.append(y.strip())
        if len(ys) > 0:
            lefigures.append(y.strip())


    # Default arxiver image if no images have converted correctly
    if len(lefigures) < 1:
        lefigures.append('arxiver.png')

    scores = {}

    for figure in lefigures:
            logging.info('Processing',figure,'...')
            
            img = misc.imread(figure, flatten=True)
            ix = shape(img)[0] 
            iy = shape(img)[1] 
            inpx = ix*iy

            # fourier transform
            ift = log10(abs(fft.fft2(img)))
            ift[0][0] = 0.0
            ift = fft.fftshift(ift)
            ftm = ift.max()
            ift = ift / ftm

            # New shape
            fx = shape(ift)[0] 
            fy = shape(ift)[1] 
            fnpx = fx*fy

            # Get score
            inf = ift.sum() / fnpx

            # Store the score
            if inf in scores.keys():
                scores[inf].append(figure)
            else:
                scores[inf] = [figure]

    # Process scores
    scores2 = scores.keys()[::]
    scores2.sort()

    # Get max,min,middle
    middle = int(len(scores)/2.0)

    # Deal with potential less figures
    final = []
    if len(scores2) > 3:
        final.append(scores[scores2[0]][0])
        final.append(scores[scores2[middle]][0])
        final.append(scores[scores2[-1]][0])
    elif len(scores2) == 3:
        final.append(scores[scores2[0]][0])
        final.append(scores[scores2[1]][0])
        final.append(scores[scores2[2]][0])
    elif len(scores2) == 2:
        final.append(scores[scores2[0]][0])
        final.append(scores[scores2[1]][0])
    elif len(scores2) == 1:
        final.append(scores[scores2[0]][0])

    # Create dictionary
    fdict = {}
    for i in range(0,len(final)):
        key = 'fig%i' % i
        val = final[i]
        fdict[key] = val

    return fdict




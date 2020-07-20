
## Written by Daniel Buscombe,
## MARDA Science
## daniel@mardascience.com

##> Release v1.3 (July 2020)

###===================================================
# import libraries
import sys, getopt, json, os
from numpy import any as npany
#
# PREDICT = True
#
# ##OS -- use CPU for prediction
# if PREDICT == True:
#    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

USE_GPU = True

if USE_GPU == True:
   ##use the first available GPU
   os.environ['CUDA_VISIBLE_DEVICES'] = '0' #'1'
else:
   ## to use the CPU (not recommended):
   os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

from sedinet_eval import *

#==============================================================
if __name__ == '__main__':

    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv,"h:c:w:")
    except getopt.GetoptError:
        print('python sedinet_predict.py -w weightsfile.hdf5 -c configfile.json')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Example usage: python sedinet_predict.py -c config/config_mattole.json -w mattole/res/mattole_simo_batch7_im512_512_2vars_pinball_aug.hdf5')
            sys.exit()
        elif opt in ("-c"):
            configfile = arg
        elif opt in ("-w"):
            weights_path = arg

    if not os.path.isfile(os.getcwd()+os.sep+weights_path):
        if not os.path.isfile(weights_path):
           print("Weights path does not exist ... exiting")
           sys.exit()

    try:
       # load the user configs
       with open(os.getcwd()+os.sep+configfile) as f:
          config = json.load(f)
    except:
       # load the user configs
       with open(configfile) as f:
          config = json.load(f)

    ###===================================================
    #csvfile containing image names and class values
    csvfile = config["csvfile"]
    #csvfile containing image names and class values
    res_folder = config["res_folder"]
    #folder containing csv file and that will contain model outputs
    name = config["name"]
    #name prefix for output files
    #convert imagery to greyscale or not
    dropout = config["dropout"]
    #dropout factor
    scale = config["scale"] #do scaling on variable
    greyscale = config['greyscale']

    try:
       numclass = config['numclass']
    except:
       numclass = 0

    try:
       greyscale = config['greyscale']
    except:
       greyscale = 'true'

    #output variables
    vars = [k for k in config.keys() if not npany([k.startswith('base'), k.startswith('MAX_LR'),
            k.startswith('MIN_LR'), k.startswith('DO_AUG'), k.startswith('SHALLOW'),
            k.startswith('res_folder'), k.startswith('train_csvfile'), k.startswith('csvfile'),
            k.startswith('test_csvfile'), k.startswith('name'),
            k.startswith('greyscale'), k.startswith('aux_in'),
            k.startswith('dropout'), k.startswith('N'),
            k.startswith('scale'), k.startswith('numclass')])]
    vars = sorted(vars)

    auxin = [k for k in config.keys() if k.startswith('aux_in')]

    if len(auxin) > 0:
       auxin = config[auxin[0]]   ##at least for now, just one 'auxilliary' (numerical/categorical) input in addition to imagery
       if len(vars) ==1:
          mode = 'miso'
       elif len(vars) >1:
          mode = 'mimo'
    else:
       if len(vars) ==1:
          mode = 'siso'
       elif len(vars) >1:
          mode = 'simo'

    print("Mode: %s" % (mode))
    ###==================================================

    csvfile = res_folder+os.sep+csvfile

    if (mode=='siso' or mode=='simo'):
       if numclass>0:
          estimate_categorical(vars, csvfile, res_folder,
                               dropout, numclass, greyscale, name, mode)
       else:
          if type(BATCH_SIZE) is list:
              for batch_size in BATCH_SIZE:
                  estimate_siso_simo(vars, csvfile, greyscale,
                                 dropout, numclass, scale, name, mode,
                                 res_folder, batch_size, weights_path) #
          else:
              estimate_siso_simo(vars, csvfile, greyscale,
                                 dropout, numclass, scale, name, mode,
                                 res_folder, BATCH_SIZE, weights_path) #

    # if (mode=='miso' or mode=='mimo'):
    #    estimate_miso_mimo(vars, csvfile, greyscale, auxin, weights_path, dropout)

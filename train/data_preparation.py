import argparse
import theano
import numpy as np
from parseData import parseData

parser = argparse.ArgumentParser(description='Bombr Game')

parser.add_argument('-O', action='store', dest='obser')
parser.add_argument('-R', action='store', dest='reward')
parser.add_argument('-S', action='store', dest='state')
parser.add_argument('-A', action='store', dest='action')
parser.add_argument('-Q', action='store', dest='seq')

Bombr_data = parseData(parser.parse_args())
Bombr_data.policy_train_data()
Bombr_data.getDataDistribution()
print (Bombr_data.act_Distribution)
Bombr_data.save_state_action()
Bombr_data.save_sequence()
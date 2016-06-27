from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Flatten, Reshape, Merge
from keras.layers.convolutional import Convolution2D
from keras.callbacks import EarlyStopping, ModelCheckpoint
import numpy as np
from DQN import DQN
BOMBR_COLUMN = 19
BOMBR_ROW = 19
FINALSTATE = np.full((19,19),3.0)
REWARD = 0
ACTION_CLASSES = 10

class bombrtrain:
   def __init__(self, option):
      self.obser_file = option.obser
      self.reward_file = option.reward
      self.models_init()
      self.data_init()
      self.parse_policy_train_data()
      self.create_all_action()

   def create_all_action(self):
      self.all_action = []
      for i in range(10):
         action = np.zeros(10,)
         action[i] = 1
         self.all_action.append(action)

   def parse_policy_train_data(self):
      self.states = []
      self.actions = []
      self.dqn_data = []
      last_state_action_pair = [FINALSTATE, np.zeros(10)]
      for i in range(len(self.sequence)):
         for j in range(len(self.sequence[i])):
            if(self.check_duplicate(last_state_action_pair, self.sequence[i][j])):
               self.states.append(self.sequence[i][j]['St'])
               self.actions.append(self.sequence[i][j]['At'])
               self.dqn_data.append(self.sequence[i][j])

   def check_duplicate(self, last_state_action_pair, data):
      action0 = np.zeros(10)
      action0[0] = 1
      if (data['St'] == last_state_action_pair[0]).all() and (data['At'] == last_state_action_pair[1]).all():
         return False
      #elif (data['At'] == action0).all():
      #   return False
      else:
         last_state_action_pair[0] = data['St']
         last_state_action_pair[1] = data['At']
         return True

   def models_init(self):
      #Todo
      self.model = Sequential()
      self.model.add(Reshape((1, BOMBR_ROW, BOMBR_COLUMN), input_shape=(BOMBR_ROW, BOMBR_COLUMN)))
      self.model.add(Convolution2D(64, 3, 3, activation='relu'))
      self.model.add(Convolution2D(64, 3, 3, activation='relu'))
      self.model.add(Dropout(0.25))
      self.model.add(Flatten())
      self.model.add(Dense(128, activation='relu'))
      self.model.add(Dropout(0.5))
      self.model.add(Dense(ACTION_CLASSES, activation='softmax'))
      open('model.json', 'w').write(self.model.to_json())

   def data_init(self):
      ObserFile = open(self.obser_file,'r')
      trash = ObserFile.readline()
      RewardFile = open(self.reward_file,'r')
      #every game sequence's data
      self.sequence = list()
      for r in RewardFile.readlines():
         strings = ObserFile.readline()
         ori_data = self.spliter(strings, "  ")
         #every time step's data
         data = list()
         for counter, d in enumerate(ori_data):
             timeslice = np.fromstring(d, sep = ",")
             timeslice = timeslice.astype(np.int32)
             action=np.zeros(10)
             action[timeslice[0]] = 1
             if len(timeslice) != 1:
                 state = np.reshape( timeslice[1:], (BOMBR_ROW, BOMBR_COLUMN))
                 info = {'St':state , 'Rt1':REWARD}
                 if counter != 0:
                     data[counter-1]['At']=action
                     data[counter-1]['St1']=state
             else:
                 data[counter-1]['At']=action
                 data[counter-1]['St1']=FINALSTATE
                 data[counter-1]['Rt1']=r
             data.append(info)
         self.sequence.append(data)

   def spliter(self, string, splitElm):
      data = string.split(splitElm)
      data.pop()
      return data

   def models_policy_train(self, epoch, out_weights_file, load_weights=False, in_weights_file=None):
      if load_weights:
         self.model.load_weights(in_weights_file)
      self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
      self.model.summary()
      callbacks = [
          EarlyStopping(monitor='val_loss', patience=5, verbose=0),
          ModelCheckpoint(filepath=out_weights_file, monitor='val_loss', save_best_only=True, verbose=0)
      ]
      self.model.fit(np.asarray(self.states), np.asarray(self.actions), batch_size=128, nb_epoch=epoch, verbose=1, validation_split=0.1, callbacks=callbacks)

   def test_predict(self, weights_file):
      self.model.load_weights(weight_file)
      self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
      for x in self.states:
         state = np.zeros((1, BOMBR_ROW, BOMBR_COLUMN))
         state[0] = x
         action = self.model.predict_classes(state)
         print (action)

   def dqnmodel_init(self):
      state_model = Sequential()
      state_model.add(Reshape((1, BOMBR_ROW, BOMBR_COLUMN), input_shape=(BOMBR_ROW, BOMBR_COLUMN)))
      state_model.add(Convolution2D(64, 3, 3, activation='relu'))
      state_model.add(Convolution2D(64, 3, 3, activation='relu'))
      state_model.add(Dropout(0.25))
      state_model.add(Flatten())
      state_model.add(Dense(128, activation='relu'))

      action_model = Sequential()
      action_model.add(Dense(32, input_shape=(10,), activation='relu'))
      action_model.add(Dense(32, activation='relu'))

      merged = Merge([state_model, action_model], mode='concat')
      final_model = Sequential()
      final_model.add(merged)
      final_model.add(Dense(200, activation='relu'))
      final_model.add(Dense(200, activation='relu'))
      final_model.add(Dense(1))
      open('dqnmodel.json', 'w').write(final_model.to_json())
      self.dqnmodel = DQN(final_model)

   def dqn_train(self):
      self.dqnmodel.train(self.dqn_data, self.all_action, 0.9)

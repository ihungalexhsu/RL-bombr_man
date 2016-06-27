from keras.models import model_from_json
from keras.optimizers import SGD
from keras.callbacks import EarlyStopping, ModelCheckpoint
import numpy as np
FINALSTATE = np.full((19,19),3.0)
BOMBR_COLUMN = 19
BOMBR_ROW = 19

class DQN:
   def __init__(self, model, load_weight=False, weight_file="../dqnmodel_weight.h5"):
      self.model = model
      json_string = model.to_json()
      self.evalute_model = model_from_json(json_string)
      if load_weight:
         self.model.load_weights(weight_file)
         self.evalute_model.load_weights(weight_file)

   def train(self, data, actions, gamma, batch_size=32, nb_epoch=10, 
         nb_iter=10, optimizer=SGD(lr=0.001, decay=1e-6, momentum=0.9, nesterov=True)):
      self.actions = actions
      self.optimizer = optimizer
      self.gamma = gamma
      states = [] #list of numpy array
      rewards = []
      actions = []
      next_states = []
      for d in data:
         states.append(d['St'])
         rewards.append(d['Rt1'])
         actions.append(d['At'])
         next_states.append(d['St1'])
      states = np.array(states)
      actions = np.array(actions)   

      self.model.compile(loss='mean_squared_error', optimizer=optimizer)
      self.model.summary()
      callbacks = [
         EarlyStopping(monitor='val_loss', patience=5, verbose=0),
         ModelCheckpoint(filepath="dqnmodel_weight.h5", monitor='val_loss', save_best_only=True, verbose=0)
      ]
      self.save_model_weight()
      for x in range(nb_epoch):
         print "All Date Epoch "+str(x)+"/"+str(nb_epoch)
         self.update_evalute_model_weight()
         self.update_target(rewards, next_states)
         print "Start fit"
         self.model.fit([states, actions], self.targets, batch_size, nb_iter, verbose=1, validation_split=0.1, callbacks=callbacks)
         print "Finish fit"
         self.save_model_weight()

   def update_target(self, reward, next_state):
      self.targets = []
      for i in range(len(reward)):
         if next_state[i] == FINALSTATE:
            self.targets.append(reward[i])
         else:
            a = self.get_maxQ(next_state[i])
            self.targets.append(reward[i]+self.gamma*a)
      self.targets = np.array(self.targets)

   def save_model_weight(self):
      self.model_weights = []
      for layer in self.model.layers:
         self.model_weights.append(layer.get_weights())

   def update_evalute_model_weight(self):
      i = 0
      for layer in self.evalute_model.layers:
         layer.set_weights(self.model_weights[i])
         i += 1
      self.evalute_model.compile(loss='mean_squared_error', optimizer=self.optimizer)

   def get_maxQ(self, state):
      maxQ = float('-inf')
      x = np.zeros((1, BOMBR_ROW, BOMBR_COLUMN))
      x[0] = state
      for action in self.actions:
         a = np.zeros((1, 10))
         a[0] = action
         Q = self.evalute_model.predict([x, a])
         maxQ = max(maxQ, Q[0][0])
      return maxQ

   def predict(self, data):
      return self.evalute_model.predict(data)
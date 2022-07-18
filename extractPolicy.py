def PrismPolicy(self, policyfile):
    self.policyfile = policyfile

def extractPolicy(initial_state, stateActionMap, stateEndStateMap):
    String_State = initial_state
    String_action = ""
    while (for key, value in stateEndStateMap):
        foundState = False
        previousState = foundState
        e = []
        for k1 in stateEndStateMap:
            e = list.append(k1)
            if ( k1 in stateEndStateMap):
                action = stateActionMap[k1]
                state = e
                foundState = True
            if (k1 not in stateEndStateMap):
                if ((len(stateEndStateMap[k1]) == 1) & (stateEndStateMap[k1]== False)):
                    action = stateActionMap[state]
                    state = stateEndStateMap[state]
                elif(len(stateEndStateMap[k1] > 1) & (k1 in stateEndStateMap == False)):
                    action = stateActionMap[state]
                    state = stateEndStateMap[state]











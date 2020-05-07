# featureExtractors.py
# --------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"Feature extractors for Pacman game states"

from game import Directions, Actions
import util

class FeatureExtractor:
    def getFeatures(self, state, action):
        """
          Returns a dict from features to counts
          Usually, the count will just be 1.0 for
          indicator functions.
        """
        util.raiseNotDefined()

class IdentityExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[(state,action)] = 1.0
        return feats

class CoordinateExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[state] = 1.0
        feats['x=%d' % state[0]] = 1.0
        feats['y=%d' % state[0]] = 1.0
        feats['action=%s' % action] = 1.0
        return feats

def closestFood(pos, food, walls):
    """
    closestFood -- this is similar to the function that we have
    worked on in the search project; here its all in one place
    """
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find a food at this location then exit
        if food[pos_x][pos_y]:
            return dist
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))
    # no food found
    return None

class SimpleExtractor(FeatureExtractor):
    """
    Returns simple features for a basic reflex Pacman:
    - whether food will be eaten
    - how far away the next food is
    - whether a ghost collision is imminent
    - whether a ghost is one step away
    """

    def getFeatures(self, state, action):
        # extract the grid of food and wall locations and get the ghost locations
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostPositions()

        features = util.Counter()

        features["bias"] = 1.0

        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        # count the number of ghosts 1-step away
        features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)

        # if there is no danger of ghosts then add the food feature
        if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
            features["eats-food"] = 1.0

        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist) / (walls.width * walls.height)
        features.divideAll(10.0)
        return features

class NewExtractor(FeatureExtractor):
    """
    Design you own feature extractor here. You may define other helper functions you find necessary.
    """
    def closestObject(self, pos, objects, walls):
        """
        closestObject -- finds the closest of a particular type of object
        """
        fringe = [(pos[0], pos[1], 0)]
        expanded = set()
        while fringe:
            pos_x, pos_y, dist = fringe.pop(0)
            if (pos_x, pos_y) in expanded:
                continue
            expanded.add((pos_x, pos_y))
            # if we find a ghost at this location then exit
            if (pos_x, pos_y) in objects:
                return dist
            # otherwise spread out from the location to its neighbours
            nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
            for nbr_x, nbr_y in nbrs:
                fringe.append((nbr_x, nbr_y, dist+1))
        # none of type object found
        return None

    def getFeatures(self, state, action):
        "*** YOUR CODE HERE ***"
        # extract the grid of food and wall locations and get the ghost locations
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostStates()
        capsules = state.getCapsules()

        features = util.Counter()

        features["bias"] = 1.0

        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        # count the number of ghosts 1-step away
        # features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g.getPosition(), walls) for g in ghosts)

        # count the number of capsules 1-step away
        features["#-of-capsules-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(c, walls) for c in capsules)

        # get legal locations 2 steps away
        two_steps = set()
        for neighbour in Actions.getLegalNeighbors((next_x, next_y), walls):
            for n_neighbour in Actions.getLegalNeighbors(neighbour, walls):
                if n_neighbour == (next_x, next_y):
                    continue
                two_steps.add(n_neighbour)

        # count the number of ghosts 2-step away
        features["#-of-ghosts-2-step-away"] = sum(ghost.getPosition() in two_steps for ghost in ghosts)

        # IDEA: eat the ghosts that are 1 steps away
        # How? If the ghosts are scared, then eat them
        # If ghosts are not scared, then go for capsules as top priority if it exists
        # Lastly then eat the food
        scared_ghosts = []
        for ghost in ghosts:
            if ghost.scaredTimer > 0:
                scared_ghosts.append(ghost.getPosition())

        scared_ghost_dist = self.closestObject((next_x, next_y), scared_ghosts, walls)
        food_dist = closestFood((next_x, next_y), food, walls)
        capsule_dist = self.closestObject((next_x, next_y), capsules, walls)
        if scared_ghost_dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            # add a balancing factor to favor chasing ghost instead of food
            chase_ghost = 0.9
            features["closest-scared-ghost"] = (1 - float(scared_ghost_dist) / (walls.width * walls.height)) * chase_ghost
            features["closest-food"] = float(food_dist) / (walls.width * walls.height) * (1 - chase_ghost)

        elif capsule_dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            chase_capsule = 0.6
            features["closest-capsule"] = float(capsule_dist) / (walls.width * walls.height) * chase_capsule
            features["closest-food"] = float(food_dist) / (walls.width * walls.height) * (1 - chase_capsule)
        else:
            features["closest-food"] = float(food_dist) / (walls.width * walls.height)

        if features["#-of-ghosts-2-step-away"]:
            neighbours = Actions.getLegalNeighbors((next_x, next_y), walls)
            for ghost in ghosts:
                if ghost.getPosition() in two_steps and ghost.scaredTimer > 0:
                    features["eats-ghost"] = 5.0
                    break
                # if ghost.getPosition() in neighbours and ghost.scaredTimer > 0:
                #     features["eats-ghost"] = 2.0
                #     break

        # if there is no danger of ghosts, then eat capsule before eating food
        if not features["#-of-ghosts-2-step-away"]:
            if features["#-of-capsules-1-step-away"]:
                features["eats-capsule"] = 1.0
            elif food[next_x][next_y]:
                features["eats-food"] = 1.0

        features.divideAll(10.0)
        return features


        

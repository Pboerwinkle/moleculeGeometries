molecules=[[[0, 0, 20], 12], [[0, 0, 7], 3], [[0, -50, -6], 4], [[0, 0, -20], 5]] #[horizontal, depth, vertical] position of center, number of bonded atoms
bondDist=4#how close outer atoms want to be to the central atom
bondSpringConst=50
pointRepulsion=1000#the charge of the atoms is 1, so it kind of makes sense for this to be high?
shellError=4#leniency in shell drawing(small number=low leniency)
screenWidth=900
screenScale=16#I set a lot of constants(like atom mass, atom charge, gravitational constant, etc) to 1 for simplicity, so the constants I did set would be a lot larger if I didn't scale it
velocityDamping = 0.03
turnRate=1/8#multiplied by pi, per second (independent of framerate)
framerate=30#no, simulation speed is not independent of framerate, I sincerely apologise
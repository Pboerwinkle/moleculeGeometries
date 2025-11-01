import math as m
import numpy as np
import pygame
import pygame.gfxdraw
import config
pygame.init()
clock = pygame.time.Clock()

molecules=config.molecules
bondDist=config.bondDist
bondSpringConst=config.bondSpringConst
pointRepulsion=config.pointRepulsion
shellError=config.shellError
screenWidth=config.screenWidth
offset=screenWidth//2
screenScale=config.screenScale
velocityDamping = 1-config.velocityDamping
turnRate=m.pi*config.turnRate
framerate=config.framerate

screenSize = (screenWidth, screenWidth)
screen = pygame.display.set_mode(screenSize)
viewAngle=0
numPoints = 0
Molecules = []
#count total points
for molecule in molecules:
    numPoints+=molecule[1]+1
Points = np.zeros((numPoints, 3))

def pointDiff(p1, p2):
    return np.array([p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]])

class Molecule:
    def __init__(self, center, linkStart, numBonds):
        self.linkStart = linkStart
        self.numBonds = numBonds
        #assign initial values for the points owned by this molecule
        for i in range(numBonds):
            Points[linkStart+i] = [center[0]+(i-numBonds//2), center[1]+((-1)**i), center[2]+i]
        Points[linkStart+numBonds]=center
        self.velocities = np.zeros((numBonds,3))
        self.closePoints = np.zeros((numBonds, numBonds))

    def accelPoints(self):
        myPoints = np.array(Points[self.linkStart:self.linkStart+self.numBonds])
        center = Points[self.linkStart+self.numBonds]

        netForces=np.zeros((self.numBonds, 3))
        closePoints = np.zeros((self.numBonds, self.numBonds))
        for point1 in range(len(myPoints)):
            #connect each point with a spring to the center
            centerDiff = pointDiff(center, myPoints[point1])
            distRatio=bondDist/m.sqrt(centerDiff[0]**2+centerDiff[1]**2+centerDiff[2]**2)
            netForces[point1,]+=(centerDiff*distRatio-centerDiff)*bondSpringConst
            closeDist = m.inf
            #push each point away from other points
            for point2 in range(len(myPoints)):
                if point1 == point2:
                    continue
                diff = pointDiff(myPoints[point2], myPoints[point1])
                dist = m.sqrt(diff[0]**2+diff[1]**2+diff[2]**2)
                distRatio = (1/(dist**2))/dist
                netForces[point1,]+=diff*distRatio*pointRepulsion

                #find close points to draw lines to
                if round(dist/shellError)*shellError < closeDist:
                    closeDist = round(dist/shellError)*shellError
                    closePoints[point1] = np.zeros(self.numBonds)
                    closePoints[point1,point2] = 1
                elif round(dist/shellError)*shellError == closeDist:
                    closePoints[point1,point2] = 1
        self.closePoints = closePoints.copy()

        self.velocities[:,]+=netForces[:,]/framerate
        self.velocities[:,]*=velocityDamping

        myPoints[:,]+=self.velocities[:,]/framerate

        #write points to main array
        for i in range(len(myPoints)):
            Points[self.linkStart+i]=myPoints[i].copy()

    def drawRequests(self):
        requests = []
        #send requests based on close points
        for i in range(len(self.closePoints)):
            for j in range(len(self.closePoints[i])):
                if self.closePoints[i,j] == 1:
                    requests.append([self.linkStart+i, self.linkStart+j])
        return requests

#create molecules
numPoints=0
for molecule in molecules:
    Molecules.append(Molecule(molecule[0], numPoints, molecule[1]))
    numPoints+=molecule[1]+1

#rotate points by an angle
def rotPoints(points, angle):
    newPoints = np.zeros((len(points), len(points[0])))
    newPoints[:,0] = points[:,0]*m.cos(angle)-points[:,1]*m.sin(angle)
    newPoints[:,1] = points[:,1]*m.cos(angle)+points[:,0]*m.sin(angle)
    newPoints[:,2] = points[:,2]
    return newPoints

#project points onto the screen space
def projectPoints(points):
    newPoints = np.zeros((len(points), 2))
    newPoints[:,0] = points[:,0]*(1+points[:,1]*screenScale/screenWidth/2)*screenScale+offset
    newPoints[:,1] = -points[:,2]*(1+points[:,1]*screenScale/screenWidth/2)*screenScale+offset
    newPoints = np.round(newPoints).astype(int)
    return newPoints

while True:
    clock.tick(framerate)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    #turn view angle
    viewAngle+=turnRate/framerate
    if viewAngle >= 2*m.pi:
        viewAngle -= 2*m.pi

    requests = []
    for molecule in Molecules:
        molecule.accelPoints()
        requests.extend(molecule.drawRequests())

    finalPoints = rotPoints(Points, viewAngle)
    finalPoints = projectPoints(finalPoints)

    #draw stuff
    screen.fill((0, 0, 0))
    for point in finalPoints:
        pygame.gfxdraw.filled_circle(screen, point[0], point[1], 2, (255, 0, 0))
    for request in requests:
        pygame.gfxdraw.line(screen, *finalPoints[request[0]], *finalPoints[request[1]], (0, 255, 0))
    pygame.display.flip()
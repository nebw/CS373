#visualization code by berthy424 and Marcello79

from Tkinter import *
from impl import *

from time import sleep

#***************************************
class DispParticleFilter(Tk):

    '''frameLength is the delay between two frames, i.e. two steps of the filter'''
    def __init__(self, motions, N=1000, frameLength = 0.1, displayRealRobot = True, displayGhost = False ):
        Tk.__init__(self)
        self.title( 'Diplay Particle Filter CS373-HW03.06')
        self.motions = motions        
        self.N = N

        self.frameLength = frameLength
        self.displayRealRobot = displayRealRobot        
        self.displayGhost = displayGhost
        #init particle filter
        self.initFilter()
        # Drawing
        self.margin = 130                                  # margin
        self.zoom_factor = 2                                # zoom factor
        self.playing = False
        self.can = DisplayParticles ( self.margin, self.zoom_factor )
        self.can.configure(bg ='ivory', bd =2, relief=SUNKEN)
        self.can.pack(side =TOP, padx =5, pady =5)
        self.can.draw_all(self.p, self.robot, self.displayRealRobot, self.displayGhost)
        #Buttons
        self.buttonReset = Button(self, text ='Reset', command =self.resetFilter)
        self.buttonReset.pack(side =LEFT, padx =5, pady =5)
        self.buttonNext = Button(self, text ='Next step', command =self.nextStep)
        self.buttonNext.pack(side =LEFT, padx =5, pady =5)
        self.buttonPlay = Button(self, text ='Play', command =self.play)
        self.buttonPlay.pack(side =LEFT, padx =5, pady =5)
        self.buttonPause = Button(self, text ='Pause', command =self.pause)
        self.buttonPause.pack(side =LEFT, padx =5, pady =5)    
        self.buttonPause.configure(state=DISABLED)         
        #Label
        textLabel = 'Current state = ' + str(self.actualState+1) + '/' + str(len(motions))
        self.label = Label(self, text = textLabel )
        self.label.pack(side = BOTTOM, padx =5, pady =5)

    def resetFilter(self):
        self.pause()

        self.initFilter()
        #Replot all
        self.can.draw_all(self.p, self.robot, self.displayRealRobot, self.displayGhost)

    def initFilter (self):

        #New Robot's position
        self.robot = robot(init=1)
        self.robot.set_noise(bearing_noise, steering_noise, distance_noise)

        # Make particles            
        self.p = []                     # p : particles set
        for i in range(self.N):
            r = robot()
            r.set_noise(bearing_noise, steering_noise, distance_noise)
            self.p.append(r)
        # --------------
        self.actualState = 0

    def nextStep (self, event=None):
        self.actualState = self.actualState + 1
        if self.actualState < len(self.motions):
            #Label
            stateString = 'Actual state = ' + str(self.actualState+1) + '/' + str(len(motions))
            self.label.configure( text = stateString )
            # motion update (prediction)
            if(random.random() <= 0.90):
              self.robot = self.robot.move(self.motions[self.actualState])
            else:
              self.robot = robot(init=1)
            self.can.draw_all(self.p, self.robot, self.displayRealRobot, self.displayGhost)
            self.update()
            sleep(self.frameLength)
            p2 = []
            for i in range(self.N):
                p2.append(self.p[i].move(self.motions[self.actualState]))
            self.p = p2
            self.can.draw_all(self.p, self.robot, self.displayRealRobot, self.displayGhost)
            self.update()
            sleep(self.frameLength)
            # measurement update
            w = []
            Z = self.robot.sense()
            for i in range(self.N):
                w.append(self.p[i].measurement_prob( Z ))
            # resampling
            p3 = []
            index = int(random.random() * self.N)
            beta = 0.0
            mw = max(w)
            for i in range(int(0.90 * self.N)):
                beta += random.random() * 2.0 * mw
                while beta > w[index]:
                    beta -= w[index]
                    index = (index + 1) % self.N
                p3.append(self.p[index])
            for i in range(self.N - int(0.90 * self.N)):
                r = robot()
                r.set_noise(bearing_noise, steering_noise, distance_noise)
                p3.append(r)
            self.p = p3
            #Replot all
            self.can.draw_all(self.p, self.robot, self.displayRealRobot, self.displayGhost)
            return True
        else:
            return False

    def play (self, event=None):
        self.playing = True
        self.buttonPause.configure(state=NORMAL)  
        self.buttonNext.configure(state=DISABLED) 
        self.buttonPlay.configure(state=DISABLED) 
        while self.playing:
            if self.nextStep() == False:
                self.pause(event)
                self.buttonPlay.configure(state=DISABLED)  
                self.buttonNext.configure(state=DISABLED)                 
                break
            self.update()
            sleep(self.frameLength)

    def pause (self, event=None):
        self.playing = False
        self.buttonPause.configure(state=DISABLED)  
        self.buttonNext.configure(state=NORMAL) 
        self.buttonPlay.configure(state=NORMAL)

class DisplayParticles(Canvas):

    def __init__(self, margin, zoom_factor ):
        Canvas.__init__(self)
        #self.p = p
        self.margin = margin
        self.zoom_factor = zoom_factor
        self.larg = (2*margin + world_size) * zoom_factor
        self.haut = self.larg
        self.configure(width=self.larg, height=self.haut )
        self.larg, self.haut = (2*margin + world_size) * zoom_factor, (2*margin + world_size) * zoom_factor
        # Landmarks
        self.landmarks_radius = 2
        self.landmarks_color = 'green'
        # Particles
        self.particle_radius = 1
        self.particle_color = 'red'
        # Robot
        self.robot_radius = 4
        self.robot_color = 'blue'
        self.ghost_color = None

    def draw_all(self, p, realRob, displayRealRobot, displayGhost):
        #print len(p)
        self.configure(bg ='ivory', bd =2, relief=SUNKEN)
        self.delete(ALL)
        self.p = p
        self.plot_particles()

        if displayGhost:
            ghost = get_position(self.p)
            self.plot_robot( ghost[0], ghost[1], ghost[2], self.robot_radius, self.ghost_color)
        self.plot_landmarks( landmarks, self.landmarks_radius, self.landmarks_color )

        if displayRealRobot:
            self.plot_robot( realRob.x, realRob.y, realRob.orientation, self.robot_radius, self.robot_color)

    def plot_landmarks(self, lms, radius, l_color ):
        for lm in lms:
            x0 = (self.margin + lm[1] - radius) * self.zoom_factor
            y0 = (self.margin + lm[0] - radius) * self.zoom_factor
            x1 = (self.margin + lm[1] + radius) * self.zoom_factor
            y1 = (self.margin + lm[0] + radius) * self.zoom_factor
            self.create_oval( x0, y0, x1, y1, fill = l_color )

    def plot_particles(self):
        for particle in self.p:
            self.draw_particle( particle, self.particle_radius, self.particle_color )

    def draw_particle(self, particle, radius, p_color):
        #x0 = (self.margin + particle.x - radius) * self.zoom_factor
        #y0 = (self.margin + particle.y - radius) * self.zoom_factor
        #x1 = (self.margin + particle.x + radius) * self.zoom_factor
        #y1 = (self.margin + particle.y + radius) * self.zoom_factor
        #self.create_oval( x0, y0, x1, y1, fill = p_color )
        x2 = (self.margin + particle.x) * self.zoom_factor
        y2 = (self.margin + particle.y) * self.zoom_factor
        x3 = (self.margin + particle.x + 2*radius*cos(particle.orientation)) * self.zoom_factor
        y3 = (self.margin + particle.y + 2*radius*sin(particle.orientation)) * self.zoom_factor
        self.create_line( x2, y2, x3, y3, fill = p_color, width =self.zoom_factor,
                          arrow=LAST, arrowshape=(2*self.zoom_factor,
                                                  3*self.zoom_factor,
                                                  1*self.zoom_factor) )

    def plot_robot(self, x,y, orientation, radius, r_color):
        x0 = (self.margin + x - radius) * self.zoom_factor
        y0 = (self.margin + y - radius) * self.zoom_factor
        x1 = (self.margin + x + radius) * self.zoom_factor
        y1 = (self.margin + y + radius) * self.zoom_factor
        self.create_oval( x0, y0, x1, y1, fill = r_color )
        x2 = (self.margin + x) * self.zoom_factor
        y2 = (self.margin + y) * self.zoom_factor
        x3 = (self.margin + x + 2*radius*cos(orientation)) * self.zoom_factor
        y3 = (self.margin + y + 2*radius*sin(orientation)) * self.zoom_factor
        self.create_line( x2, y2, x3, y3, fill = r_color, width =self.zoom_factor, arrow=LAST )

#**************************************************

if __name__ == "__main__":
    #motions  ( here copy of the dataset in hw3-6 )
    number_of_iterations = 500
    motions = [[2. * pi / 20, 12.] for row in range(number_of_iterations)]

    #Display window
    wind = DispParticleFilter ( motions, 1000, displayRealRobot = True, displayGhost = True )
    wind.mainloop()
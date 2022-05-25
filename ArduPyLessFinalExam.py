from vpython import *
import _thread
import serial

roomX=12
roomY=10
roomZ=16
wallT=.5
wallColor=vector(1,1,1)
wallOpacity=.8
frontOpacity=.1
marbleR=.5
brokeballColor= vector(1,0,0)
ballColor=vector(.5,0,1)
blockerColor=vector(.2,.2,1)

scene= canvas(width=800, height=550, title='Pong in 3D in a box')

arduinoData=serial.Serial('/dev/ttyACM0', 115200) #<--- Change to your own Arduino Port and baud rate!

# dedicated thread function to control the joystick/blocker
def cntrl_blocker(threadName):
    global threadkill #<global variable to properly exit the thread
    global xpos
    global ypos #<--global variables so that both threads can access the x & y position of the blocker
    while True: 
        if threadkill == True:
            break
        if(arduinoData.inWaiting()!=0):
            dataPacket=arduinoData.readline()
            dataPacket=str(dataPacket,'utf-8')
            dataPacket=dataPacket.strip('\r\s\n')
            triPosit = dataPacket.split(';')
            if triPosit[0]!="":
                xpos=float((int(triPosit[0])-500)/100)
                ypos=float((int(triPosit[1])-500)/100)
                xpos=xpos*-1
                ypos=ypos*-1
                myBlocker.pos=vector(xpos, ypos, roomZ/2)
    pass
    print("successfully exited thread")
    _thread.exit()
    

myFloor=box(size=vector(roomX, wallT, roomZ), pos=vector(0, -(roomY/2),0), color=wallColor, opacity=wallOpacity)
myceiing=box(size=vector(roomX, wallT, roomZ), pos=vector(0, (roomY/2), 0), color=wallColor, opacity=wallOpacity)
leftWall=box(size=vector(wallT, roomY, roomZ), pos=vector(-roomX/2,0,0), color=wallColor, opacity=wallOpacity)
rightWall=box(size=vector(wallT, roomY, roomZ), pos=vector(roomX/2,0,0), color=wallColor, opacity=wallOpacity-.3)
backWall=box(size=vector(roomX, roomY, wallT), pos=vector(0, 0, -(roomZ/2)-wallT/2), color=wallColor, opacity=wallOpacity)
marble=sphere(color=ballColor,radius=marbleR)

marbleX=0
marbleY=0
marbleZ=0

deltaX=.1
deltaY=.1
deltaZ=.1

xpos=0
ypos=0
zpos=0

ballspeed = 20
yourScore = 0

myBlocker=box(size=vector(roomX/5, roomY/5, wallT), pos=vector(0, 0, roomZ/2), color=blockerColor, opacity=wallOpacity-.4)
topLabel=label(text="Score: " + str(yourScore), fontsize=26, box=False, pos=vector(0, roomY + .3, 0))

# start the thread that controls the blocker
try:
    threadkill = False
    _thread.start_new_thread(cntrl_blocker, ("blockerThread",))
except:
    print('Unable to start thread')

#start the loop that controls the rest of the game
while True:
    rate(ballspeed)
    marbleX=marbleX+deltaX
    marbleY=marbleY+deltaY
    marbleZ=marbleZ+deltaZ

    if marbleX+marbleR>(roomX/2 -wallT/2) or marbleX-marbleR<(-roomX/2 + wallT/2 ):
        deltaX=deltaX*(-1)
    if marbleY+marbleR>(roomY/2 -wallT/2) or marbleY-marbleR<(-roomY/2 + wallT/2):
        deltaY=deltaY*(-1)
    if marbleZ-marbleR<(-roomZ/2 + wallT/2):
        deltaZ=deltaZ*(-1)
    if marbleZ+marbleR>(roomZ/2 -wallT/2):
        if marbleX < xpos+roomX/10+marbleR and marbleX>xpos-roomX/10-marbleR and marbleY<ypos+roomY/10+marbleR and marbleY>ypos-roomY/10-marbleR:
            yourScore=yourScore +1
            deltaZ=deltaZ*(-1)
        else:
            yourScore=yourScore-1
            marble.pos=vector(marbleX,marbleY,marbleZ)
            marble.color = brokeballColor
            sleep(3)
            marble.color = ballColor
            marbleX=0
            marbleY=0
            marbleZ=0
            deltaZ=deltaZ*(-1)

    topLabel.text = "Score: " + str(yourScore)
    marble.pos=vector(marbleX,marbleY,marbleZ)

    if yourScore <0:
        ballspeed = 10
    if yourScore >0:
        ballspeed =20
    if yourScore > 2: #<-- The ball picks up speed as your score increases
        ballspeed = 30
    if yourScore > 4:
        ballspeed = 40
    if yourScore > 7:
        ballspeed = 50
    if yourScore > 9: #< -- This game ends when you block the ball ten times
        topLabel.text ="You Win!!"
        threadkill = True
        sleep(5) # waits five seconds to kill the other thread before exit
        break
    pass

scene.delete()
exit()


    

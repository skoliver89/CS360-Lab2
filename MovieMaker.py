#------------------------------------------------------------------------------------------------------------#
# Lab # 2 Python for POV-Ray Animations																		 #
# CS 360 MTWR @ 1400-1450 w/ Mr. Becka Morgan (Fall 2016)													 #
# Due: 10/28/2016 @ 2355																					 #
# Author: Stephen K Oliver (V00324155)																	 	 #
# Version: 10/26/2016 : 1935																				 #
#																											 #
# ABOUT: Use Python scripts to modify a Pov-Ray scene and encode the images into movies               		 #
# 	PART I : Camera pan  																					 #
#	PART II: Moving objects and creating new ones															 #
#------------------------------------------------------------------------------------------------------------#
import os
import sys
import re
import math

# Open the base (original) POV file and retrun the SDL code within as a string.
def getBaseFile (path):
	fin = open(path)
	sdl = fin.read()			# Read the file into a string
	fin.close()
	return sdl					# Return the str containing POV SDL for later use

# Create/Overwrite a temp file with modified SDL to create the next image of our movie
def createNewFile (sdl_new):
	fileName = 'tmp.pov'		# Name of new POV file to be created
	fout = open(fileName, 'w')
	fout.write(sdl_new)			# Write the new SDL code to our new POV file
	fout.close()

# Run POV on some POV SDL and render it into a .png image (Windows10 Command Prompt)
def povCommand(fileName, imgName):
	if not os.path.exists('./tmp'):
		os.system('mkdir tmp')
	pov_cmd = 'C:/"Program Files"/POV-Ray/v3.7/bin/pvengine.exe +I%s +O%s -D -V +A +H720 +W1280'
	cmd = pov_cmd % (fileName, imgName)
	os.system(cmd)
	os.system('move /Y ' + imgName + ' tmp')
	os.system('cls')
	
# Encode the .png files into a movie of .avi format (protip: use VLC for playback)
# Encoder used: mencoder http://www.mplayerhq.hu/design7/news.html
# NOTE: mencoder is added to system environment so that you can just use 'mencoder' in CMD
def encodeMovie(movieName):
	print 'Encoding Movie...'
	os.system( 'mencoder ./tmp/tmp*.png -mf type=png:fps=25 -ovc lavc -lavcopts vcodec=msmpeg4:vbitrate=2160000:keyint=5:vhq -o '+ movieName +'.avi' )

#-----PART I Functions(Not perfect yet, hopefuly close enough)-----#

# makes changes to the pov sdl on camera x & z location
def changeCameraLocation(sdl, x, y, z):
	old_regex = r'location <([-]*\d*\.*\d*),([-]*\d*\.*\d*),([-]*\d*\.*\d*)>'
	match = re.search(old_regex,sdl)
	if match:
		new_regex = r'location <' + str(x) + ',' + str(y) + ',' + str(z) + r'>'
		sdl = re.sub(old_regex, new_regex, sdl)
	return sdl

# Modify the sdl string to rotate the camera around our object.
# rotation algorithm inspiration here: http://www.mathopenref.com/coordcirclealgorithm.html
def pan(sdl, numRotations):
	new_sdl = ''
	completedRotations = 0	
	step = 0.01					# amount to add to theta each time (degrees)
	tFrames = (int(numRotations) * (3.60/step))
	frame = 1
	#---------------------------------Spiral Up/Down Variables----------------------------------------#
	yMax = 5.0					# Highest camera point
	yMin = 0.0					# Lowest camera point
	yRange = (yMax - yMin)		# Range of camera movement
	yInc = (yRange/(3.60/step))	# Amount for the camera to move each image
	y = None					# Initialize variable for y value
	#-------------------------------------------------------------------------------------------------#
	while completedRotations < int(numRotations):
		#-------------------------------------Rotation Variables--------------------------------------#
		theta = 0.0				# angle that will be increased each loop
		h = 0.0					# x-coordinate of camera path (circle) center
		k = 0.0					# z-coordinate of camera path (circle) center
		r = 5.0					# radius of camera path
		while theta <= 3.60:
			x = h + r*math.cos(theta)		# Calculate x value (rotation)
			z = k - r*math.sin(theta)		# Calculate z value (rotation)
			if y == None:
				y = yMin				# Start with camera at lowest point
			elif completedRotations%2 == 0:
				y += yInc				# Spiral Up
			else:
				y -= yInc				# Spiral Down
			theta += step		
			sdl = changeCameraLocation(sdl, x, y, z)
			createNewFile(sdl)
			imgName = 'tmp%05d.png' % frame
			povCommand('tmp.pov', imgName)
			percentDone = round((float(frame) / float(tFrames)*100), 2)
			print 'Rendering Movie: ' + str(percentDone) + '%'
			frame += 1
		completedRotations += 1
	
	encodeMovie('panMovie')
	os.system('cls')
	os.system('del tmp.pov')								# clean up tmp pov file!
	os.system('rmdir tmp /S /Q')							# clean up tmp folder!
	print 'Rendering Movie: FINISHED!!'
	
#-----------------------------------------PART II FUNCTIONS------------------------------------------------#
#
def createSphere(sdl,x,y,z,rad,r,g,b):
	sphere = '\nsphere\n{\n  <%f,%f,%f>,%f\n  pigment { rgb <%d,%d,%d> }\n}' %(x,y,z,rad,r,g,b)
	sdl += sphere
	return sdl
#
def moveSphere(sdl, theta):		#Keep it simple, orbit the original object
	h = 0.0
	k = 0.0
	rad = 2
	x = h + rad*math.cos(theta)		# Calculate x value (rotation)
	y = 0.5							# Add equation to change sphere height (if desired) else, 0
	z = k - rad*math.sin(theta)		# Calculate z value (rotation)
	# ([-]*\d*\.*\d*)
	old_regex = r'\nsphere\n{\n  <([-]*\d*\.*\d*),([-]*\d*\.*\d*),([-]*\d*\.*\d*)>,([-]*\d*\.*\d*)\n  pigment { rgb <([-]*\d*\.*\d*),([-]*\d*\.*\d*),([-]*\d*\.*\d*)> }\n}' 
	match = re.search(old_regex,sdl)
	if match:
		#print "Match!"
		(r,g,b) = (float(match.group(5)), float(match.group(6)), float(match.group(7)))
		(r,g,b) = colorFade(r,g,b)
		print 'rgb value: ' + str((r,g,b))
		new_regex = r'\nsphere\n{\n  <' + str(x) + ',' + str(y) + ',' + str(z) + '>,0.25\n  pigment { rgb <'+ str(r) +','+ str(g) +','+ str(b) +'> }\n}'
		sdl = re.sub(old_regex, new_regex, sdl)
	#else:
		#print "NO Match!"s
	return sdl

# Rad color changes yo!
# Original Algorithm here: http://codepen.io/Codepixl/pen/ogWWaK/
def colorFade(r,g,b):
	step = .01
	if r > 0 and b == 0:
		r -= step
		g += step
	elif g > 0 and r == 0:
		g -= step
		b += step
	elif b > 0 and g == 0:
		r += step
		b -= step
	return (r,g,b)

# Overall animation function (i.e., the master controler for the animation/render)
def animate (sdl):
	povCommand('base.pov', 'tmp00000.png')
	sphVals = {'x':-1.5, 'y':0, 'z':-1.5, 'rad':0.25,'red':1, 'green':0, 'blue':0} # initial sphere vals
	sdl = createSphere(sdl, sphVals['x'],sphVals['y'],sphVals['z'],sphVals['rad'],sphVals['red'],sphVals['green'],sphVals['blue']) # our baby sphere is born!
	sdl = moveSphere(sdl, 0)		#put the new in starting position
	createNewFile(sdl)
	povCommand('tmp.pov', 'tmp00001.png')
	i = 2
	theta = 0.01
	step = 0.01
	while theta <= 10.00:
		sdl = moveSphere(sdl, theta)										
		createNewFile(sdl)													# Write to tmp.pov
		imgName = 'tmp%05d.png' %(i)
		povCommand('tmp.pov', imgName)										# Render the new image
		percentDone = i/(10.00/(step)) * 100
		print 'Rendering Movie: ' + str(round(percentDone,2)) + '%'
		print 'Working on frame #' + str(i)
		i += 1
		theta += step
	encodeMovie('animationMovie')
	os.system('cls')
	os.system('del tmp.pov')								# clean up tmp pov file!
	os.system('rmdir tmp /S /Q')							# clean up tmp folder!
	print 'Rendering Movie: FINISHED!!'
		
#Main method... 
def main():
	args = sys.argv[1:]

	if not args:
		print 'usage: [--pan #Rotations][--animate] file.pov'
		sys.exit(1)

	else:
		try:
			if args[0] == '--pan':
				sdl = getBaseFile(args[2])
				print "Panning with " + str(args[1]) + " Rotations!"
				pan(sdl, args[1])
				sys.exit(1)
			if args[0] == '--animate':
				sdl = getBaseFile(args[1])
				animate(sdl)
				sys.exit(1)
			else:
				print 'usage: [--pan #Rotations][--animate] file.pov'
				sys.exit(1)
		except IndexError, e:
			print 'usage: [--pan #Rotations][--animate] file.pov'
			sys.exit(1)
	
if __name__ == '__main__':
	main()

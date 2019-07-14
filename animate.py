import bpy  
from mathutils import Vector
from math import pi

DEG_TO_RAD = pi/180

####
#### Controls. All numerical values should be integers unless otherwise stated.
# The name of the ship object in the scene
shipname = "spacecomma"

# The starting point on the axis of movement (typically in the distance)
move_start = 75

# The end finishing point on the axis of movement (typically close up)
move_end = 0

#(set the above two equal to disable this effect)

# The number of keyframes we spend at the beginning moving along the axis of movement
move_incs = 48

# The number of degrees of rotation along each axis, per keyframe
x_rot_degrees = 10
y_rot_degrees = 15
z_rot_degrees = 20

# Keyframe interval. A keyframe is a frame in which we describe the scene in full,
# the animation engine generates the intermediate frames.
keyframe_interval = 10

# Maximum length the animation should last, counted in keyframes
max_keyframes = 144 # (=1 minute @24fps and keyframe inteval of 10)

# Maximum time the animation should repeat itself. Repeating occurs once movement along the z-axis
# has finished, and the combined x,y,z rotation value starts repeating old values. How long that takes
# depends on the inter-keyframe increment values chosen. Note this is why I have chosen degrees, if we used
# radians then the increment values would have to be irrational numbers for repititon to ever occur. In theory
# it is not necessary to render any more frames once the animation has entered repeat - it can be extended by
# copy and paste instead.
max_repeat_count = 0 


### End user controls


scene = bpy.context.scene

ship = scene.objects[shipname]


# start with frame 0
number_of_frame = 0  
keyframe_count = 0
repeat_count = 0
move_finished = False
move_finished_1 = False # Goes True one interation of the loop after move_finished goes True

# Work out how much the z position changes on each keyframe
move_increment = 1.0 * (move_end - move_start) / move_incs
move_location = move_start * 1.0

#Rotation start values, arbitrartily 0 0 0 
x_cur = 0
y_cur = 0
z_cur = 0

# Clear any animation data from a previous run
ship.animation_data_clear()

# Frame number for the end of the repeat loop, if this is still -1 at the end,
# then no repitition occurred.
repeat_loop_end = -1

while True: #until break

    # Apply rotation for the current key frame
    x_cur += x_rot_degrees             
    y_cur += y_rot_degrees             
    z_cur += z_rot_degrees

    #Radian values
    x_rad = x_cur * DEG_TO_RAD
    y_rad = y_cur * DEG_TO_RAD
    z_rad = z_cur * DEG_TO_RAD

    # Calculate the new location, if still moving
    if (not move_finished):
        move_location += move_increment
        
        # Test whether we have reached the end point of the move, accounting for
        # positive, negative or zero movement.
        
        if (move_increment == 0 or
            move_location > move_end and move_increment > 0
         or move_location < move_end and move_increment < 0):
            move_finished = True
            move_location = move_end
            
            # We have reached the end of the move...
            
            # Now capture the rotation values, this is the start of the repeat loop
            x_rot_repeat_start = x_cur % 360
            y_rot_repeat_start = y_cur % 360
            z_rot_repeat_start = z_cur % 360
            
            # Make a record of where the repeat loop starts
            repeat_loop_start = number_of_frame
            
    else: 
        move_finished_1 = True
            
    
    # Tell the scene which keyframe we are describing
    scene.frame_set(number_of_frame)

    # Set the location
    if (not move_finished_1):
        ship.location = (0,move_location,0)
        ship.keyframe_insert(data_path="location", index=-1)

    # Set the rotation
    ship.rotation_euler = (x_rad, y_rad, z_rad) 
    ship.keyframe_insert(data_path="rotation_euler", index=-1)

    if (keyframe_count > max_keyframes):
        break

    if (move_finished_1):
        # Check for the repeat condition
        if (x_cur % 360 == x_rot_repeat_start and
          y_cur % 360 == y_rot_repeat_start and
          z_cur % 360 == z_rot_repeat_start):
              repeat_count += 1
              
              # If this is the end of the first repeat loop, make a note of the frame number
              if (repeat_count == 1):
                  repeat_loop_end = number_of_frame
                  
              if (repeat_count > max_repeat_count):
                  break

    # Advance to the next keyframe
    number_of_frame += keyframe_interval
    keyframe_count += 1
    

print ("Did %d frames, %s keyframes" % (number_of_frame, keyframe_count))

if (repeat_loop_end > 0):
    print ("Repeat loop frames %d to %d" % (repeat_loop_start, repeat_loop_end))
else:
    print ("Didn't repeat")

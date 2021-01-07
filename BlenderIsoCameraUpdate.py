import bpy
import math

### Begin Tunable Parameters ###

# The number of units the tile will be
tile_size = 1

# Size In Blender of the unit tile
blender_unit_tile_size = 10

# If you have big decorations, you may need
# a bigger Image
add_pixels_to_top    = 0
add_pixels_to_bottom = 0
add_pixels_to_right  = 0
add_pixels_to_left   = 0


# The pixel size of the undecorated tile
undecorated_tile_pixel_width  = (tile_size * 60) - 2
undecorated_tile_pixel_height = tile_size * 30


### End Tunable Parameters ###


bender_tile_size = blender_unit_tile_size * tile_size


# The dimentions of the decorated tile
decorated_tile_pixel_width  = undecorated_tile_pixel_width + add_pixels_to_right + add_pixels_to_left
decorated_tile_pixel_height = undecorated_tile_pixel_height + add_pixels_to_top + add_pixels_to_bottom


## Setup Render Ouput
bpy.context.scene.render.resolution_x = decorated_tile_pixel_width
bpy.context.scene.render.resolution_y = decorated_tile_pixel_height
bpy.context.scene.render.film_transparent = True



## Setup Camera

# Figure out maximum Dimention as the Camera stuff scales realitive to that
if decorated_tile_pixel_width > decorated_tile_pixel_height:
   max_decorated_pixel_dimension = decorated_tile_pixel_width
else:
   max_decorated_pixel_dimension = decorated_tile_pixel_height
camera_unit_pixel = 1 / max_decorated_pixel_dimension

# I think my math is correct, but I need to do this otherwise the tile
# gets these strange jagged edges that make it look like it is bowing in 
# I have no idea why these are nessary, but they seem to be.
evil_camera_scale_scrub_factor            = 0.98
evil_camera_rotation_scrub_factor         = 1.005



# Compute Camera Angles
inverse_tile_ratio = undecorated_tile_pixel_height / undecorated_tile_pixel_width
iso_x_angle = math.acos(inverse_tile_ratio) * evil_camera_rotation_scrub_factor
iso_z_angle = math.radians(45)

# Compute Camera Translation Distance
camera_move_distance = bender_tile_size * 2 # Be really sure we are able to see everything


# Compute Camera Scale Information
blender_tile_width_at_angle = math.sqrt((bender_tile_size ** 2) + (bender_tile_size ** 2))
blender_units_per_pixel = blender_tile_width_at_angle / undecorated_tile_pixel_width
camera_width_ortho_scale = ((blender_tile_width_at_angle * evil_camera_scale_scrub_factor) + 
                            ((add_pixels_to_right + add_pixels_to_left) * blender_units_per_pixel))

if decorated_tile_pixel_width > decorated_tile_pixel_height:
   camera_ortho_scale = camera_width_ortho_scale
else:
   # Convert Width into height as all scale calculations are based on the largest image dimention
   camera_ortho_scale = camera_width_ortho_scale * (decorated_tile_pixel_height / decorated_tile_pixel_width)

# Compute Camera shift for decorations

camera_shift_x = (add_pixels_to_right - add_pixels_to_left)   * camera_unit_pixel  * 0.5
camera_shift_y = (add_pixels_to_top   - add_pixels_to_bottom) * camera_unit_pixel  * 0.5

cameraObject = bpy.data.objects['Camera']
cameraObject.data.type = 'ORTHO'
cameraObject.data.ortho_scale = camera_ortho_scale 

cameraObject.rotation_euler = (iso_x_angle, 0, iso_z_angle)


# I just guessed and checked here, I don't know why this works
cameraObject.location = ( math.sin(iso_z_angle) * math.sin(iso_x_angle) * camera_move_distance, 
                         -math.cos(iso_z_angle) * math.sin(iso_x_angle) * camera_move_distance, 
                          math.cos(iso_x_angle) * camera_move_distance)

# Shift are percentages of camera width
cameraObject.data.shift_x = camera_shift_x
cameraObject.data.shift_y = camera_shift_y

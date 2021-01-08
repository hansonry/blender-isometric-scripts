bl_info = {
    "name": "Isometric Tools",
    "blender": (2, 80, 0),
    "category": "Camera",
}

import bpy
import math
from bpy.props import (
    FloatProperty,
    IntProperty,
    StringProperty
)

def SetScreenSizeAndCameraPosition(blender_tile_size, 
                                   undecorated_tile_pixel_width,
                                   undecorated_tile_pixel_height,
                                   cameraObject,
                                   add_pixels_to_top = 0,
                                   add_pixels_to_right = 0,
                                   add_pixels_to_bottom = 0,
                                   add_pixels_to_left = 0,
                                   camera_distance_scale = 2):


   # The dimentions of the decorated tile
   decorated_tile_pixel_width  = undecorated_tile_pixel_width + add_pixels_to_right + add_pixels_to_left
   decorated_tile_pixel_height = undecorated_tile_pixel_height + add_pixels_to_top + add_pixels_to_bottom


   ## Setup Render Ouput
   bpy.context.scene.render.resolution_x = decorated_tile_pixel_width
   bpy.context.scene.render.resolution_y = decorated_tile_pixel_height
   #bpy.context.scene.render.film_transparent = True



   ## Setup Camera

   # Figure out maximum Dimention as the Camera stuff scales realitive to that
   if decorated_tile_pixel_width > decorated_tile_pixel_height:
      max_decorated_pixel_dimension = decorated_tile_pixel_width
   else:
      max_decorated_pixel_dimension = decorated_tile_pixel_height
   camera_unit_pixel = 1 / max_decorated_pixel_dimension


   # Map the lines of the square onto the center of pixels so we get
   # no distortion
   x1 = 0.5
   y1 = (undecorated_tile_pixel_height / 2) - 0.5
   x2 = (undecorated_tile_pixel_width  / 2) - 0.5
   y2 = 0.5
   m = (y1 - y2) / (x1 - x2)
   b = y1 - m * x1

   pixel_height = 2 * b
   pixel_width  = 2 * (-b) / m

   print("undecorated", undecorated_tile_pixel_width, undecorated_tile_pixel_height)
   print("ajusted", pixel_width, pixel_height)


   # Compute Camera Angles
   inverse_tile_ratio = pixel_height / pixel_width 
   iso_x_angle = math.acos(inverse_tile_ratio)
   iso_z_angle = math.radians(45)

   # Compute Camera Translation Distance
   camera_move_distance = blender_tile_size * camera_distance_scale


   # Compute Camera Scale Information
   pixel_correction_scale = undecorated_tile_pixel_width / pixel_width 
   blender_tile_width_at_angle = math.sqrt((blender_tile_size ** 2) + (blender_tile_size ** 2)) * pixel_correction_scale 
   blender_units_per_pixel = blender_tile_width_at_angle / undecorated_tile_pixel_width
   camera_width_ortho_scale = (blender_tile_width_at_angle  + 
                               ((add_pixels_to_right + add_pixels_to_left) * blender_units_per_pixel))

   if decorated_tile_pixel_width > decorated_tile_pixel_height:
      camera_ortho_scale = camera_width_ortho_scale
   else:
      # Convert Width into height as all scale calculations are based on the largest image dimention
      camera_ortho_scale = camera_width_ortho_scale * (decorated_tile_pixel_height / decorated_tile_pixel_width)

   # Compute Camera shift for decorations

   camera_shift_x = (add_pixels_to_right - add_pixels_to_left)   * camera_unit_pixel  * 0.5
   camera_shift_y = (add_pixels_to_top   - add_pixels_to_bottom) * camera_unit_pixel  * 0.5

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

class IsometricCameraPosition(bpy.types.Operator):
   """Isometric Camera Position"""
   bl_idname = "object.isometric_camera_position"
   bl_label = "Isometric Camera Position"
   #bl_space_type = 'VIEW_3D'
   #bl_region_type = 'UI'
   bl_options = {'REGISTER', 'UNDO'}
   

   blender_tile_size: FloatProperty(
      name="Blender Tile Size",
      description="Size of the tile in Blender Units",
      default=2,
      min=0, soft_min=0.001, soft_max=100)

   undecorated_tile_pixel_width  : IntProperty(
      name="Width (Pixels)",
      description="Width of a perfectly flat one unit isometric tile",
      default=64,
      min=0)
   undecorated_tile_pixel_height : IntProperty(
      name="Height (Pixels)",
      description="Height of a perfectly flat one unit isometric tile",
      default=32,
      min=0)

   add_pixels_to_top    : IntProperty(
      name="Add Top (Pixels)",
      description="Amount of pixels to add to the top of the image",
      default=0,
      min=0)
   add_pixels_to_bottom : IntProperty(
      name="Add Bottom (Pixels)",
      description="Amount of pixels to add to the Bottom of the image",
      default=0,      
      min=0)
   add_pixels_to_right  : IntProperty(
      name="Add Right (Pixels)",
      description="Amount of pixels to add to the Right of the image",
      default=0,      
      min=0)
   add_pixels_to_left   : IntProperty(
      name="Add Left (Pixels)",
      description="Amount of pixels to add to the Left of the image",
      default=0,      
      min=0)

   camera_distance_scale : FloatProperty(
      name="Camera Distance Scale",
      description="The distance of the camera is this times the Blender Tile Size",
      default = 2,
      step = 25,
      min = 0, soft_min=0.1)
      
   def execute(self, context):
      cameraObject = obj_camera = bpy.context.scene.camera
      SetScreenSizeAndCameraPosition(self.blender_tile_size,
                                     self.undecorated_tile_pixel_width,
                                     self.undecorated_tile_pixel_height,
                                     cameraObject,
                                     self.add_pixels_to_top,
                                     self.add_pixels_to_right,
                                     self.add_pixels_to_bottom,
                                     self.add_pixels_to_left,
                                     self.camera_distance_scale)
      return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(IsometricCameraPosition.bl_idname, icon='MESH_CUBE')
    
def register():
   bpy.utils.register_class(IsometricCameraPosition)
   bpy.types.VIEW3D_MT_view.append(menu_func)

def unregister():
   bpy.utils.unregister_class(IsometricCameraPosition)
   bpy.types.VIEW3D_MT_view.remove(menu_func)

if __name__ == "__main__":
   register()

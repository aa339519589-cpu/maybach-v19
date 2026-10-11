"""Portable lighting/camera switch embedded in master.blend.
In Blender Text Editor: choose PRESET below, then Run Script.
Uses only data already stored inside this BLEND. No external code or network.
"""
import bpy,json
PRESET='hero_front'  # hero_front, rear_studio, rear_daylight, side_profile, interior_front, interior_rear, reference_showroom
CAMERA_OVERRIDE=None  # e.g. 'MT6_CAM_REF03' for the photo03 camera

def activate_preset(key,camera=None):
 s=bpy.context.scene;presets=json.loads(s['MT6_presets'])
 if key not in presets:raise KeyError('Available presets: '+', '.join(presets))
 parts={o.name:(o.hide_render,o.hide_viewport) for o in bpy.data.objects if o.get('component')}
 original=set(json.loads(s['MT1_original_component_names']))
 added=set(json.loads(s['MT1_added_component_names']))
 assert len(original)==967 and added=={'MT4_Rear_left_sliding_belt_tongue','MT4_Rear_right_sliding_belt_tongue','MT4_Rear_center_low_visible_outer_cap'}
 assert set(parts)==original|added and len(parts)==970
 for o in s.objects:
  if o.get('MT6_owned') and o.type=='LIGHT':
   o.hide_render=o.get('MT6_preset')!=key
   if o.name.startswith('MT6_CABIN_INTERNAL_FILL') and o.data.energy<=0:o.hide_render=True
   o.hide_viewport=o.hide_render
 cyc=bpy.data.objects.get('MT6_PHYSICAL_CYCLORAMA')
 if cyc:cyc.hide_render=key in {'rear_daylight','side_profile'};cyc.hide_viewport=cyc.hide_render
 original=json.loads(s['MT6_legacy_stage_original_visibility']);viewport=json.loads(s['MT6_legacy_stage_original_viewport'])
 for name in json.loads(s['MT6_legacy_stage_exact_names']):
  o=bpy.data.objects[name];assert not o.get('component')
  o.hide_render=original[name] if key=='reference_showroom' else True
  o.hide_viewport=viewport[name] if key=='reference_showroom' else True
 p=presets[key];s.world=bpy.data.worlds[p['world']];s.camera=bpy.data.objects[camera or p['camera']]
 s.render.resolution_x,s.render.resolution_y=p['size'];s.render.resolution_percentage=100;s['MT6_active_preset']=key
 s['MT6_legacy_stage_mode']='REFERENCE_ORIGINAL_STAGE' if key=='reference_showroom' else 'HIDDEN_NONVEHICLE_STAGE'
 bpy.context.view_layer.update()
 assert parts=={o.name:(o.hide_render,o.hide_viewport) for o in bpy.data.objects if o.get('component')}
 return {'preset':key,'camera':s.camera.name,'resolution':[s.render.resolution_x,s.render.resolution_y]}

if __name__=='__main__':print(activate_preset(PRESET,CAMERA_OVERRIDE))

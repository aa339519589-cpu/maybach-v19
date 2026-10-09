"""Photo-only detail pass. The ten supplied photos are the visual authority.
Inferred small dimensions and unreadable screen text are recorded as unresolved.
"""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'refinement'));sys.path.insert(0,str(ROOT/'current-native-v14/master_shell'))
from detail_utils import material,mesh,tube,join,tag,cylinder,apply_modifiers
from split_door_frames import split_door_frames
S=bpy.context.scene;S.frame_set(1);report={}
def P(name):return bpy.data.materials[name].node_tree.nodes['Principled BSDF']
p=P('Vehicle deep blue metallic');p.inputs['Base Color'].default_value=(.0025,.0055,.018,1);p.inputs['Metallic'].default_value=.78;p.inputs['Roughness'].default_value=.18;p.inputs['Coat Weight'].default_value=.8
p=P('Vehicle satin black');p.inputs['Base Color'].default_value=(.003,.003,.003,1);p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.82;p.inputs['Coat Weight'].default_value=0
for m in bpy.data.materials:
 if m.name.startswith('INT silk beige semi-aniline leather'):m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.45,.37,.28,1)
p=P('DP titanium leather dashboard roll');p.inputs['Base Color'].default_value=(.044,.038,.033,1);p.inputs['Roughness'].default_value=.49
# Regenerate the existing watertight 20-hole disc using a gentler recess profile.
# The original generator is reused, not its historical visual reference claims.
src=(ROOT/'current-native-v14/master_shell/sculpt_reference_wheels.py').read_text().split('# Mirror caps')[0]
src=src.replace("ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))",'ROOT='+repr(str(ROOT/'current-native-v14')))
src=src.replace("(.75,.77,.79),1,.095","(.55,.57,.59),1,.24").replace('.0095*math.exp','.0040*math.exp').replace("'vent_recess_m':.0095","'vent_recess_m':.004")
ns={'__file__':__file__};exec(compile(src,'photo_wheel_profile','exec'),ns);report['wheels']=ns['report']
for o in S.objects:
 if 'Maybach 20-hole wheel' in o.name:o['reference']='Photo_01 and Photo_05';o['wheel_surface_revision']='ten-photo shallow vent depressions, 20 true openings'
# Keep optics behind the current cover, shorten the signature to three rising torches.
LED=bpy.data.materials['Lamp diffusing light guide'];CHROME=bpy.data.materials['Lamp vacuum-metallised reflector']
def sample(points,n=16):
 out=[]
 for i in range(len(points)-1):
  a,b,c,d=[Vector(points[max(0,min(len(points)-1,j))]) for j in [i-1,i,i+1,i+2]]
  for k in range(n):
   t=k/n;out.append(.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t**3))
 return out+[Vector(points[-1])]
for sign,label in [(-1,'Left'),(1,'Right')]:
 cover=bpy.data.objects[label+' headlamp clear cover'];cover.data.calc_loop_triangles();bvh=BVHTree.FromPolygons([cover.matrix_world@v.co for v in cover.data.vertices],[tuple(f.vertices) for f in cover.data.loop_triangles],all_triangles=True)
 def sx(y,z):
  hit,_,_,_=bvh.ray_cast(Vector((-3.6,y,z)),Vector((1,0,0)),4)
  assert hit is not None,(label,y,z);return hit.x+.003
 for suffix in ['triple torch light guides','triple torch backing rails']:
  old=bpy.data.objects.get(label+' '+suffix)
  if old:bpy.data.objects.remove(old,do_unlink=True)
 rods=[];backs=[]
 for j in range(3):
  cs=[(.626+j*.024,.654+j*.009),(.638+j*.023,.691+j*.006),(.663+j*.020,.743+j*.001),(.683+j*.018,.775-j*.003),(.709+j*.016,.793-j*.005)]
  path=sample(cs);pts=[(sx(sign*y,z)+.011,sign*y,z) for y,z in path]
  rods.append(tube(label+' torch diffuser '+str(j+1),pts,.0032,LED,'Lighting',(-1.41,sign*.68,.66)))
  backs.append(tube(label+' torch channel '+str(j+1),[(x+.004,y,z) for x,y,z in pts],.0048,CHROME,'Lighting',(-1.31,sign*.62,.61)))
 join(rods,label+' triple torch light guides');join(backs,label+' triple torch backing rails')
 for j in range(1,4):
  optic=bpy.data.objects[label+' outboard LED optic '+str(j)];material_emit=bpy.data.materials.get('Photo reference LED module lit face') or material('Photo reference LED module lit face',(.8,.9,1),0,.1);p=material_emit.node_tree.nodes['Principled BSDF'];p.inputs['Emission Color'].default_value=(.8,.9,1,1);p.inputs['Emission Strength'].default_value=4
  # A shallow emitter behind the existing clear optical module.
  pts=[optic.matrix_world@v.co for v in optic.data.vertices];center=sum(pts,Vector())/len(pts);center.x+=.015
  from detail_utils import cube
  ob=cube(label+' outboard module emitter '+str(j),center,(.001,.025,.010),material_emit,'Lighting',(-1.3,sign*.67,.60),.001)
for name in ['Mercedes upright hood ornament','Hood ornament mounting base']:
 o=bpy.data.objects[name];o.animation_data_clear();o.location.x-=.29;o['reference_photos']='1,5';o['photo_alignment_note']='Position fitted from photo05 camera; not OEM dimension'
report['lighting']='Three shortened rising torches per headlamp, lit main and outboard modules; clear cover silhouette preserved'
report['door_frame_faces']=split_door_frames()
# Screens remain independently editable planes with actual packed textures.
for name,tex in [('Driver instrument display','instrument_photo04_layout.png'),('COMAND center display','comand_photo04_layout.png')]:
 old=bpy.data.objects[name];bb=[old.matrix_world@Vector(v) for v in old.bound_box];xmin=max(v.x for v in bb)+.0005;y0=min(v.y for v in bb);y1=max(v.y for v in bb);z0=min(v.z for v in bb);z1=max(v.z for v in bb);delta=old['explode'].to_list();bpy.data.objects.remove(old,do_unlink=True)
 mat=material(name+' ten-photo graphic',(.03,.04,.06),0,.20);p=mat.node_tree.nodes['Principled BSDF'];image=bpy.data.images.load(str(ROOT/'refinement/textures'/tex),check_existing=True);image.pack();n=mat.node_tree.nodes.new('ShaderNodeTexImage');n.image=image
 mat.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color']);mat.node_tree.links.new(n.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.55
 ob=mesh(name,[(xmin,y0,z0),(xmin,y1,z0),(xmin,y1,z1),(xmin,y0,z1)],[(0,1,2,3)],mat,'Dashboard',(-.12,0,1.34));ob['explode']=delta
 uv=ob.data.uv_layers.new(name='DisplayUV')
 for i,co in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=co
 ob['reference_photos']='4,6';ob['text_accuracy']='Authored arrangement; illegible popup wording intentionally not transcribed'
# Soft pillows: constrained wrinkles near the seams with a quiet centre.
for side in ['left','right']:
 ob=bpy.data.objects['INT Rear '+side+' soft executive head pillow'];ob.animation_data_clear();pts=[ob.matrix_world@v.co for v in ob.data.vertices];center=sum(pts,Vector())/len(pts);inv=ob.matrix_world.inverted()
 for v in ob.data.vertices:
  w=ob.matrix_world@v.co;q=w-center;y=q.y/.146;z=q.z/.100;front=max(0,min(1,-q.x/.024))
  fold=.0034*math.sin(37*y+5*z)*math.exp(-((z-.74)/.24)**2)+.0016*math.sin(34*z+5*y)*math.exp(-((abs(y)-.84)/.19)**2)
  w.x+=front*fold-.012;w.z=center.z+q.z*1.12;v.co=inv@w
 ob.data.update();ob['reference_photos']='8,9';ob['surface_note']='Authored seam-local cloth folds from visible pillow silhouette'
# New satin-metal key islands follow the two three-spoke wheel arms.
sys.path.insert(0,str(ROOT/'current-native-v14/interior_integration/scripts'));import interior_common as C
silver=material('Photo steering satin machined aluminium',(.43,.46,.48),.86,.26);black=material('Photo steering dark switch polymer',(.008,.009,.01),0,.32);white=material('Photo steering switch legends',(.7,.72,.71),0,.5)
sc=Vector((-.247,-.43,1.002));rot=Matrix.Rotation(-.16,4,'Y');T=Matrix.Translation(sc)@rot
for side,sign in [('Left',-1),('Right',1)]:
 old=bpy.data.objects.get(side+' steering touch controls')
 if old:bpy.data.objects.remove(old,do_unlink=True)
 before=set(bpy.data.objects)
 yc=sign*.111
 C.box(side+' wheel satin switch carrier',(.031,yc,.026),(.015,.070,.073),silver,'Controls',(.25,sign*.3,1.1),.009)
 C.box(side+' wheel lower black key field',(.040,yc,.013),(.004,.054,.032),black,'Controls',(.25,sign*.3,1.1),.005)
 C.box(side+' wheel upper black touch key',(.041,yc-sign*.013,.049),(.004,.018,.014),black,'Controls',(.25,sign*.3,1.1),.003)
 C.cylinder(side+' wheel thumb roller',(.044,yc,.024),.004,.024,silver,'Controls',(.25,sign*.3,1.1),axis='Y',n=40)
 for j in range(13):
  y=yc-.010+j*.00165;C.ring(side+' thumb roller knurl '+str(j),(.044,y,.024),.0042,.00016,black,'Controls',(.25,sign*.3,1.1),axis='Y')
 for j,tx in enumerate(['+','−']):C.text(side+' wheel key legend '+str(j),tx,(.044,yc+(-1 if j==0 else 1)*.019,.006),.005,white,'Controls',(.25,sign*.3,1.1))
 for o in set(bpy.data.objects)-before:o.matrix_world=T@o.matrix_world;o['reference_photos']='4'
# Small bottom-spoke brand engraving, and circular hub seam.
ob=C.text('Steering lower spoke MAYBACH engraving','MAYBACH',(.024,0,-.146),.007,black,'Controls',(.24,-.35,1.1));ob.matrix_world=T@ob.matrix_world
pts=[T@Vector((.071,.074*math.cos(a),.006+.074*math.sin(a))) for a in [i*math.tau/160 for i in range(160)]]
C.curve('Steering airbag circular stitched seam',pts,.00025,bpy.data.materials['INT silk beige sewn thread'],'Controls',(.24,-.35,1.1),True)
# Exhibition floor protectors, as visible in photographs 4 and 6.
matblack=material('Photo exhibition floor protector black',(.002,.002,.003),0,.72);gold=material('Photo exhibition floor print muted gold',(.32,.14,.04),.2,.65)
for side,sign in [('Left',-1),('Right',1)]:
 ob=bpy.data.objects[side+' front footwell mat'];ob.data.materials.clear();ob.data.materials.append(matblack)
 center=Vector((-.485,sign*.445,.389));paths=[]
 for r in [.070,.073]:paths.append([center+Vector((r*math.cos(i*math.tau/96),r*math.sin(i*math.tau/96),0)) for i in range(97)])
 for k in range(10):
  a=k*math.tau/10;pts=[]
  for off,r in [(0,.063),(.8,.038),(1.6,.063),(0,.063)]:pts.append(center+Vector((r*math.cos(a+off*math.pi/5),r*math.sin(a+off*math.pi/5),.0001)))
  paths.append(pts)
 C.curve(side+' floor protector visible gold circular motif',paths,.00065,gold,'Interior trim',(0,sign*.6,.45));ob['reference_photos']='4,6';ob['small_logo_accuracy']='Only visible circular geometry; fine dealer emblem unresolved'
# Low-energy warm footwell pools; emissive materials export to GLB.
emit=material('Photo footwell pink warm light',(.4,.12,.18),0,.5);pp=emit.node_tree.nodes['Principled BSDF'];pp.inputs['Emission Color'].default_value=(1,.22,.33,1);pp.inputs['Emission Strength'].default_value=2.5
for sign in [-1,1]:
 C.box('Front footwell courtesy source '+str(sign),(-.51,sign*.49,.64),(.04,.018,.001),emit,'Interior trim',(0,sign*.5,.5),.001)
# Preserve explosion animation with the current assembled transforms.
parts=[o for o in S.objects if o.get('component')];homes={o.name:o.matrix_world.copy() for o in parts}
assert len({o['component'] for o in parts})==len(parts)
for o in parts:
 o.animation_data_clear();home=o.location.copy();e=list(o['explode']);delta=Vector((e[0],-e[2],e[1]));o['rest_matrix']=[float(v) for row in homes[o.name] for v in row];o['assembled_location']=list(home)
 for f,a in [(1,0),(65,1),(95,1),(160,0)]:o.location=home+a*delta;o.keyframe_insert(data_path='location',frame=f)
 action=o.animation_data.action
 for layer in action.layers:
  for strip in layer.strips:
   bag=strip.channelbag(o.animation_data.action_slot)
   if bag:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
err=0
for f in [1,65,95,160,1]:
 S.frame_set(f);bpy.context.view_layer.update()
 assert all(math.isfinite(v) for o in parts for row in o.matrix_world for v in row)
 if f in [1,160]:err=max(err,max(abs(o.matrix_world[i][j]-homes[o.name][i][j]) for o in parts for i in range(4) for j in range(4)))
assert err<1e-6
S['reference_authority']='Only Photo_01..Photo_10 supplied by the user';S['refinement_version']='v17-ten-photo-details';S['quality_accepted']=False
report.update(reference_images=10,components=len(parts),animation_return_error_m=err,quality_accepted=False,unresolved=['Full photographic material agreement','Camera fit is approximate, not dimensional validation','Tiny screen popup wording and dealer emblem','Interior and exterior final visual acceptance'])
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'refinement/Maybach_Ten_Photo_v17.blend'),compress=True)
(ROOT/'refinement/photo-detail-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('PHOTO_DETAILS_COMPLETE',json.dumps(report,ensure_ascii=False),flush=True)

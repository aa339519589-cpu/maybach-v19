"""Separate the four upper door frames along the shared canopy parameter surface.
Glass silhouettes and canopy field are preserved. This makes door inspection
views physically coherent instead of hiding the entire roof.
"""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'current-native-v14/master_shell'))
from body_curves_reference import canopy,VERSION
from detail_utils import mesh
from fix_surface_normals import fix_surface_normals

def split_door_frames():
 src=(ROOT/'current-native-v14/master_shell/repair_glazing_curve_sampling.py').read_text()
 ns={'math':math}
 exec(src[src.index('def front_edge'):src.index('coords=[];edges=[]')],ns)
 windows=ns['loops'];inside=ns['inside'];coords=[];edges=[]
 def add_loop(poly):
  start=len(coords);coords.extend(poly);edges.extend((start+i,start+(i+1)%len(poly)) for i in range(len(poly)))
 outer=[(-1.172+3.402*i/112,-1) for i in range(112)]+[(2.23,-1+2*i/80) for i in range(80)]+[(2.23-3.402*i/112,1) for i in range(112)]+[(-1.172,1-2*i/80) for i in range(80)]
 add_loop(outer)
 for name,poly in windows:add_loop(poly)
 domains=[]
 # The split follows each opening, leaving the structural A/B/C roof rails in place.
 for sign,side in [(-1,'Left'),(1,'Right')]:
  for part,poly in [('front',[(-1.078,1),(.058,1),(.058,.798),(-.291,.798),(-1.078,.983)]),('rear',[(.062,1),(1.146,1),(1.125,.80),(.062,.798)])]:
   poly=[(x,q*sign) for x,q in poly];name=side+' '+part+' door upper window frame';domains.append((name,poly));add_loop(poly)
 for i in range(1,112):
  for j in range(1,80):coords.append((-1.172+3.402*i/112,-1+2*j/80))
 result=delaunay_2d_cdt([Vector(p) for p in coords],edges,[],0,1e-7,False);uv=result[0]
 roof='Roof and pillar outer framework';groups={roof:[]};groups.update({n:[] for n,p in domains})
 for face in result[2]:
  p=tuple(sum(uv[i][j] for i in face)/len(face) for j in range(2))
  if any(inside(p,poly) for n,poly in windows):continue
  name=next((n for n,poly in domains if inside(p,poly)),roof)
  a,b,c=[uv[i] for i in face[:3]]
  groups[name].append(tuple(face) if (b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)>0 else tuple(reversed(face)))
 old=bpy.data.objects[roof];bpy.data.objects.remove(old,do_unlink=True)
 names=[];counts={}
 for name,faces in groups.items():
  used=sorted({i for f in faces for i in f});remap={j:i for i,j in enumerate(used)};verts=[canopy(*uv[i]) for i in used];norm=[]
  for idx in used:
   x,q=uv[idx];e=1e-5;n=(Vector(canopy(x+e,q))-Vector(canopy(x-e,q))).cross(Vector(canopy(x,q+e))-Vector(canopy(x,q-e))).normalized();norm.append(n)
  delta=(0,0,1.8) if name==roof else (0,(-1 if name.startswith('Left') else 1)*1.65,1.05)
  o=mesh(name,verts,[tuple(remap[i] for i in f) for f in faces],bpy.data.materials['Vehicle deep blue metallic'],'Roof and glass',delta)
  o.data.normals_split_custom_set_from_vertices(norm);m=o.modifiers.new('Physical sheet thickness','SOLIDIFY');m.thickness=.012;m.offset=-1;o['curvature_version']=VERSION;o['reference_photos']='1,2,3,5';names.append(name);counts[name]=len(faces)
 fix_surface_normals(ROOT/'current-native-v14/master_shell',ROOT/'refinement/door-frame-normals.json',object_names=names)
 for o in bpy.context.scene.objects:
  n=o.name.lower()
  for side in ['left','right']:
   for which in ['front','rear']:
    if side in n and which in n and (o.get('category')=='Door interiors' or any(k in n for k in ['door skin','door glass','door upper window frame','door handle'])):
     o['door_group']=side+'_'+which
     o['door_hinge_m']=[-.995 if which=='front' else .063,-.85 if side=='left' else .85,.65]
 return counts

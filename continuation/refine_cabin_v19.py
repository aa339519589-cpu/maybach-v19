import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'current-native-v14/master_shell'))
from detail_utils import mesh
from body_curves_reference import canopy
S=bpy.context.scene;S.frame_set(1)
for o in S.objects:
    if o.get('component'):o.animation_data_clear()
changes=[]
# The prior liner followed the full canopy and extended behind the roof into
# the rear glazing. Its cream band in the rear render is a real geometry error.
# End the liner at the existing windshield/roof boundary, not the glass surface.
old=bpy.data.objects['INT Sculpted headliner interior surround']
props={k:(old[k].to_list() if hasattr(old[k],'to_list') else old[k].to_dict() if hasattr(old[k],'to_dict') else old[k]) for k in old.keys()};mat=old.data.materials[0]
bpy.data.objects.remove(old,do_unlink=True)
vv=[];ff=[];nu,nv=100,64
for i in range(nu+1):
    for j in range(nv+1):
        q=-.80+1.60*j/nv;front=-.43+.20*q*q+.025;back=1.29-.17*q*q-.045
        x=front+(back-front)*i/nu;p=Vector(canopy(x,q));p.z-=.024;vv.append(p)
for i in range(nu):
    for j in range(nv):ff.append((i*(nv+1)+j,i*(nv+1)+j+1,(i+1)*(nv+1)+j+1,(i+1)*(nv+1)+j))
o=mesh('INT Sculpted headliner interior surround',vv,ff,mat,'Interior trim')
for k,v in props.items():o[k]=v
m=o.modifiers.new('Leather backing thickness','SOLIDIFY');m.thickness=.008;m.offset=-1
o['roof_boundary_correction']='Trimmed to existing front/rear glass boundary with 25/45 mm inset'
o['reference_photos']='2,3,10'
# Keep the rear blind seam inside the shortened roof lining.
for o in S.objects:
    if o.name.startswith('INT Panoramic roof blind inset seam 0.4'):
        for spline in o.data.splines:
            for v in spline.points:
                x,y,z,w=v.co;x=.40+(x-.40)*(.72/.79)
                lo,hi=-1.,1.
                for _ in range(25):
                    q=(lo+hi)/2
                    if canopy(x,q)[1]<y:lo=q
                    else:hi=q
                v.co=(x,y,canopy(x,(lo+hi)/2)[2]-.0255,w)
changes.append('Headliner trimmed away from the existing rear-window aperture; front corners aligned to windshield boundary')
# Photo 2/3 show a dark rear windscreen; use a separate neutral green tint.
rear=bpy.data.objects['Heated rear window'];glass=rear.data.materials[0].copy();glass.name='Photo 2 and 3 rear windscreen neutral tinted glass'
p=glass.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.50,.57,.56,1);p.inputs['Roughness'].default_value=.014
rear.data.materials.clear();rear.data.materials.append(glass);rear['reference_photos']='2,3'
changes.append('Independent rear glazing tint from Photos 2 and 3')
# Lower front seat soft assemblies while keeping the original mounting rails.
# The bottom seat valance is shortened to preserve carriage/floor clearance.
delta=.045;moved=[]
for o in list(S.objects):
    if not o.name.startswith(('INT Front left','INT Front right')) or o.get('category') not in ['Seats','Cabin technology']:continue
    if any(s in o.name for s in ['mounting rail','seat carriage']):continue
    if 'upholstered seat valance' in o.name:
        M=o.matrix_world.copy();inv=M.inverted()
        for v in o.data.vertices:
            q=M@v.co;q.z=.406+(q.z-.406)*.55;v.co=inv@q
        o.data.update();o['front_valance_vertical_scale']=.55
    else:o.location.z-=delta
    o['photo_7_10_vertical_adjustment_m']=-delta;moved.append(o.name)
bpy.context.view_layer.update()
for side,sign in [('left',-1),('right',1)]:
    prefix='INT Front '+side
    # Make the headrest less horizontally stretched, retaining its soft corners.
    yc=sign*.455;cz=1.270-delta;A=Matrix.Translation((0,yc,cz))@Matrix.Diagonal((1.,.90,1.12,1.))@Matrix.Translation((0,-yc,-cz))
    for suffix in [' rounded-rectangular headrest cushion',' headrest rear bound piping',' headrest rear fine edge seam']:
        o=bpy.data.objects[prefix+suffix];o.matrix_world=A@o.matrix_world;o['reference_photos']='7,10'
    # Replace the flat top pad with a narrow upholstered wrap along top/side.
    old=bpy.data.objects[prefix+' independent headrest upper comfort pad']
    # Copy ID arrays to Python values before removing the old ID datablock.
    props={k:(old[k].to_list() if hasattr(old[k],'to_list') else old[k].to_dict() if hasattr(old[k],'to_dict') else old[k]) for k in old.keys()};material=old.data.materials[0]
    bpy.data.objects.remove(old,do_unlink=True)
    points=[]
    for i in range(145):
        a=-.22+(math.pi+.44)*i/144
        y=.134*math.copysign(abs(math.cos(a))**.48,math.cos(a));z=.108*math.copysign(abs(math.sin(a))**.48,math.sin(a))
        points.append(Vector((.217+.08*z,yc+y,cz+z)))
    verts=[];faces=[];n=16
    for i,q in enumerate(points):
        t=(points[min(len(points)-1,i+1)]-points[max(0,i-1)]).normalized();b=Vector((1,0,0));a=t.cross(b).normalized()
        cap=min(1.,(i+1)/8,(len(points)-i)/8)
        for j in range(n):
            th=math.tau*j/n;verts.append(q+cap*(b*(.011*math.cos(th))+a*(.010*math.sin(th))))
    for i in range(len(points)-1):
        for j in range(n):faces.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
    faces.extend([tuple(reversed(range(n))),tuple((len(points)-1)*n+j for j in range(n))])
    o=mesh(prefix+' independent headrest upper comfort pad',verts,faces,material,'Seats')
    for k,v in props.items():o[k]=v
    o['reference_photos']='7,10';o['shape_note']='Narrow upper and side wrap, fitted from visible outline; dimensions estimated'
changes.append('Front soft seat assembly lowered 45 mm, fixed rails; photo-estimated fit')
changes.append('Front headrest aspect and upper-side wrap adjusted against Photos 7 and 10')
# Rebuild reversible native explosion actions at the updated rest locations.
parts=[o for o in S.objects if o.get('component')];homes={o.name:o.matrix_world.copy() for o in parts}
assert len(parts)==967 and len(set(o['component'] for o in parts))==len(parts)
for o in parts:
    o.animation_data_clear();home=o.location.copy();e=o['explode'];d=Vector((e[0],-e[2],e[1]));o['rest_matrix']=[float(v) for row in homes[o.name] for v in row];o['assembled_location']=list(home)
    for frame,factor in [(1,0),(65,1),(95,1),(160,0)]:o.location=home+factor*d;o.keyframe_insert(data_path='location',frame=frame)
    for layer in o.animation_data.action.layers:
        for strip in layer.strips:
            bag=strip.channelbag(o.animation_data.action_slot)
            if bag:
                for curve in bag.fcurves:
                    for k in curve.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
error=0
for frame in [1,65,95,160,1]:
    S.frame_set(frame);bpy.context.view_layer.update()
    assert all(math.isfinite(v) for o in parts for row in o.matrix_world for v in row)
    if frame in [1,160]:error=max(error,max(abs(o.matrix_world[i][j]-homes[o.name][i][j]) for o in parts for i in range(4) for j in range(4)))
assert error<1e-6
S['quality_accepted']=False;S['refinement_version']='v19-ten-photo-rear-and-cabin';S['reference_authority']='Only user Photos 01-10, uploaded 2026-10-07'
report=dict(reference_images=10,components=len(parts),quality_accepted=False,changes=changes,moved_front_components=moved,native_animation_return_error=error,dimensional_status='Estimated from perspective images; not factory dimensions')
(ROOT/'refinement/checkpoint19.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'refinement/Maybach_Ten_Photo_v19.blend'),compress=True)
print('CHECKPOINT19_SAVED',len(parts),flush=True)

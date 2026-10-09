"""Conservative normal repair of the existing rear pressing; geometry is untouched.

The canonical functions describe the already modelled geometry. They are used as
normal datums, not as new visual references. Unmatched cut walls are preserved.
"""
import bpy,sys,json
import numpy as np
from pathlib import Path
from types import SimpleNamespace
from mathutils.kdtree import KDTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from fix_surface_normals import _load_curvature,_world_positions
from fix_panel_normals import _surface,project

def smooth(a,b,x):
    t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)

def section(C,x,theta):
    R=SimpleNamespace(base=C.base,warp_array=lambda p:p)
    theta=np.mod(theta,1);v=np.empty((len(theta),3));xx=np.full(len(theta),x)
    a=theta<1/6;b=(theta>=1/6)&(theta<.5);c=(theta>=.5)&(theta<2/3);d=theta>=2/3
    deck=C.base.deck(x)
    if a.any():v[a]=_surface(R,np.column_stack((xx[a],.19+(deck-.05-.19)*(theta[a]*6))),'side',1)
    if b.any():v[b]=_surface(R,np.column_stack((xx[b],np.cos(np.pi*(theta[b]-1/6)*3))),'cap',1)
    if c.any():v[c]=_surface(R,np.column_stack((xx[c],.19+(deck-.05-.19)*(1-(theta[c]-.5)*6))),'side',-1)
    if d.any():
        y=(-1+(theta[d]-2/3)*6)*C.base.width(x)*.91
        amount=(np.abs(y)/C.base.width(x))**3
        v[d]=np.column_stack((x+.180*amount*np.exp(-((x+C.base.LENGTH/2)/.34)**2)-.170*amount*np.exp(-((x-C.base.LENGTH/2)/.30)**2),y,np.full(d.sum(),.19)))
    return v

def tail(C,uv):
    t,theta=uv.T;b=section(C,2.5,theta);eps=1e-5
    lo=section(C,2.5-eps,theta);hi=section(C,2.5+eps,theta)
    scale=(b[:,0]-C.base.LENGTH/2)*np.pi/2
    dy=scale*(hi[:,1]-lo[:,1])/(hi[:,0]-lo[:,0]);dz=scale*(hi[:,2]-lo[:,2])/(hi[:,0]-lo[:,0])
    r=np.sin(np.pi*t/2);g=1-np.cos(np.pi*t/2);h=t*t*(t-1)
    x=C.base.LENGTH/2+(b[:,0]-C.base.LENGTH/2)*g;y=r*b[:,1]+h*dy;z=.56+r*(b[:,2]-.56)+h*dz
    # Existing local pressing correction made before Boolean apertures/warp.
    w=smooth(2.50,2.60,x)*smooth(.60,.86,z)*(1-smooth(.73,.88,np.abs(y)))
    tx=2.716-.040*(y/.8)**2-.028*((z-.78)/.25)**2
    x=x+w*np.maximum(0,tx-x)
    return C.warp_array(np.column_stack((x,y,z)))

def project_tail(C,positions):
    uvgrid=np.array([(t,th) for t in np.linspace(.01,1,90) for th in np.linspace(0,1,360,endpoint=False)])
    pp=tail(C,uvgrid);tree=KDTree(len(pp))
    for i,p in enumerate(pp):tree.insert(p,i)
    tree.balance();uv=np.array([uvgrid[tree.find(p)[1]] for p in positions]);e=1e-5
    for _ in range(20):
        s=tail(C,uv);a=(tail(C,uv+[e,0])-tail(C,uv-[e,0]))/(2*e);b=(tail(C,uv+[0,e])-tail(C,uv-[0,e]))/(2*e)
        r=s-positions;aa=np.einsum('ij,ij->i',a,a);ab=np.einsum('ij,ij->i',a,b);bb=np.einsum('ij,ij->i',b,b);ar=np.einsum('ij,ij->i',a,r);br=np.einsum('ij,ij->i',b,r)
        det=np.maximum(aa*bb-ab*ab,1e-18);delta=np.column_stack(((bb*ar-ab*br)/det,(aa*br-ab*ar)/det));delta=np.clip(delta,[-.05,-.03],[.05,.03]);uv-=delta;uv[:,0]=np.clip(uv[:,0],.001,1);uv[:,1]%=1
        if np.max(np.abs(delta))<1e-9:break
    a=(tail(C,uv+[e,0])-tail(C,uv-[e,0]))/(2*e);b=(tail(C,uv+[0,e])-tail(C,uv-[0,e]))/(2*e)
    n=np.cross(a,b);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-18)
    return n,np.linalg.norm(tail(C,uv)-positions,axis=1),uv

def fix_rear_normals():
    C=_load_curvature(Path(__file__).resolve().parents[1]/'current-native-v14/master_shell')
    # Check vectorization against the exact original source boundary.
    th=np.linspace(.002,.998,73)
    err=float(np.max(np.abs(section(C,2.5,th)-np.array([C.base.section_boundary(2.5,float(t)) for t in th]))))
    assert err<1e-10,err
    report=[]
    for name in ['Trunk lid outer assembly','Rear bumper cover']:
        o=bpy.data.objects[name];d=o.data;assert not o.modifiers
        pos=_world_positions(o);M=np.asarray(o.matrix_world)[:3,:3];cur=np.asarray([n.vector[:] for n in d.corner_normals]);res=cur.copy()
        fields=[project(C,pos,'cap',1),project_tail(C,pos)];changed=[];targets=[];angles=[];counts=[0,0];areas=[0.,0.]
        for face in d.polygons:
            ids=np.asarray(face.vertices);p=pos[ids];gn=np.zeros(3)
            for k in range(1,len(p)-1):gn+=np.cross(p[k]-p[0],p[k+1]-p[0])
            area=np.linalg.norm(gn)*.5;gn/=max(area*2,1e-18)
            candidates=[]
            for k,(n,dist,uv) in enumerate(fields):
                if np.max(dist[ids])<.00018 and np.min(n[ids]@gn)>.8:candidates.append((float(np.max(dist[ids])),k,n[ids]))
            if not candidates:continue
            _,k,n=min(candidates,key=lambda x:x[0]);loops=np.asarray(face.loop_indices)
            old=cur[loops]@np.linalg.inv(M);old/=np.maximum(np.linalg.norm(old,axis=1)[:,None],1e-18)
            angles.extend(np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i',old,n),-1,1))))
            local=n@M;local/=np.linalg.norm(local,axis=1)[:,None];res[loops]=local;face.use_smooth=True;changed.extend(loops);targets.extend(n);counts[k]+=1;areas[k]+=area
        assert changed,(name,'No exact exterior faces')
        d.normals_split_custom_set(res.tolist());d.update();out=np.asarray([n.vector[:] for n in d.corner_normals]);idx=np.array(changed)
        actual=out[idx]@np.linalg.inv(M);actual/=np.linalg.norm(actual,axis=1)[:,None]
        after=np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i',actual,np.asarray(targets)),-1,1)))
        # Packed custom normals at very thin cut corners can quantize coarsely.
        # Keep a recorded half-degree ceiling and a tighter 95th-percentile check.
        print('REAR_NORMAL_ASSIGNMENT_ERROR',name,np.quantile(after,[.5,.95,1]).tolist(),flush=True)
        assert float(np.max(after))<.5 and float(np.quantile(after,.95))<.1,(name,float(np.max(after)))
        assert np.array_equal(pos,_world_positions(o))
        o['rear_normal_revision']='continuous-exterior-fields-v1'
        r=dict(object=name,repaired_cap_faces=counts[0],repaired_tail_faces=counts[1],repaired_area_m2=areas,repaired_corners=len(idx),unmatched_faces_preserved=len(d.polygons)-sum(counts),before_p95_deg=float(np.quantile(angles,.95)),before_max_deg=float(np.max(angles)),after_p95_deg=float(np.quantile(after,.95)),after_max_deg=float(np.max(after)),geometry_max_change_m=0)
        report.append(r);print('REAR_NORMAL_REPAIR',json.dumps(r),flush=True)
    return {'source_boundary_vectorization_error_m':err,'objects':report}

if __name__=='__main__':
    p=Path(__file__).parent;report=fix_rear_normals();(p/'rear-normal-report.json').write_text(json.dumps(report,indent=2))
    bpy.ops.wm.save_as_mainfile(filepath=str(p/'Maybach_Rear_Normal_Test.blend'),compress=True)
    print('REAR_NORMAL_TEST_SAVED',flush=True)

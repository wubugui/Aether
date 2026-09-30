"""Sample the actual finite cone interval and compensate growing cross-section."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'captures/lantern_volume_28e.gdshader').read_text(encoding='utf-8')
anchor='    float depth=textureLod(depth_texture,SCREEN_UV,0.).r;'
assert s.count(anchor)==1
s=s.replace(anchor,'''    // Tighten the box interval to the actual finite frustum, avoiding empty
    // space samples that miss the thin near-source cone. z caps are in box.
    float origin_distance=enter;
    vec3 interval_origin=local_camera+ray*origin_distance;
    if(volume_kind<.5){
        float r_camera=start_radius-divergence*interval_origin.z;
        float qa=dot(ray.xy,ray.xy)-divergence*divergence*ray.z*ray.z;
        float qb=2.*(dot(interval_origin.xy,ray.xy)+r_camera*divergence*ray.z);
        float qc=dot(interval_origin.xy,interval_origin.xy)-r_camera*r_camera;
        if(abs(qa)<.0000001){
            if(abs(qb)>.0000001){
                float crossing=origin_distance-qc/qb;
                if(qb>0.)leave=min(leave,crossing);else enter=max(enter,crossing);
            }else if(qc>0.)leave=enter;
        }else{
            float discriminant=qb*qb-4.*qa*qc;
            if(discriminant<0.){
                if(qa>0.)leave=enter;
            }else{
                float h=sqrt(max(discriminant,0.));
                float first=(-qb-h)/(2.*qa),last=(-qb+h)/(2.*qa);
                float t0=origin_distance+min(first,last),t1=origin_distance+max(first,last);
                if(qa>0.){enter=max(enter,t0);leave=min(leave,t1);}
                else if(enter<t0){leave=min(leave,t0);}
                else{enter=max(enter,t1);}
            }
        }
    }else{
        float qb=dot(interval_origin,ray);
        float disc=qb*qb-dot(interval_origin,interval_origin)+halo_radius*halo_radius;
        if(disc<0.)leave=enter;
        else{enter=max(enter,origin_distance-qb-sqrt(disc));leave=min(leave,origin_distance-qb+sqrt(disc));}
    }
'''+anchor)
old='density=(1.-smoothstep(.70,1.,radial))*exp(-along*.0025)*lit*above_sea*.012;'
assert s.count(old)==1
s=s.replace(old,'''// Artistic fog scattering: compensate wider ray chords and fade axially.
                // This is not a calibrated radiometric atmosphere.
                density=(1.-smoothstep(.70,1.,radial))*exp(-along/260.)*lit*above_sea*.065/max(radius,.8);''')
(R/'captures/lantern_volume_28f.gdshader').write_text(s,encoding='utf-8')
a=(R/'captures/lantern_lighting_28e.gd').read_text(encoding='utf-8').replace('32step density integration','32step finite-cone-interval density integration with distance/cross-section falloff')
(R/'captures/lantern_lighting_28f.gd').write_text(a,encoding='utf-8')
d=(R/'tools/render_lantern_lighting_28e.py').read_text(encoding='utf-8').replace('28e','28f')
d=d.replace('28f fixes unshaded final color routing to ALBEDO;', '28f samples the true finite frustum/sphere ray intervals, and uses radial-width compensation plus axial extinction to prevent far-end haze dominance; retains corrected ALBEDO output;')
(R/'tools/render_lantern_lighting_28f.py').write_text(d,encoding='utf-8')

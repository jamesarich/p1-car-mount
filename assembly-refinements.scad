// P1 mount 1.1 assembly helpers. Millimeters; no top-level printable geometry.
// Original design James Rich, CC BY-SA 4.0. Refinements preserve interface datums.
// Import with use <assembly-refinements.scad>; reference cable/tool bodies must
// never be unioned into the printable frame. All hardware envelopes are nominal.

function ar_sum(v, i=0) = i >= len(v) ? 0 : v[i] + ar_sum(v, i+1);
function ar_path_length(p) = ar_sum([for(i=[0:len(p)-2]) norm(p[i+1]-p[i])]);
function ar_three_point_radius(a,b,c) =
    let(den=2*norm(cross(b-a,c-a))) den < 1e-10 ? 1e12 :
    norm(b-a)*norm(c-b)*norm(c-a)/den;
function ar_path_min_radius(p) = min([for(i=[1:len(p)-2])
    ar_three_point_radius(p[i-1],p[i],p[i+1])]);
function ar_bezier(a,b,c,d,t) =
    pow(1-t,3)*a + 3*pow(1-t,2)*t*b + 3*(1-t)*t*t*c + t*t*t*d;
function ar_node_point(p, seat_z=10.5+59*tan(4), tilt=4, insert_offset=11.5) =
    [p[0], insert_offset+(p[1]-insert_offset)*cos(tilt)+p[2]*sin(tilt),
     seat_z-(p[1]-insert_offset)*sin(tilt)+p[2]*cos(tilt)];
function ar_node_port(seat_z=10.5+59*tan(4), tilt=4, insert_offset=11.5) =
    ar_node_point([-55,-36.5,17],seat_z,tilt,insert_offset);

// Capsule shims sit INSIDE the screw access recess, against the original
// 2 mm web. A metal flat washer remains between each screw head and shim.
// Overall 14 x 20, bore capsule 6.8 x 12.8: full +/-3 mm shank travel retained.
// The 16 x 22 bearing recess leaves 1 mm nominal clearance around the shim.
// Thicknesses below are CALIBRATION SPECIMENS, not a selected service stack.
// 0.5 mm is intentionally a thin supported fit sample, not an unsupported lug.
module ar_capsule2d(d=14, travel=6) {
    hull() for(y=[-travel/2,travel/2]) translate([0,y]) circle(d=d,$fn=96);
}
module ar_screw_shim(thickness=1, outer_d=14, bore_d=6.8, travel=6,
                     entry_relief=0.15) {
    assert(thickness >= 0.5 && thickness <= 3,
        "shim checked nominal design range is 0.5-3 mm; revalidate outside it");
    assert(outer_d-bore_d >= 6 && outer_d <= 14 && travel == 6,
        "preserve shim bearing webs, recess clearance and full slot travel");
    relief=min(entry_relief,thickness/4);
    difference() {
        linear_extrude(thickness) ar_capsule2d(outer_d,travel);
        translate([0,0,-0.1]) linear_extrude(thickness+0.2)
            ar_capsule2d(bore_d,travel);
        // Separate bore entry treatment; leave both bearing faces planar.
        for(z=[0,thickness-relief]) translate([0,0,z])
            hull() for(y=[-travel/2,travel/2]) translate([0,y,0])
                cylinder(h=relief+0.01,
                    d1=z==0?bore_d+2*relief:bore_d,
                    d2=z==0?bore_d:bore_d+2*relief,$fn=96);
    }
}
module ar_screw_shim_set(thicknesses=[0.5,1,1.5,2]) {
    // Separate components, left-to-right increasing thickness; no connecting sprue.
    for(i=[0:len(thicknesses)-1]) translate([24*i,0,0])
        ar_screw_shim(thicknesses[i]);
}
module ar_screw_shims_installed(front=0,rear=0,seat_z=10.5+59*tan(4),
                                tilt=4,offset=11.5,spacing=39,web=2) {
    // Reference assembly only. Print shims individually FLAT, not in this pose.
    for(i=[0,1]) let(t=i==0?front:rear, y=i==0?spacing/2:-spacing/2)
        if(t>0) translate([0,offset,seat_z]) rotate([-tilt,0,0])
            translate([0,y,-web-t]) ar_screw_shim(t);
}
function ar_screw_engagement(screw_length=undef,web=2,washer=undef,shim=0) =
    is_undef(screw_length)||is_undef(washer) ? undef : screw_length-web-washer-shim;
function ar_stack_status(screw_length=undef,web=2,washer=undef,shim=0,
                        insert_depth=undef,min_engagement=undef,bottom_margin=0.5) =
    let(e=ar_screw_engagement(screw_length,web,washer,shim))
    is_undef(e)||is_undef(insert_depth)||is_undef(min_engagement) ? "not checked" :
    e>=min_engagement && e<=insert_depth-bottom_margin ? "nominal pass" : "fail";
module ar_screw_stack_report(screw_length=undef,washer=undef,front_shim=0,rear_shim=0,
                            insert_depth=[undef,undef],min_engagement=undef,
                            web=2,bottom_margin=0.5) {
    // Front/rear insert depths and minimum engagement must be measured/specified.
    // Nominal screw label alone does not establish actual under-head length.
    for(i=[0,1]) let(s=i==0?front_shim:rear_shim)
        echo(str(i==0?"front":"rear"," screw: engagement=",
            ar_screw_engagement(screw_length,web,washer,s)," mm; ",
            ar_stack_status(screw_length,web,washer,s,insert_depth[i],
                            min_engagement,bottom_margin),
            "; bottoming margin target=",bottom_margin,
            " mm (provisional); select shim only after measurements"));
}

// Complete nominal cable CENTERLINE from bulkhead's free cable to node-side
// plug tail. First quarter-bend matches the original validated tail keep-out.
// A tilted semicircle lifts the cable while bringing it around the rear-left;
// a C1 Bezier traverses outside the node box, and a quarter-circle approaches
// the node-side plug axially. Required curvature is 25 mm N / 15 mm stock.
// N centerline ~288.37 mm; stock ~211.08 mm. The 300 mm catalog length datum,
// rigid termination lengths and remaining slack are NOT measured. The route
// is feasible nominal geometry, not a verified use of every mm of the cable.
function ar_coax_route(alfa=true,hole_y=undef,fin_h=68,
                       drop_z=53,tail=undef,bend=undef,
                       seat_z=10.5+59*tan(4),tilt=4,insert_offset=11.5,
                       lift_angle=25,plug_tail_x=-73) =
    let(hy=is_undef(hole_y)?(alfa?-124:-118.2):hole_y,
        r=is_undef(bend)?(alfa?25:15):bend,
        st=is_undef(tail)?(alfa?24:9.5):tail,
        port=ar_node_port(seat_z,tilt,insert_offset),
        a=[0,hy-r,drop_z-st-r],
        u=[-cos(lift_angle),0,sin(lift_angle)],
        b=a+2*r*u,
        c=[plug_tail_x-r,port[1]-r,port[2]],
        l=(c[1]-b[1])*0.45)
    concat([[0,hy,drop_z]],
        [for(k=[0:45]) let(t=90*k/45)
            [0,hy-r*(1-cos(t)),drop_z-st-r*sin(t)]],
        [for(k=[1:90]) let(t=180*k/90)
            a+r*u*(1-cos(t))+[0,-r*sin(t),0]],
        [for(k=[1:64]) ar_bezier(b,b+[0,l,0],c-[0,l,0],c,k/64)],
        [for(k=[1:45]) let(t=90*k/45)
            [plug_tail_x-r*cos(t),port[1]-r+r*sin(t),port[2]]]);

module ar_path_tube(points,d=2.5,facets=16) {
    for(i=[0:len(points)-2]) hull() for(j=[i,i+1])
        translate(points[j]) sphere(d=d,$fn=facets);
}
module ar_node_plug_envelope(seat_z=10.5+59*tan(4),tilt=4,insert_offset=11.5,
                              tool=false,plug_tail_x=-73) {
    p=ar_node_port(seat_z,tilt,insert_offset);
    // Source photo-derived jack projects 8 mm outboard from X=-55.
    // Provisional 10 mm plug body occupies X=-73..-63; width 8 mm AF.
    // Tool is a conservative 15 mm cylinder from the outboard side, not hardware.
    if(tool) translate([plug_tail_x-15,p[1],p[2]]) rotate([0,90,0])
        cylinder(d=15,h=25,$fn=96);
    else translate([plug_tail_x,p[1],p[2]]) rotate([0,90,0]) {
        cylinder(d=8/cos(30),h=10,$fn=6);
        translate([0,0,7]) cylinder(d=7.5,h=3,$fn=96);
    }
}
module ar_coax_reference(alfa=true,hole_y=undef,fin_h=68,drop_z=53,
                         tail=undef,bend=undef,seat_z=10.5+59*tan(4),tilt=4,
                         insert_offset=11.5,keepout=0,show_tool=false) {
    pts=ar_coax_route(alfa,hole_y,fin_h,drop_z,tail,bend,seat_z,tilt,insert_offset);
    color(keepout>0?[0.9,0.45,0.1,0.25]:[0.08,0.08,0.08])
        ar_path_tube(pts,(alfa?2.5:2.9)+2*keepout);
    color("gold") ar_node_plug_envelope(seat_z,tilt,insert_offset,show_tool);
    echo(str(alfa?"N-type":"stock"," complete free-cable centerline: ",
        ar_path_length(pts)," mm; min sampled 3-point radius ",
        ar_path_min_radius(pts)," mm; catalog 300 mm datum / surplus slack unverified"));
}

function ar_path_index_at_y(points,y) =
    let(gaps=[for(p=points) abs(p[1]-y)], best=min(gaps))
    [for(i=[0:len(points)-1]) if(gaps[i]==best) i][0];
function ar_cable_saddle_center(alfa=true,hole_y=undef,fin_h=68,drop_z=53,
                                tail=undef,bend=undef,
                                seat_z=10.5+59*tan(4),tilt=4,insert_offset=11.5) =
    let(pts=ar_coax_route(alfa,hole_y,fin_h,drop_z,tail,bend,seat_z,tilt,insert_offset),
        i=ar_path_index_at_y(pts,alfa?-86:-65)) pts[i];

module ar_cable_saddle(alfa=true,hole_y=undef,fin_h=68,drop_z=53,
                        tail=undef,bend=undef,
                        seat_z=10.5+59*tan(4),tilt=4,insert_offset=11.5,
                        cable_radial_clearance=1,body_edge_radius=1,
                        eye_outline_radius=1.1,eye_entry_relief=0.35,
                        mouth_relief=0.4,root_z=8) {
    // PRINTABLE integrated cable-tie saddle; union into frame BEFORE existing
    // foot/nut and node keep-out cuts so those critical interfaces remain intact.
    // Target locations are variant-specific: N lies over left-rear boss, stock
    // over its forward shoulder. No unsupported rigid snap tabs are used.
    // Tie is nominal 2.5 mm wide x <=1.5 thick; actual tie/coupon fit unverified.
    pts=ar_coax_route(alfa,hole_y,fin_h,drop_z,tail,bend,seat_z,tilt,insert_offset);
    ix=ar_path_index_at_y(pts,alfa?-86:-65);
    p=pts[ix];
    tangent=pts[ix+1]-pts[ix-1];
    angle=atan2(tangent[1],tangent[0])-90;
    root=[-76,p[1],root_z];
    top_z=p[2]-7;
    wire_r=(alfa?2.5:2.9)/2+cable_radial_clearance;
    local_points=[for(i=[max(0,ix-10):min(len(pts)-1,ix+10)]) pts[i]];
    assert(cable_radial_clearance>=0.5 && eye_outline_radius>=1,
        "retain cable clearance and rounded tie-eye outline");
    assert(6.5-eye_outline_radius-eye_entry_relief-wire_r>=2.3,
        "tie eye entry leaves less than 2.3 mm nominal central bearing web");
    assert(top_z>root_z+8,"saddle root is too short for the checked loft");
    difference() {
        union() {
            // C1 station law: zero slope at base/top; sixteen loft segments.
            // Base 16x20 capsule is buried in the left rear foot/rail shoulder.
            for(k=[0:15]) hull() for(j=[k,k+1]) let(
                u=j/16,s=u*u*(3-2*u),
                q=[root[0]+(p[0]-root[0])*s,root[1],root_z+(top_z-root_z)*u])
                translate(q) rotate([0,0,angle]) linear_extrude(0.04)
                    ar_capsule2d(16-2*s,4+2*s);
            // Broad rounded working head; dimensions 14 x 20 in plan.
            // Its crest is 0.8 mm BELOW the nominal cable axis so a tie can
            // contact the cable, even after it settles into the 1 mm clearance.
            translate(p) rotate([0,0,angle]) minkowski() {
                translate([0,0,-8]) linear_extrude(6.2)
                    ar_capsule2d(14-2*body_edge_radius,6);
                sphere(r=body_edge_radius,$fn=32);
            }
        }
        // Open cradle follows the ACTUAL curved centerline. Upper hull gives a
        // separate flared mouth, retaining the 1 mm radial free-cable allowance.
        for(i=[0:len(local_points)-2]) hull()
            for(j=[i,i+1]) for(lift=[0,12])
                translate(local_points[j]+[0,0,lift])
                    sphere(r=wire_r+(lift>0?mouth_relief:0),$fn=32);
        // One rounded, transverse tie passage. Capsule is 3.4 x 2.2 nominal;
        // entry relief flares to 4.1 x 2.9 over the last 0.5 mm each side.
        translate(p) rotate([0,0,angle]) translate([0,0,-6.5]) {
            rotate([0,90,0]) linear_extrude(30,center=true)
                hull() for(y=[-0.6,0.6]) translate([0,y])
                    circle(r=eye_outline_radius,$fn=64);
            for(side=[-1,1]) hull() for(a=[0,1])
                translate([side*(6.5+a),0,0]) rotate([0,90,0])
                    linear_extrude(0.02,center=true)
                        hull() for(y=[-0.6,0.6]) translate([0,y])
                            circle(r=eye_outline_radius+a*eye_entry_relief,$fn=64);
        }
    }
}

// Magnetic roof mount for the Seeed SenseCAP Solar Node P1 / P1-Pro.
// Six DIYMAG 1.69" magnets with 1/4" studs, Bambu P1S bed, ASA.
//
// A raked ring of rounded rails through six feet, a center spine and a hub.
// The node bolts to the hub by its two 1/4-20 back inserts, tilted 4° nose
// down. The rails follow the node's tilted box face. The front rail is a wedge
// to the panel's edge. A swept pylon behind the rear rail carries the antenna
// on its bulkhead connector, held by the bulkhead nut and washer.
// Both variants share the tapered rear recess. N-type (antenna = "alfa"): the
// nut and washer are trapped under the roof and the connector turns from above.
// Stock: the front-mount RP-SMA jack's hex body and its two washers sit in a
// round pocket under the D-flat roof, the nut tightens on top, and the cable
// leaves through the recess.
//
// +Y is the front of the car. The node's port end faces the pylon.
// Assembly: nylocs in, nylon up; node on with blue threadlocker; magnets.
// Remove by the scallops under the rear bosses, one corner first, never by the node.
//
// Print flat. ASA, light color, 6 walls, 40% infill, 4 mm brim; support the
// pylon and node screw ceilings; flat feet need none.

$fn = $preview ? 48 : 96;

/* [Output] */
// Frame or test coupon; tools/build_models.py also renders internal check parts.
part = "mount"; // [mount, coupon, foot_coupon, rear_foot_coupon, rear_left_foot_coupon, seat_coupon]
show_node = false;   // preview only

/* [Hidden] */
version = "1.0";
bed = 256;
brim = 4;            // reserved on every side, plus 1 mm bed-edge margin

/* [Node, from the datasheet] */
case_w = 191.2;
case_l = 201.2;
case_h = 42.1;
box_h = 22;          // box wall, from the side photo

/* [Node back; the screw slots cover the spread] */
insert_spacing = 39;
insert_offset = 11.5;    // insert midpoint forward of the box center, away from the port end
box_w = 110;
box_l = 141;
box_c_y = 0;             // box is centered on the panel
screw_slot = 6;          // screw holes are slots this long along Y; covers 36.5 to 42.5 mm insert spacing

/* [Seat] */
tilt = 4;
pad = [44, 70];
pad_r = 6;
screw_web = 2;
screw_hole = 6.8;
screw_access_d = 18;
screw_access_bevel = 1; // 45-degree approach to a 16 mm bearing opening

/* [Magnet feet; measure stud_len] */
magnet_d = 43;
stud_len = 12.7;     // thread above the rubber face
stud_hole = 6.8;
nut_af = 11.2;       // 1/4-20 nyloc, 7/16" across flats
nut_h = 8.4;
recess = 0;          // flat underside: eliminates the 44 mm pocket-ceiling bridge
stud_leadin = 0.4;   // 45-degree entrance relief; keeps first-layer swell out of bore
nut_leadin = 0.8;    // short hex entry chamfer, not an unbounded flared cavity
nut_clear = 0.25;    // clearance per flat, independent of hardware AF
stud_protrusion = 1.27; // one complete 1/4-20 pitch beyond the modeled nut
foot_web_min = 3;

/* [Frame] */
foot_x = 76;
foot_y = 76;        // compact footprint; antenna datum is independent of feet
bow = 5;             // front and rear rails bow outward at the center
rail_r = 12;
min_t = 9;          // rail height under the low front of the box
max_t = 18;
fillet = 5;
foot_chamfer = 0.6;  // bottom edges, against elephant's foot
ramp_half_w = 54;
ramp_t = 2.5;
dam_h = 24;          // front lip, closing the gap under the panel's skirt; the skirt underside is ~30 mm above the box face at the rim
scallop = [24, 12, 8];   // width, height, depth

/* [Antenna pylon] */
// stock: Seeed's rod on the stock RP-SMA bulkhead cable.
// alfa: ALFA AOA-915-5ACM (N male) on an RP-SMA to N-female bulkhead cable.
antenna = "alfa"; // [stock, alfa]
fin_clear = 3;       // pylon roof above the panel's rear top edge, so the whip stands clear of the node
fin_base_l = 26;
alfa = antenna == "alfa";
// The antenna screws directly onto the metal bulkhead connector. No loose
// collar, cover, keeper bolts, mounting ears or accessory fasteners.
// Connector dimensions remain provisional; measure the actual cable hardware.
n_flange = [24, 3.5];
n_coupling_d = 22;
n_coupling_h = 18;
pylon_top_r = 17.5;   // 35 mm rounded shoulder, flat flange seat above it
top_e = 4;
fin_top_l = alfa ? 2 * pylon_top_r : 24.6;
pylon_r = fin_top_l / 2;              // round pylon top
pylon_k = pylon_r / pylon_top_r;      // shoulder and rear taper scale with the top
fin_wall = alfa ? 4 : 2.5; // thicker roof carries the bulkhead directly
// Provisional Seeed 100007236 hardware envelope, NOT a verified drawing.
n_body_d = 15.875;
n_bore_leadin = 0.4;                     // 45-degree entrance chamfer
bulkhead_clear = 0.3;                     // radial
sma_d = alfa ? n_body_d + 2 * bulkhead_clear : 6.8;
sma_flat = alfa ? sma_d : 6.1;            // flat >= d: round hole
n_thread = 15;
n_nut_af = 19.1;
n_nut_h = 2.82;
n_washer = [20.5, 1.1];
n_nut_clear = 0.35;                      // per flat
n_nut_corner_d = 21.5;                  // conservative test envelope; measure actual nut corners
n_washer_clear = 0.3;                    // radial; retain nut corner engagement
tail_straight = 24;                      // free length below bulkhead thread
cable_d = 2.5;                           // RG316 nominal, check supplied cable
cable_clear = 1;                         // radial keep-out around free cable
cable_bend_r = 25;                       // conservative Belden 83284 benchmark
// Stock front-mount RP-SMA bulkhead jack, measured from a photo of the supplied
// Seeed pigtail beside a US quarter (1/4-36 pitch sets the scale at the part,
// about 3% plus 0.1 mm per edge). Cable side up: hex body, flat washer, toothed
// lock washer, then the roof, then the nut. The thread OD reads 6.06 from the
// same photo, so the 1/4-36 D-flat bore stays.
s_body_af = 8.1;       // body hex across flats, 9.4 across corners
s_body_h = 1.9;        // body hex height, read 1.7 to 1.9
s_pocket_clear = 0.7;  // radial, round pocket around the widest element
s_ferrule_d = 5.4;     // heat shrink over the crimp ferrule
s_ferrule_h = 9;       // rigid length below the hex
s_nut_af = 7.8;        // 5/16" panel nut, 9.0 across corners, on the roof
s_nut_h = 1.5;         // read 1.36 at the silhouette, chamfers hidden
s_flat_washer = [10.0, 1.0]; // on the body, under the roof
s_washer = [8.7, 2.1];       // toothed lock washer as photographed, cocked on the thread; sizes the pocket
s_washer_flat = 0.6;         // toothed washer thickness once the nut flattens it
s_stack_free = s_flat_washer[1] + s_washer[1];   // sizes the pocket
s_stack = s_flat_washer[1] + s_washer_flat;      // installed stack under the roof
s_nose_h = 0.9;        // plain socket nose above the thread
s_thread_len = 10.25;  // threaded length above the body, 11.2 to the tip, +-0.5
s_mate_engage = 4;     // antenna coupling thread above the nut
s_panel_max = s_thread_len - s_stack - s_nut_h - s_mate_engage;
s_cable_d = 2.9;       // grey jacket read 2.88 at the table
s_bend_r = 15;         // RG316 minimum bend
s_tail_straight = 9.5; // heat shrink tail below the ferrule, Ø4.6, kept straight
s_recess_floor = 22;   // the stock bowl stays above the lower pylon
s_pocket_d = max(s_body_af / cos(30), s_flat_washer[0], s_washer[0]) + 2 * s_pocket_clear;
// The N-type nut is spun up by hand in the chamber and stops turning in a rounded
// hex trap under the roof; the last turn is on the connector, from above. The
// stock body and both washers rise into a round pocket; the D-flat bore keys it.
trap_h = alfa ? n_nut_h + n_washer[1] + 0.6 : s_body_h + s_stack_free + 0.6;
drop_straight = alfa ? tail_straight : s_tail_straight;
bend_r = alfa ? cable_bend_r : s_bend_r;
free_cable_d = alfa ? cable_d : s_cable_d;
recess_channel_w = 10; // rounded lower cable exit, before widening to hardware access
recess_channel_z = 12; // short lower exit; the taper starts immediately above the bowl
recess_flare_h = 34;
recess_arch_drop = 7; // shallow curved crown outside the hardware passage
recess_scoop_r = 14; // transverse bowl radius beneath rear access opening

floor_t = recess + stud_len - nut_h - stud_protrusion;
nut_top = floor_t + nut_h;
pocket_r = (nut_af + 2 * nut_clear) / (2 * cos(30));
nut_boss_r = pocket_r + 3.5;
boss_r = magnet_d / 2 + 2.5;

feet = [[foot_x, foot_y], [-foot_x, foot_y], [foot_x, 0], [-foot_x, 0], [foot_x, -foot_y], [-foot_x, -foot_y]];
tail_y = -foot_y - bow;

seat_c = [0, insert_offset];
drop = function(y) (y - seat_c[1]) * tan(tilt);
seat_z = min_t + 1.5 + drop(box_c_y + box_l / 2);
box_face = function(y) seat_z - drop(y);
rail_t = function(y) min(max_t, max(min_t, box_face(y) - 1.5));
fin_h = ceil(box_face(-case_l / 2) + case_h + fin_clear);
foot_top = function(y) max(rail_t(y), nut_top);
front_y = function(x) foot_y + bow * (1 - pow(x / foot_x, 2));
rear_y = function(x) -front_y(x);

pylon_gap = 11.5;  // pylon set back from the rail's rear face, clear of the panel's rear edge with the node 3 mm back in its screw slots
fin_front = tail_y - rail_r - pylon_gap;
fin_back = fin_front - fin_base_l;
hole_y = alfa ? -124 : fin_back + fin_top_l / 2;
pylon_reach = tail_y + 2;             // loft base front Y, buried in the rear rail
slot = [alfa ? 26 : 14, 12, hole_y - fin_back + 12];
slot_z = fin_h - fin_wall - trap_h - slot[1];
nose_edge = alfa ? case_l / 2 - 2 : case_l / 2 + 0.5;
y_max = max(foot_y + boss_r, foot_y + bow + rail_r, nose_edge + ramp_t / 2);
y_min = min(-foot_y - boss_r, tail_y - rail_r, hole_y - pylon_r);
length = y_max - y_min;
width = 2 * (foot_x + boss_r);
drop_z = alfa ? fin_h - n_thread : fin_h - fin_wall - s_stack - s_body_h - s_ferrule_h; // free cable starts here
cable_low_z = drop_z - drop_straight - bend_r - free_cable_d / 2 - cable_clear;

function under_box(p, r) = abs(p[0]) - r < box_w / 2 && abs(p[1] - box_c_y) - r < box_l / 2;
assert(len([for (f = feet) if (under_box(f, nut_boss_r) && foot_top(f[1]) > rail_t(f[1])) f]) == 0,
  "a nut pocket under the node's box stands taller than the rail: reduce recess or stud_len");
assert(fin_wall <= (alfa ? n_thread - n_nut_h - n_washer[1] - 2 : s_panel_max), "bulkhead thread too short for the pylon roof");
assert(alfa || s_thread_len >= s_stack + fin_wall + s_nut_h + s_mate_engage,
  "stock thread leaves no antenna engagement above the panel nut");
assert(alfa || s_pocket_d < slot[0] - 1, "stock pocket is wider than the chamber");
assert(alfa || pylon_r - s_pocket_d / 2 >= 4, "stock pocket leaves thin pylon walls");
assert(alfa || s_pocket_d > s_body_af / cos(30) + 0.6, "stock pocket does not clear the body hex corners");
assert(!alfa || hole_y - fin_back + n_nut_af / 2 / cos(30) + 0.5 < slot[2], "nut corners hit the front of the slot");
assert(!alfa || n_washer[0] + 2 * n_washer_clear + 0.8 < n_nut_af / cos(30),
  "washer passage removes nut corner engagement; recheck hardware dimensions");
assert(!alfa || fin_h - n_thread < slot_z + slot[1] - n_nut_h, "connector thread ends above the chamber; the nut cannot be started");
assert(hole_y < -case_l / 2 - 8, "whip would sit under the panel frame");
assert(length + 2 * brim + 2 <= bed && width + 2 * brim + 2 <= bed,
  str("frame plus brim/edge margin exceeds ", bed, " mm: ", width, " x ", length));
assert(floor_t - recess >= foot_web_min, "stud/nut stack leaves too little plastic: use longer studs or shorter nuts");
assert(recess >= 0 && stud_leadin >= 0 && stud_leadin < floor_t - recess - 1 && nut_leadin >= 0 && nut_leadin <= 1.5,
  "invalid magnet recess or stud-hole lead-in; retain at least 1 mm straight bore");
assert(recess + stud_len >= nut_top + stud_protrusion - 0.001, "stud does not fully engage the locknut");
assert(ramp_half_w <= foot_x - boss_r + 2, "nose wedge runs into the front pockets");
assert(cable_low_z >= 1.5, "lower pylon crowds cable bend below frame");
assert(!alfa || pylon_top_r - top_e >= n_flange[0] / 2 + 0.75,
  "flange reaches pylon roundover; increase flat seating area");
assert(pylon_r - slot[0] / 2 >= 4, "upper chamber leaves thin pylon cheeks");
assert(pylon_reach - hole_y > pylon_r, "pylon root does not reach the rear rail");

assert(!alfa || n_nut_corner_d > n_washer[0] + 2 * n_washer_clear + 0.3,
  "rounded nut envelope loses capture; measure nut corners and washer");
assert(recess_channel_w > 6 && recess_channel_w >= free_cable_d + 2*cable_clear + 2,
  "lower cable channel is too narrow for the cable keep-out and rounded walls");
assert(recess_channel_w < slot[0], "cable exit must be narrower than the hardware chamber");
assert(recess_flare_h > 12 && recess_channel_z + recess_flare_h < slot_z,
  "recess transition must finish below the nut chamber");
assert(recess_scoop_r > slot[0] / 2 - 3, "scoop radius too small for access opening");

assert(screw_access_bevel >= 0 && screw_access_d - 2*screw_access_bevel >= 16,
  "screw approach crowds the 15 mm tool envelope");

assert(n_bore_leadin >= 0 && n_bore_leadin <= fin_wall / 4, "bore lead-in removes too much bearing thickness");

module seat_frame() {
  translate([seat_c[0], seat_c[1], seat_z]) rotate([-tilt, 0, 0]) children();
}

module rpuck(p, t, r, roundover = fillet) {
  f = min(roundover, t / 2, r / 2 - 0.01);
  c = foot_chamfer;
  translate([p[0], p[1], 0]) rotate_extrude($fn = $preview ? 48 : 96) hull() {
    translate([0, c]) square([r, t - f - c]);
    square([r - c, 0.01]);
    square([0.01, t]);
    translate([r - f, t - f]) circle(r = f, $fn = 64);
  }
}

module rail(a, b) hull() { rpuck(a, rail_t(a[1]), rail_r); rpuck(b, rail_t(b[1]), rail_r); }

module polyrail(pts) for (i = [0 : len(pts) - 2]) rail(pts[i], pts[i + 1]);

// Boss whose top follows the rail rake: a hull of small pucks on a circle.
module sboss(p, r) {
  rs = 10;
  low = rail_t(p[1] + r - rs);
  high = rail_t(p[1] - r + rs);
  // Level feet need one rounded boss, avoiding coplanar hull slivers.
  if (abs(high - low) < 0.000001) rpuck(p, high, r);
  else hull() for (a = [0 : 10 : 359]) {
    q = [p[0] + (r - rs) * cos(a), p[1] + (r - rs) * sin(a)];
    rpuck(q, rail_t(q[1]), rs);
  }
}

module ring() {
  n = 24;
  for (s = [-1, 1]) {
    polyrail([for (k = [0 : n]) let(x = s * foot_x * k / n) [x, front_y(x)]]);
    polyrail([for (k = [0 : n]) [s * foot_x, foot_y - 2 * foot_y * k / n]]);
    polyrail([for (k = [0 : n]) let(x = s * foot_x * k / n) [x, rear_y(x)]]);
  }
  polyrail([for (k = [0 : 16]) [0, front_y(0) - (front_y(0) - tail_y) * k / 16]]);
  rail([0, tail_y], [0, hole_y + 6]);   // spine ends inside the pylon root
}

module nose_wedge() {
  hull() {
    translate([-ramp_half_w, nose_edge - ramp_t / 2, ramp_t / 2]) rotate([0, 90, 0]) cylinder(d = ramp_t, h = 2 * ramp_half_w, $fn = 48);
    for (k = [0 : 8]) let(x = -ramp_half_w + 2 * ramp_half_w * k / 8) rpuck([x, front_y(x)], max(rail_t(front_y(x)), dam_h), rail_r);
  }
}

module hub() {
  hull() {
    for (sx = [-1, 1], sy = [-1, 1]) {
      translate([seat_c[0] + sx * (pad[0] / 2 - pad_r), seat_c[1] + sy * (pad[1] / 2 + 4 - pad_r), 0]) cylinder(r = pad_r, h = 0.01);
      // Rounded top edges: spheres just under the seat plane, trimmed flat by the seat cut.
      seat_frame() translate([sx * (pad[0] / 2 - pad_r), sy * (pad[1] / 2 - pad_r), -pad_r / 2]) sphere(r = pad_r / 2, $fn = 24);
    }
  }
}

// A single swept envelope grows into the rear rail and center spine.
// The lower rear face retreats clear of the cable bend; no separate foot ring.
module fin() pylon_loft();

// The base front always lands at pylon_reach, so both antenna sizes blend into
// the rail; the shoulder and rear taper scale with the top radius.
function pylon_profile(z) = let(
  t = z / (fin_h - top_e),
  shoulder = pylon_r + 9.5 * pylon_k * pow(max(0, 1-z/40), 2),
  rear_radius = pylon_r - 5.5 * pylon_k * pow(1 - t, 3),
  front_radius = pylon_r + (pylon_reach - hole_y - pylon_r) * pow(max(0, 1-z/60), 2))
  [shoulder, (front_radius+rear_radius)/2, hole_y+(front_radius-rear_radius)/2];

module pylon_loft() {
  // Smooth elliptical sections lean forward into the rear rail. All stations
  // share the same angular samples, with no straight tangent patches between
  // competing solids and no overlapping thin extrusions.
  n = 128;
  d = 360/n;
  profiles = concat([[0, 0], [foot_chamfer, 0]],
    [for (k = [1 : 64]) [(fin_h-top_e)*k/64, 0]],
    [for (k = [1 : 24]) let(a = 90*k/24)
      [fin_h-top_e*(1-sin(a)), pylon_r-top_e*(1-cos(a))]]);
  points = [for (p = profiles) let(
    q = p[1] > 0 ? [p[1], p[1], hole_y] : pylon_profile(p[0]),
    chamfer = max(0, foot_chamfer-p[0]))
    for (j = [0 : n-1])
      [(q[0]-chamfer)*cos(j*d), q[2]+(q[1]-chamfer)*sin(j*d), p[0]]];
  faces = concat(
    [[for (j = [0 : n-1]) j]],
    [[for (j = [n-1 : -1 : 0]) (len(profiles)-1)*n+j]],
    [for (k = [0 : len(profiles)-2], j = [0 : n-1]) let(
      a = k*n+j, b = k*n+(j+1)%n, c = (k+1)*n+j, e = (k+1)*n+(j+1)%n)
      each [[a, e, b], [a, c, e]]]);
  polyhedron(points, faces, convexity = 12);
}

// Explicit passage from above the flange seat down into the open chamber.
module bulkhead_bore() {
  bore_bottom = alfa ? fin_h - n_thread - 1 : slot_z - 1;
  translate([0, hole_y, bore_bottom]) linear_extrude(fin_h + 1 - bore_bottom) intersection() {
    circle(d = sma_d);
    translate([-sma_d, -sma_d / 2]) square([2 * sma_d, sma_flat]);
  }
  if (alfa && n_bore_leadin > 0)
    translate([0, hole_y, fin_h - n_bore_leadin])
      cylinder(d1 = sma_d, d2 = sma_d + 2 * n_bore_leadin + 0.02, h = n_bore_leadin + 0.01);
}

module fin_cuts() {
  bulkhead_bore();
  rear_recess();
  trap_bottom = slot_z - 1;
  if (alfa) {
    // Extend the entrance into the arched chamber, preserving the nut's
    // vertical installation path and the round washer passage. Bearing roof
    // stays flat and 4 mm thick; the six corner stops remain below it.
    translate([0, hole_y, trap_bottom - 1.2])
      cylinder(r1 = (n_nut_af + 2 * n_nut_clear) / (2 * cos(30)) + 0.6,
               r2 = (n_nut_af + 2 * n_nut_clear) / (2 * cos(30)), h = 1.21, $fn = 6);
    translate([0, hole_y, trap_bottom]) {
      cylinder(d = n_washer[0] + 2 * n_washer_clear, h = fin_h - fin_wall - trap_bottom);
      cylinder(r = (n_nut_af + 2 * n_nut_clear) / (2 * cos(30)),
               h = fin_h - fin_wall - n_washer[1] + 0.2 - trap_bottom, $fn = 6);
    }
  } else {
    // Round pocket for the jack's hex body and washers at any angle; the D-flat keys it.
    translate([0, hole_y, trap_bottom])
      cylinder(d = s_pocket_d, h = fin_h - fin_wall - trap_bottom);
  }
}

function bezier(p0, p1, p2, p3, t) =
  pow(1 - t, 3) * p0 + 3 * pow(1 - t, 2) * t * p1 +
  3 * (1 - t) * t * t * p2 + t * t * t * p3;

// Nearly straight tapered sides, with short curved blends into the lower
// cable channel and upper chamber. Integrating a smoothstep gives continuous
// slope and curvature without a pinched waist.
function access_flare(t, h) =
  t < 6 ? (pow(t, 3)/36 - pow(t, 4)/432)/(h-6) :
  t > h-6 ? 1 - (pow(h-t, 3)/36 - pow(h-t, 4)/432)/(h-6) :
  (t-3)/(h-6);

// Rounded crown, simple taper and the retained curved cable floor. The cut
// stays continuous through the broadened root and out of the rear face.
module rear_recess() {
  r = 3;
  yb = hole_y - pylon_r - 8;
  yf = hole_y + slot[0]/2;
  zt = fin_h - fin_wall - trap_h;
  // The bowl must start under the arched crown at the chamber's edge, or the
  // slice polygon folds over itself.
  zc = min(drop_z - drop_straight + 8, zt - recess_arch_drop - 2);
  zb = alfa ? max(3, fin_h - 65) : s_recess_floor;
  curve = [for (k = [0 : 48]) bezier([yf, zc], [yf, zb + 10],
    [hole_y - 5, zb], [yb, zb], k / 48)];
  core_half_w = slot[0] / 2 - r;
  channel_core_w = recess_channel_w / 2 - r;
  taper = concat([[-10, channel_core_w], [recess_channel_z, channel_core_w]],
    [for (k = [1 : 68]) let(t = recess_flare_h * k / 68)
      [recess_channel_z + t,
       channel_core_w + (core_half_w - channel_core_w) * access_flare(t, recess_flare_h)]],
    [[fin_h + 10, core_half_w]]);
  minkowski() {
    intersection() {
      hull() for (i = [0 : 32]) let(
        x = -core_half_w + 2 * core_half_w * i / 32,
        rise = recess_scoop_r - sqrt(pow(recess_scoop_r, 2) - pow(x, 2)),
        roof = zt - recess_arch_drop * pow(x / core_half_w, 2))
        translate([x, 0, 0]) rotate([90, 0, 90]) linear_extrude(0.01, center = true)
          offset(delta = -r) polygon(concat([[yb, roof], [yf, roof]],
            [for (p = curve) [p[0], p[1] + rise]]));
      rotate([90, 0, 0]) linear_extrude(400, center = true)
        polygon(concat([for (p = taper) [-p[1], p[0]]],
                       [for (i = [len(taper)-1 : -1 : 0]) [taper[i][1], taper[i][0]]]));
      // Round the leading wall in plan before filleting. This preserves the
      // diagonal wall thickness and blends the bowl into the curved wall.
      translate([0, hole_y, -10]) linear_extrude(fin_h + 20) union() {
        scale([core_half_w, core_half_w - 0.5]) circle(r = 1);
        translate([-core_half_w, -80]) square([2*core_half_w, 80]);
      }
    }
    sphere(r = r, $fn = $preview ? 32 : 64);
  }
}

// Curved in plan and profile, with a steep crown where it meets the foot.
// The tip stays outside the boss. The roof's working slope exceeds 45 degrees.
module finger_scoop() {
  scale([scallop[2] + 4.6, scallop[0] / 2, scallop[1] + 4])
    rotate_extrude($fn = 96)
      polygon(concat([[0, 0]],
        [for (k = [0 : 48]) let(r = 1 - k / 48) [r, 1 - pow(r, 1.25)]]));
}

// OpenCSG draws stray lines on the cut dam/spine when displaying the nested
// hulls directly. Evaluate only the preview; export/check CSG stays optimizable.
module mount(include_pylon = true) {
  if ($preview) render(convexity = 12) mount_solid(include_pylon);
  else mount_solid(include_pylon);
}

module mount_solid(include_pylon = true) {
  difference() {
    union() {
      ring();
      nose_wedge();
      hub();
      for (f = feet)
        if (foot_top(f[1]) > rail_t(f[1]) + 0.5)
          hull() { sboss(f, boss_r); rpuck(f, foot_top(f[1]), nut_boss_r); }   // dome up to the pocket
        else sboss(f, boss_r);
      if (include_pylon) fin();
    }
    // Nothing stands proud of the seat.
    seat_frame() translate([-pad[0] / 2 - 1, -pad[1] / 2 - 1, 0.01]) cube([pad[0] + 2, pad[1] + 2, 60]);
    // Keep-out under the node's box: 1.5 mm below its face over its whole
    // footprint plus 5 mm (3 mm slot travel + 2 mm clearance), except the pad the box rests on.
    seat_frame() difference() {
      translate([-box_w / 2 - 5, box_c_y - box_l / 2 - seat_c[1] - 5, -1.5]) cube([box_w + 10, box_l + 10, 60]);
      translate([-pad[0] / 2 - 0.5, -pad[1] / 2 - 0.5, -3]) cube([pad[0] + 1, pad[1] + 1, 10]);
    }
    if (include_pylon) fin_cuts();
    // Node screws, perpendicular to the seat, heads from below.
    seat_frame() for (s = [-1, 1]) translate([0, s * insert_spacing / 2, 0]) {
      hull() for (dy = [-screw_slot / 2, screw_slot / 2]) translate([0, dy, -60]) cylinder(d = screw_hole, h = 61);
      hull() for (dy = [-screw_slot / 2, screw_slot / 2])
        translate([0, dy, -60]) cylinder(d = screw_access_d, h = 60 - screw_web - screw_access_bevel + 0.01);
      hull() for (dy = [-screw_slot / 2, screw_slot / 2])
        translate([0, dy, -screw_web - screw_access_bevel])
          cylinder(d1 = screw_access_d, d2 = screw_access_d - 2*screw_access_bevel, h = screw_access_bevel);
    }
    // Feet sit flat on the bed by default. Optional recessed variant needs
    // separate pocket-ceiling support; do not bridge a 44 mm pocket untreated.
    for (f = feet) translate([f[0], f[1], 0]) {
      top = foot_top(f[1]);
      if (recess > 0) translate([0, 0, -1]) cylinder(d = magnet_d + 1, h = recess + 1, $fn = 96);
      translate([0, 0, -1]) cylinder(d = stud_hole, h = nut_top + 2);
      if (stud_leadin > 0) translate([0, 0, recess - 0.01])
        cylinder(d1 = stud_hole + 2 * stud_leadin + 0.02, d2 = stud_hole, h = stud_leadin + 0.01);
      translate([0, 0, floor_t]) cylinder(r = pocket_r, h = fin_h + 2, $fn = 6);
      translate([0, 0, top - nut_leadin])
        cylinder(r1 = pocket_r, r2 = pocket_r + nut_leadin, h = nut_leadin + 0.01, $fn = 6);
      translate([0, 0, top]) cylinder(r = pocket_r + nut_leadin, h = fin_h + 2, $fn = 6);
    }
    // Rear finger grips retain rounded outlines with steeper printable crowns.
    for (f = [feet[4], feet[5]])
      translate([f[0], f[1], -1]) rotate([0, 0, -90 + sign(f[0]) * 45])
        translate([boss_r + 4, 0, 0]) finger_scoop();
  }
}

coupon_z = 0; // full-height pylon coupon includes the reinforced lower cheeks
module pylon_coupon() {
  translate([0, -hole_y, -coupon_z]) intersection() {
    difference() { fin(); fin_cuts(); }
    translate([-50, hole_y - 40, coupon_z]) cube([100, 100, 70]);
  }
}

module foot_coupon(rear = false, left = false) {
  fx = left ? -foot_x : foot_x;
  fy = rear ? -foot_y : foot_y;
  translate([-fx, -fy, 0]) intersection() {
    // This crop is outside the pylon's X bounds; skip its expensive recess.
    mount(include_pylon = false);
    translate([fx - boss_r - 1, fy - boss_r - 1, -1])
      cube([2 * boss_r + 2, 2 * boss_r + 2, dam_h + max_t]);
  }
}

module n_tail_clearance() {
  bz = drop_z - drop_straight;
  points = concat([[0, hole_y, drop_z]],
    [for (a = [0 : 3 : 90]) [0, hole_y - bend_r * (1 - cos(a)), bz - bend_r * sin(a)]]);
  for (i = [0 : len(points) - 2]) hull() for (j = [i, i + 1])
    translate(points[j]) sphere(d = free_cable_d + 2 * cable_clear, $fn = 48);
}

use <p1-node-model.scad>

// Visual hardware only; not part of the exported frame.
module antenna_preview() {
  translate([0, hole_y, fin_h])
    if (alfa) alfa_915(n_flange=n_flange, coupling_d=n_coupling_d, coupling_h=n_coupling_h);
    else translate([0, 0, s_nut_h]) seeed_rod();   // the rod seats on the panel nut
}
module node_ghost() {
  seat_frame() translate([0, -seat_c[1], 0]) p1_node();
  antenna_preview();
  for (f=feet) translate([f[0], f[1], recess]) magnet_foot();
}

// Actual-size provisional connector stack; exclude bearing-plane contact.
module bulkhead_hardware() {
  e = 0.01;
  translate([0, hole_y, fin_h]) if (alfa) {
    translate([0, 0, -n_thread]) cylinder(d=n_body_d, h=n_thread+n_flange[1]);
    translate([0, 0, e]) cylinder(d=n_flange[0], h=n_flange[1]-e);
    translate([0, 0, -fin_wall-n_washer[1]])
      cylinder(d=n_washer[0], h=n_washer[1]-e);
    translate([0, 0, -fin_wall-n_washer[1]-n_nut_h])
      cylinder(r=n_nut_af/(2*cos(30)), h=n_nut_h-e, $fn=6);
  } else {
    // 1/4-36 thread with its D-flat through the roof; hex body, flat washer and
    // flattened toothed washer below the roof, ferrule under the body, nut above.
    translate([0, 0, -fin_wall - s_stack - e])
      linear_extrude(s_thread_len + s_nose_h + e) intersection() {
        circle(d = 6.35);
        translate([-4, -3.175]) square([8, 5.8]);
      }
    translate([0, 0, -fin_wall - s_stack - s_body_h]) cylinder(r = s_body_af / (2 * cos(30)), h = s_body_h - e, $fn = 6);
    translate([0, 0, -fin_wall - s_stack]) cylinder(d = s_flat_washer[0], h = s_flat_washer[1] - e);
    translate([0, 0, -fin_wall - s_washer_flat]) cylinder(d = s_washer[0], h = s_washer_flat - e);
    translate([0, 0, -fin_wall - s_stack - s_body_h - s_ferrule_h]) cylinder(d = s_ferrule_d, h = s_ferrule_h);
    translate([0, 0, e]) cylinder(r = s_nut_af / (2 * cos(30)), h = s_nut_h - e, $fn = 6);
  }
}
check_dy = 0;
check_dz = 0;
module node_body(dy = check_dy, dz = check_dz) {
  seat_frame() translate([0, -seat_c[1] + dy, dz]) {
    translate([-box_w / 2, box_c_y - box_l / 2, 0]) cube([box_w, box_l, 60]);
    translate([-case_w / 2, -case_l / 2, box_h]) cube([case_w, case_l, 60]);
  }
}

// Union must be empty: no positive interference can cancel another.
// Grouping checks lets OpenSCAD reuse the same evaluated mount geometry.
module audit_checks() {
  intersection() { mount(); n_tail_clearance(); }
  intersection() { mount(); bulkhead_hardware(); }
  for (dy = [-3, 0, 3]) {
    intersection() { mount(); node_body(dy, 0); }
    intersection() { antenna_preview(); node_body(dy, 0); }
  }
}


if (part == "mount") { mount(); if (show_node) node_ghost(); }
else if (part == "plate") translate([0, -(y_min+y_max)/2, 0]) mount();
else if (part == "coupon") { assert(alfa, "coupon requires alfa"); pylon_coupon(); }
else if (part == "foot_coupon") foot_coupon();
else if (part == "rear_foot_coupon") foot_coupon(rear=true);
else if (part == "rear_left_foot_coupon") foot_coupon(rear=true, left=true);
else if (part == "seat_coupon") intersection() {
  mount(include_pylon = false); // seat crop is entirely forward of the pylon
  translate([-pad[0]/2-1, seat_c[1]-pad[1]/2-5, -1]) cube([pad[0]+2,pad[1]+10,fin_h+2]);
}
else if (part == "pylon") difference() { fin(); fin_cuts(); }
else if (part == "recess") rear_recess();
else if (part == "section") intersection() { mount(); translate([0,y_min-1,-1]) cube([width,length+2,fin_h+2]); }
else if (part == "check") intersection() { mount(); node_body(); }
else if (part == "cable_check") intersection() { mount(); n_tail_clearance(); }
else if (part == "bulkhead_check") intersection() { mount(); bulkhead_hardware(); }
else if (part == "antenna_node_check") intersection() { antenna_preview(); node_body(); }
else if (part == "audit_checks") audit_checks();
else assert(false, str("Unknown part: ", part));

echo(str("version ",version,"; one printed frame; bounds ",width," x ",length,
  " mm; seat ",seat_z," mm; antenna flange ",fin_h," mm"));

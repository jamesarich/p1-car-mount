// Visual models of the Seeed SenseCAP Solar Node P1 and antennas, for
// checking fit on the roof mount. Case size from the datasheet; the back box,
// inserts and ports measured from Seeed's product photos; skirt and box
// heights estimated. Origin at the case center on the box face, +Y away from
// the port end, +Z into the panel.

node_w = 191.2;
node_l = 201.2;
node_h = 42.1;
node_box = [110, 141, 22];   // w, l, wall height of the back box
node_box_c_y = 0;
node_insert_spacing = 39;
node_insert_offset = 11.5;
node_rim = 6;                // panel frame rim width
node_skirt_h = 8;

module p1_node() {
  color("lightgray") {
    // Back box, screws, inserts.
    difference() {
      translate([-node_box[0] / 2, node_box_c_y - node_box[1] / 2, 0]) cube(node_box);
      for (s = [-1, 1]) translate([0, node_insert_offset + s * node_insert_spacing / 2, -1]) cylinder(d = 6.4, h = 4, $fn = 24);
    }
    // Skirt from the box up and out to the panel frame.
    hull() {
      translate([-node_box[0] / 2, node_box_c_y - node_box[1] / 2, node_box[2] - 0.01]) cube([node_box[0], node_box[1], 0.01]);
      translate([-node_w / 2, -node_l / 2, node_box[2] + node_skirt_h]) cube([node_w, node_l, 0.01]);
    }
    // Panel frame.
    difference() {
      translate([-node_w / 2, -node_l / 2, node_box[2] + node_skirt_h]) cube([node_w, node_l, node_h - node_box[2] - node_skirt_h]);
      translate([-node_w / 2 + node_rim, -node_l / 2 + node_rim, node_h - 2]) cube([node_w - 2 * node_rim, node_l - 2 * node_rim, 3]);
    }
  }
  color([0.1, 0.1, 0.15]) translate([-node_w / 2 + node_rim, -node_l / 2 + node_rim, node_h - 1.99]) cube([node_w - 2 * node_rim, node_l - 2 * node_rim, 0.5]);
  // Port face: buttons, LEDs, USB-C, RP-SMA jack.
  // Port face, as seen from above with the port end to the rear: buttons on
  // the right, USB-C and the RP-SMA jack on the left.
  color("black") for (x = [24, 32, 40]) translate([x, node_box_c_y - node_box[1] / 2 - 1.5, 12]) rotate([90, 0, 0]) cylinder(d = 4, h = 1.5, $fn = 16);
  color("black") translate([-29, node_box_c_y - node_box[1] / 2 - 1, 10]) cube([9, 1, 3.5]);
  // RP-SMA jack on the left side face, 34 mm from the port end, 17 mm up, pointing outboard.
  color("gold") translate([-node_box[0] / 2, node_box_c_y - node_box[1] / 2 + 34, 17]) rotate([0, -90, 0]) cylinder(d = 6.3, h = 8, $fn = 24);
  for (s = [-1, 1]) color("gold") translate([0, node_insert_offset + s * node_insert_spacing / 2, 0]) cylinder(d = 8, h = 0.5, $fn = 24);
}

// Stock Seeed 2 dBi rod, about 195 mm, RP-SMA male. Length estimated.
module seeed_rod() {
  color("black") { cylinder(d = 10, h = 20, $fn = 24); translate([0, 0, 20]) cylinder(d = 9, h = 175, $fn = 24); }
  color("gold") translate([0, 0, -8]) cylinder(d = 8, h = 8, $fn = 24);
}

// Z=0 is the pylon's bulkhead flange seating plane. Overall antenna length
// includes the coupling; coupling stack is provisional, not a measured fit.
module alfa_915(n_flange = [24, 3.5], coupling_d = 22, coupling_h = 18) {
  color("silver") cylinder(d = n_flange[0], h = n_flange[1], $fn = 96);
  color("silver") translate([0, 0, n_flange[1]]) cylinder(d = coupling_d, h = coupling_h, $fn = 96);
  color([0.15, 0.15, 0.15]) translate([0, 0, n_flange[1] + coupling_h])
    cylinder(d = 22, h = 180 - coupling_h, $fn = 96);
  color("gold") translate([0, 0, -15]) cylinder(d = 15.875, h = 15, $fn = 64);
}

p1_node();

// DIYMAG 1.69" rubber-coated magnet with a 1/4" stud. Body height estimated.
module magnet_foot(body_h = 7, stud_len = 12.7) {
  color([0.12, 0.12, 0.12]) translate([0, 0, -body_h]) cylinder(d = 43, h = body_h, $fn = 64);
  color("silver") cylinder(d = 6.35, h = stud_len, $fn = 20);
}

// Cable as a chain of spheres along a polyline, with an RP-SMA plug at the end.
module cable(pts, d = 3.4) {
  color([0.1, 0.1, 0.1]) for (i = [0 : len(pts) - 2]) hull() { translate(pts[i]) sphere(d = d, $fn = 12); translate(pts[i + 1]) sphere(d = d, $fn = 12); }
}
module rpsma_plug() color("gold") { cylinder(d = 8, h = 10, $fn = 6); translate([0, 0, 10]) cylinder(d = 6.5, h = 5, $fn = 20); }

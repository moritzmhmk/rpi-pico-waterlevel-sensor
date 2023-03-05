$fn=64;

us_o_d = 12; // offset of ultrasonic sensor in depth direction
us_o_w = 3*2.54; // offset of ultrasonic sensor in width direction
us_d = 16.5; // diameter of ultrasonic sensor tubes

module rounded_cube(size, r, center) {
  translate(center ? [0,0,0] : [r,r,r]) minkowski() {
    cube([size[0]-2*r, size[1]-2*r, size[2]-2*r], center);
    sphere(r=r);
  }
}

pcb_o = 3 + 3; // pcb offset = thickness of wall + standoff
w = 115;
h = 65;
d = pcb_o+us_o_d+us_d+us_o_d;

module magnet_holes() {
  mh = 2.2;
  md = 3.2;

  translate([2.5,2.5,h-5-2]) cylinder(d=md, h=2*mh);
  translate([2.5,d-5-2,2.5]) rotate([-90]) cylinder(d=md, h=2*mh);
  
  translate([w-2.5,2.5,h-5-2]) cylinder(d=md, h=2*mh);
  translate([w-2.5,d-5-2,2.5]) rotate([-90]) cylinder(d=md, h=2*mh);
}

module heat_insert() {
  cylinder(d=3.5, h=3);
  translate([0,0,2]) cylinder(d1=3.5, d2=4, h=3.1);
}

module standoff() {
  translate([0,0,2]) cylinder(d1=6, d2=5.5, h=3);
}

pcb_w = 36*2.54;
pcb_h = 16*2.54;

module case_base() difference() {
  union() {
    difference() {
      rounded_cube([w,d,h], 2);
      translate([5,2,5]) cube([w-10, d-2, h-5]);
      translate([0,d-5,0]) cube([w, 100, 100]);
      translate([0,0,h-5]) cube([w, 100, 100]);
    }

    translate([(w-pcb_w)/2,0,(h-pcb_h)/2]) rotate([-90]) standoff();
    translate([(w+pcb_w)/2,0,(h-pcb_h)/2]) rotate([-90]) standoff();
    translate([(w-pcb_w)/2,0,(h+pcb_h)/2]) rotate([-90]) standoff();
    translate([(w+pcb_w)/2,0,(h+pcb_h)/2]) rotate([-90]) standoff();
  }
  translate([(w-pcb_w)/2,0,(h-pcb_h)/2]) rotate([-90]) heat_insert();
  translate([(w+pcb_w)/2,0,(h-pcb_h)/2]) rotate([-90]) heat_insert();
  translate([(w-pcb_w)/2,0,(h+pcb_h)/2]) rotate([-90]) heat_insert();
  translate([(w+pcb_w)/2,0,(h+pcb_h)/2]) rotate([-90]) heat_insert();
  
  // ultrasonic tube holes
  translate([(w-6.5-us_d)/2-us_o_w,pcb_o+us_d/2+us_o_d,0]) cylinder(d1=us_d+4, d2=us_d+0.5, h=5);
  translate([(w+6.5+us_d)/2-us_o_w,pcb_o+us_d/2+us_o_d,0]) cylinder(d1=us_d+4, d2=us_d+0.5, h=5);
  
  // bottom mounting holes
  translate([(w-90)/2,d/2,0]) cylinder(d=3.5, h=100);
  translate([(w+90)/2,d/2,0]) cylinder(d=3.5, h=100);
  
  // cable slot
  hull() {
    translate([w-10,d-10,10]) rotate([0,90]) cylinder(d=3, h=100);
    translate([w-10,d,10]) rotate([0,90]) cylinder(d=3, h=100);
  }
  
  
  magnet_holes();
}

module case_cover() difference() {
  rounded_cube([w,d,h], 2);
  translate([5,2,2]) cube([w-10, d-4, h-4]);
  cube([w, d-5, h-5]);
  magnet_holes();
}

rotate([90,0,0]) case_base();
// rotate([-90,0,0]) case_cover();
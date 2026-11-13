"""Minimal geometry for the feasibility test: M3 x 0.5 x 10 pan head, Phillips PH1, real helical thread."""
import math
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
from OCP.TopoDS import TopoDS
from OCP.ShapeFix import ShapeFix_Solid


def _thread(r_in, r_out, pitch, base_w, crest_w, z0, height):
    pts = [(r_in, 0.0), (r_in, base_w), (r_out, base_w / 2 + crest_w / 2), (r_out, base_w / 2 - crest_w / 2)]
    hel = [cq.Wire.makeHelix(pitch, pitch, r, center=cq.Vector(0, 0, dz)).Edges()[0] for r, dz in pts]
    seg = [cq.Face.makeRuledSurface(hel[i], hel[(i + 1) % 4]) for i in range(4)]
    n = int(math.ceil(height / pitch))
    faces = [f.translate(cq.Vector(0, 0, z0 + k * pitch)) for k in range(n) for f in seg]
    starts = [h.startPoint() + cq.Vector(0, 0, z0) for h in hel]
    ends = [h.endPoint() + cq.Vector(0, 0, z0 + (n - 1) * pitch) for h in hel]
    for vs in (starts, ends):
        faces.append(cq.Face.makeFromWires(cq.Wire.makePolygon(vs, close=True)))
    sew = BRepBuilderAPI_Sewing(1e-4)
    for f in faces:
        sew.Add(f.wrapped)
    sew.Perform()
    sf = ShapeFix_Solid(BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(sew.SewedShape())).Solid())
    sf.Perform()
    return cq.Solid(sf.Solid())


def build_m3_pan(L=10.0):
    d, P = 3.0, 0.5
    h = 0.6134 * P
    r_out, r_min = d / 2, d / 2 - h
    ov = 0.05 * P
    crest = P / 8
    base = crest + 2 * (h + ov) * math.tan(math.radians(30))
    th = _thread(r_min - ov, r_out, P, base, crest, -L - P, L + 2 * P)
    env = (cq.Workplane("XZ").polyline([(0, -L), (r_min - .05, -L), (r_out + .02, -L + h + .07),
                                        (r_out + .02, 0), (0, 0)]).close().revolve(360, (0, 0, 0), (0, 1, 0))).val()
    core = cq.Solid.makeCylinder(r_min, L, cq.Vector(0, 0, -L))
    body = th.fuse(core).intersect(env)
    # pan head dk 5.6, k 2.4
    dk, k, rf = 5.6, 2.4, 1.0
    head = (cq.Workplane("XY").circle(dk / 2).extrude(k).faces(">Z").edges().fillet(rf)).val()
    # Phillips PH1 approx: cross wings intersected with cone, plus center cone
    m, b, t = 3.0, 0.97, 1.5
    wings = (cq.Workplane("XY").rect(m + 2, b).extrude(10).union(cq.Workplane("XY").rect(b, m + 2).extrude(10))
             .translate((0, 0, k - t))).val()
    cone = cq.Solid.makeCone(0, m / 2 + 5, 10.0, cq.Vector(0, 0, k - m))  # 26.5 deg wing slope
    cutter = wings.intersect(cone)
    shape = body.fuse(head).cut(cutter).clean()
    return shape


def export_step(shape, path):
    cq.exporters.export(cq.Workplane().add(shape), path, "STEP")


def mesh_arrays(shape, tol=0.01):
    """float32 xyz array + uint32 triangle index array (compact transfer to the window)."""
    import numpy as np
    verts, tris = shape.tessellate(tol, 0.2)
    v = np.array([(p.x, p.y, p.z) for p in verts], dtype="<f4").ravel()
    t = np.array(tris, dtype="<u4").ravel()
    return v, t


def mesh(shape, tol=0.01):
    verts, tris = shape.tessellate(tol, 0.2)
    return [c for v in verts for c in (v.x, v.y, v.z)], [i for t in tris for i in t]

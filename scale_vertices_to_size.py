bl_info = {
    "name": "Scale Vertices to Size",
    "author": "Community Addon",
    "version": (1, 0, 0),
    "blender": (3, 1, 0),
    "location": "View3D > Sidebar > Edit",
    "description": "Scale selected vertices to an exact size using current transform pivot",
    "category": "Mesh",
}

import bpy
import bmesh
from mathutils import Vector


def selected_bbox(context):
    obj = context.edit_object
    if not obj or obj.type != 'MESH':
        return None

    bm = bmesh.from_edit_mesh(obj.data)
    verts = [v.co for v in bm.verts if v.select]

    if not verts:
        return None

    min_v = Vector(map(min, zip(*verts)))
    max_v = Vector(map(max, zip(*verts)))
    return max_v - min_v


class MESH_OT_scale_vertices_to_size(bpy.types.Operator):
    bl_idname = "mesh.scale_vertices_to_size"
    bl_label = "Scale Vertices to Size"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bbox = selected_bbox(context)
        if not bbox:
            self.report({'WARNING'}, "No vertices selected")
            return {'CANCELLED'}

        scale = Vector((1, 1, 1))
        target = context.scene.svts_target_size

        if context.scene.svts_axis_x and bbox.x != 0:
            scale.x = target / bbox.x
        if context.scene.svts_axis_y and bbox.y != 0:
            scale.y = target / bbox.y
        if context.scene.svts_axis_z and bbox.z != 0:
            scale.z = target / bbox.z

        bpy.ops.transform.resize(value=scale)
        return {'FINISHED'}


class VIEW3D_PT_scale_vertices_to_size(bpy.types.Panel):
    bl_label = "Scale Vertices to Size"
    bl_idname = "VIEW3D_PT_scale_vertices_to_size"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Edit'
    bl_context = "mesh_edit"

    def draw(self, context):
        layout = self.layout
        bbox = selected_bbox(context)

        box = layout.box()
        box.label(text="Bounding Box (Selection)", icon="MESH_CUBE")

        if bbox:
            col = box.column(align=True)
            col.label(text=f"X: {bbox.x:.4f}")
            col.label(text=f"Y: {bbox.y:.4f}")
            col.label(text=f"Z: {bbox.z:.4f}")
        else:
            box.label(text="No vertices selected")

        layout.separator()

        layout.prop(context.scene, "svts_target_size")

        row = layout.row(align=True)
        row.prop(context.scene, "svts_axis_x")
        row.prop(context.scene, "svts_axis_y")
        row.prop(context.scene, "svts_axis_z")

        layout.operator(
            "mesh.scale_vertices_to_size",
            icon="FULLSCREEN_ENTER"
        )


def register():
    bpy.utils.register_class(MESH_OT_scale_vertices_to_size)
    bpy.utils.register_class(VIEW3D_PT_scale_vertices_to_size)

    bpy.types.Scene.svts_target_size = bpy.props.FloatProperty(
        name="Target Size",
        description="Target size for selected vertices",
        default=1.0,
        unit='LENGTH'
    )

    bpy.types.Scene.svts_axis_x = bpy.props.BoolProperty(name="X", default=True)
    bpy.types.Scene.svts_axis_y = bpy.props.BoolProperty(name="Y", default=True)
    bpy.types.Scene.svts_axis_z = bpy.props.BoolProperty(name="Z", default=True)


def unregister():
    del bpy.types.Scene.svts_target_size
    del bpy.types.Scene.svts_axis_x
    del bpy.types.Scene.svts_axis_y
    del bpy.types.Scene.svts_axis_z

    bpy.utils.unregister_class(VIEW3D_PT_scale_vertices_to_size)
    bpy.utils.unregister_class(MESH_OT_scale_vertices_to_size)


if __name__ == "__main__":
    register()

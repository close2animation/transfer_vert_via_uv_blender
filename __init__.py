bl_info = {
    "name": "UV Transfer",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 90, 0),
    "location": "View3D > Tools > UV Transfer",
    "description": "Transfers vertex locations from one mesh to another based on closest UV coordinates",
    "warning": "",
    "doc_url": "",
    "category": "Mesh",
}

import bpy
from bpy.types import Operator, Menu
from mathutils import kdtree


class UVTransferOperator(Operator):
    """Transfers vertex locations from one mesh to another based on closest UV coordinates"""
    bl_idname = "mesh.uv_transfer"
    bl_label = "UV Transfer"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH' and len(context.selected_objects) == 2 and all(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        def find_closest_uv():
            """
            Finds the closest UV coordinates between mesh1 and mesh2.

            :return: A list of tuples containing the closest UV coordinate and its index in mesh2.
            :rtype: list
            """
            uv1 = mesh1.uv_layers.active.data
            uv2 = mesh2.uv_layers.active.data
            
            kd = kdtree.KDTree(len(uv2))
            for i, uv in enumerate(uv2):
                kd.insert((uv.uv.x, uv.uv.y, 0), i)
            kd.balance()

            pair_data = [kd.find((uv.uv.x, uv.uv.y, 0)) for uv in uv1]
            return pair_data

        mesh1 = context.active_object.data
        mesh2 = None
        for obj in context.selected_objects:
            if obj.data != mesh1 and obj.type == 'MESH':
                mesh2 = obj.data
                break
        
        if len(mesh1.uv_layers) == 0 or len(mesh2.uv_layers) == 0:
            self.report({'ERROR'}, "Please make sure both objects have UVs")
            return {'CANCELLED'}
                   
        if mesh2:
            pair_data = find_closest_uv()
            for i, data in enumerate(pair_data):
                idx1 = mesh1.loops[i].vertex_index
                idx2 = mesh2.loops[data[1]].vertex_index
                mesh1.vertices[idx1].co = mesh2.vertices[idx2].co
        return {'FINISHED'}
    
    
class UVTransferMenu(Menu):
    bl_idname = "OBJECT_MT_my_menu"
    bl_label = "UV Transfer Menu"
    
    def draw(self, context):
        layout = self.layout
        if UVTransferOperator.poll(context):
            layout.operator(UVTransferOperator.bl_idname)
    
def register():
    bpy.utils.register_class(UVTransferOperator)
    bpy.utils.register_class(UVTransferMenu)
    bpy.types.VIEW3D_MT_object_context_menu.append(UVTransferMenu.draw)

def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(UVTransferMenu.draw)
    bpy.utils.unregister_class(UVTransferOperator)
    bpy.utils.register_class(UVTransferMenu)
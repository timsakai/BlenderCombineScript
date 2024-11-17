import bpy

# delete combined
combined_collection = bpy.data.collections.get("Combined")
combeds = [obj for obj in combined_collection.all_objects]
if combined_collection is not None:
    for comb_obj in combeds:
        bpy.data.objects.remove(comb_obj, do_unlink=True)

# 指定したコレクション内のメッシュオブジェクトを取得
collection_name = "Parts"
collection = bpy.data.collections[collection_name]
mesh_objects = [obj for obj in collection.all_objects if obj.type == 'MESH']

# Mirrorモディファイアがついていたオブジェクトとついていなかったオブジェクトに分ける
mirror_objects = [obj for obj in mesh_objects if obj.modifiers.get("Mirror")]
no_mirror_objects = [obj for obj in mesh_objects if obj not in mirror_objects]

# tempオブジェクトをtempコレクションに挿入
temp_collection = bpy.data.collections.get("Temp")
if temp_collection is None:
    temp_collection = bpy.data.collections.new("Temp")
    bpy.context.scene.collection.children.link(temp_collection)

# 結合前メッシュオブジェクトを一時オブジェクトにコピー
temp_objects = []
for obj in mesh_objects:
    temp_obj = obj.copy()
    temp_obj.data = obj.data.copy()
    temp_collection.objects.link(temp_obj)
    temp_objects.append(temp_obj)
    
temp_objects_mirror = [obj for obj in temp_objects if obj.modifiers.get("Mirror")]
temp_objects_no_mirror = [obj for obj in temp_objects if obj not in temp_objects_mirror]

temp_objects_arrays = [temp_objects_mirror,temp_objects_no_mirror]

# 結合前メッシュオブジェクトについて、AutoSmoothAngle以上の角度を条件に辺をシャープにする
# angle = bpy.context.scene.auto_smooth_angle
bpy.ops.object.select_all(action='DESELECT')
for obj in temp_objects:
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    #bpy.ops.object.shade_smooth()
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='DESELECT')
    if bpy.context.object.modifiers.get("Auto Smooth"):
        bpy.ops.mesh.select_all(action='DESELECT')
        #bpy.ops.mesh.edges_select_sharp(sharpness=obj.data.auto_smooth_angle)
        bpy.ops.mesh.edges_select_sharp(sharpness=obj.modifiers["Auto Smooth"]["Socket_2"])
        bpy.ops.mesh.mark_sharp()
    else:
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.mark_sharp(clear=True)
    if bpy.context.object.modifiers.get("Smooth by Angle"):
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.edges_select_sharp(sharpness=obj.modifiers["Smooth by Angle"]["Input_1"])
        bpy.ops.mesh.mark_sharp()
    bpy.ops.object.editmode_toggle()

# 結合前メッシュオブジェクトについて、移動・回転・拡縮の値を適用
bpy.ops.object.select_all(action='DESELECT')
for obj in temp_objects:
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# 結合前メッシュオブジェクトについて、Armature,Mirror以外のモディファイアを適用
for obj in temp_objects:
    for mod in obj.modifiers:
        if mod.type not in {"ARMATURE"}:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=mod.name)

# 結合(Mirrorモディファイアがついていたオブジェクト、ついていなかったオブジェクト
# Mirrorモディファイアがついていたオブジェクトを結合
obj_copy_mirror = []
if temp_objects_mirror:
    bpy.ops.object.select_all(action='DESELECT')
    for obj in temp_objects_mirror:
        obj_copy = obj.copy()
        obj_copy.data = obj.data.copy()
        bpy.context.scene.collection.objects.link(obj_copy)
        obj_copy.select_set(True)
        obj_copy_mirror.append(obj_copy)
    #for test in obj_copy_mirror:
        #print("{}".test.name)
    bpy.context.view_layer.objects.active = obj_copy_mirror[0]
    bpy.ops.object.join()
    #bpy.context.object.data.normals_split_custom_set_from_vertices(mirrored_objects)
    #bpy.context.object.data.use_auto_smooth = True
    #bpy.context.object.data.auto_smooth_angle = 180
    #bpy.ops.object.shade_smooth()
    bpy.ops.object.modifier_add_node_group(asset_library_type='ESSENTIALS', asset_library_identifier="", relative_asset_identifier="geometry_nodes\\smooth_by_angle.blend\\NodeTree\\Smooth by Angle")
    bpy.context.object.modifiers["Smooth by Angle"]["Input_1"] = 3.14159
    
# 結合後のオブジェクトを設定
#print("{} is active".bpy.context.view_layer.objects.active.name)
combined_obj = bpy.context.view_layer.objects.active
combined_obj.name = collection_name + "_mirror_combined"
#combined_obj.modifiers["Mirror"].mirror_object = None

# 結合後のオブジェクトをCombinedコレクションに挿入
combined_collection = bpy.data.collections.get("Combined")
if combined_collection is None:
    combined_collection = bpy.data.collections.new("Combined")
    bpy.context.scene.collection.children.link(combined_collection)
combined_collection.objects.link(combined_obj)
bpy.context.scene.collection.objects.unlink(combined_obj)

# NoMirrorモディファイアオブジェクトを結合
obj_copy_no_mirror = []
if temp_objects_no_mirror:
    bpy.ops.object.select_all(action='DESELECT')
    for obj in temp_objects_no_mirror:
        obj_copy = obj.copy()
        obj_copy.data = obj.data.copy()
        bpy.context.scene.collection.objects.link(obj_copy)
        obj_copy.select_set(True)
        obj_copy_no_mirror.append(obj_copy)
    #for test in obj_copy_mirror:
        #print("{}".test.name)
    bpy.context.view_layer.objects.active = obj_copy_no_mirror[0]
    bpy.ops.object.join()
    #bpy.context.object.data.normals_split_custom_set_from_vertices(mirrored_objects)
    #bpy.context.object.data.use_auto_smooth = True
    #bpy.context.object.data.auto_smooth_angle = 180
    #bpy.ops.object.shade_smooth()
    
# 結合後のオブジェクトを設定
#print("{} is active".bpy.context.view_layer.objects.active.name)
combined_obj = bpy.context.view_layer.objects.active
combined_obj.name = collection_name + "_combined"

# 結合後のオブジェクトをCombinedコレクションに挿入
combined_collection = bpy.data.collections.get("Combined")
if combined_collection is None:
    combined_collection = bpy.data.collections.new("Combined")
    bpy.context.scene.collection.children.link(combined_collection)
combined_collection.objects.link(combined_obj)
bpy.context.scene.collection.objects.unlink(combined_obj)

#Combine Mirror,NoMirror
collection_name = "Combined"
collection = bpy.data.collections[collection_name]
combined_objects = [obj for obj in collection.all_objects if obj.type == 'MESH']

#アーマチュアを再設定
bpy.ops.object.select_all(action='DESELECT')
for obj in combined_objects:
    obj.select_set(True)
bpy.ops.object.join()
bpy.ops.object.modifier_add(type='ARMATURE')
bpy.context.object.modifiers["Armature"].object = bpy.data.objects["Armature"]
bpy.ops.object.modifier_remove(modifier="Armature.001")

#普通モデルを書き出し
bpy.data.objects["Armature"].select_set(True)
bpy.ops.export_scene.fbx(filepath='C:\\Users\\game6\\OneDrive\\デスクトップ\\3dmodel\\Avater\\orge\\Bengara.fbx',use_selection=True)
bpy.data.objects["Armature"].select_set(False)

#デシメート
bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'LINEAR', "proportional_size":0.0294083, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'VERTEX'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "use_duplicated_keyframes":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
bpy.ops.object.modifier_add(type='DECIMATE')
bpy.context.object.modifiers["Decimate"].ratio = 0.5

#デシメート済みをquestとして出力
bpy.data.objects["Armature"].select_set(True)
bpy.ops.export_scene.fbx(filepath='C:\\Users\\game6\\OneDrive\\デスクトップ\\3dmodel\\Avater\\orge\\Bengara_quest.fbx',use_selection=True)
bpy.data.objects["Armature"].select_set(False)

# 一時オブジェクトを削除
for temp_obj in temp_objects:
    print("unko")
    bpy.data.objects.remove(temp_obj, do_unlink=True)
    
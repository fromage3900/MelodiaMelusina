# ============================================================================
# Blender Live Link Addon for Unreal Engine
# Version: 3.3.1 - Real-time Live Sync + Safe Bake + Animation
# Developer: Milad Kambari - 3DRedbox Studio
# ============================================================================


import bpy
import json
import socket
import threading
import os
import struct
import tempfile
import hashlib
import time
import copy
from bpy.app.handlers import persistent

# ============================================================================
# STATE
# ============================================================================

class LiveLinkState:
    is_connected = False
    is_live = False
    server_socket = None
    client_socket = None
    listener_thread = None
    status_message = "Disconnected"
    port = 9876
    host = "127.0.0.1"
    exchange_folder = os.path.join(tempfile.gettempdir(), "BlenderUnrealLiveLink")
    last_scene_hash = ""
    live_timer_running = False
    last_send_time = 0
    min_interval = 1.0
    scene_dirty = False
    all_sockets = []

_state = LiveLinkState()

# ============================================================================
# NETWORK
# ============================================================================

def send_message(sock, msg_type, data):
    try:
        message = json.dumps({"type": msg_type, "data": data})
        encoded = message.encode('utf-8')
        sock.sendall(struct.pack('!I', len(encoded)) + encoded)
        return True
    except Exception as e:
        print(f"[LiveLink] Send error: {e}")
        return False

def recv_exact(sock, num_bytes):
    data = b''
    while len(data) < num_bytes:
        try:
            chunk = sock.recv(num_bytes - len(data))
            if not chunk: return None
            data += chunk
        except socket.timeout: continue
        except: return None
    return data

def receive_message(sock):
    try:
        raw_len = recv_exact(sock, 4)
        if not raw_len: return None
        length = struct.unpack('!I', raw_len)[0]
        if length > 10*1024*1024: return None
        data = recv_exact(sock, length)
        if not data: return None
        return json.loads(data.decode('utf-8'))
    except: return None

# ============================================================================
# SCENE HASHING
# ============================================================================

def compute_scene_hash():
    h = hashlib.md5()
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH': continue
        h.update(obj.name.encode())
        loc = obj.location; rot = obj.rotation_euler; scale = obj.scale
        h.update(struct.pack('9f', loc.x, loc.y, loc.z, rot.x, rot.y, rot.z, scale.x, scale.y, scale.z))
        try:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            eval_obj = obj.evaluated_get(depsgraph)
            mesh = eval_obj.to_mesh()
            vc = len(mesh.vertices)
            h.update(struct.pack('i', vc))
            if vc <= 5000:
                for v in mesh.vertices:
                    h.update(struct.pack('3f', v.co.x, v.co.y, v.co.z))
            else:
                step = max(1, vc // 500)
                for i in range(0, vc, step):
                    h.update(struct.pack('3f', mesh.vertices[i].co.x, mesh.vertices[i].co.y, mesh.vertices[i].co.z))
            h.update(struct.pack('i', len(mesh.polygons)))
            eval_obj.to_mesh_clear()
        except:
            if obj.data:
                h.update(struct.pack('2i', len(obj.data.vertices), len(obj.data.polygons)))
        if obj.data and hasattr(obj.data, 'materials'):
            for mat in obj.data.materials:
                if not mat: continue
                h.update(mat.name.encode())
                h.update(struct.pack('4f', *mat.diffuse_color))
                h.update(struct.pack('2f', mat.metallic, mat.roughness))
                if mat.use_nodes and mat.node_tree:
                    for node in mat.node_tree.nodes:
                        h.update(node.type.encode())
                        for inp in node.inputs:
                            if hasattr(inp, 'default_value'):
                                val = inp.default_value
                                if hasattr(val, '__iter__'):
                                    for v in val:
                                        h.update(struct.pack('f', round(float(v), 4)))
                                else:
                                    try: h.update(struct.pack('f', round(float(val), 4)))
                                    except: pass
                        if node.type == 'TEX_IMAGE' and node.image:
                            h.update(node.image.name.encode())
                    for link in mat.node_tree.links:
                        h.update(link.from_node.name.encode())
                        h.update(link.to_socket.name.encode())
    return h.hexdigest()

# ============================================================================
# PBR BAKE
# ============================================================================

def backup_material(mat):
    """Save node tree as a Python-serializable description."""
    if not mat.use_nodes or not mat.node_tree:
        return None
    backup = {'nodes': [], 'links': []}
    for node in mat.node_tree.nodes:
        nd = {
            'type': node.bl_idname,
            'name': node.name,
            'location': (node.location.x, node.location.y),
            'inputs': {},
        }
        for inp in node.inputs:
            if hasattr(inp, 'default_value'):
                try:
                    val = inp.default_value
                    if hasattr(val, '__iter__'):
                        nd['inputs'][inp.name] = list(val)
                    else:
                        nd['inputs'][inp.name] = val
                except: pass
        if node.type == 'TEX_IMAGE' and node.image:
            nd['image'] = node.image.name
            nd['colorspace'] = node.image.colorspace_settings.name
        backup['nodes'].append(nd)
    for link in mat.node_tree.links:
        backup['links'].append({
            'from_node': link.from_node.name,
            'from_socket': link.from_socket.name,
            'to_node': link.to_node.name,
            'to_socket': link.to_socket.name,
        })
    return backup

def restore_material(mat, backup):
    """Restore node tree from backup."""
    if not backup: return
    tree = mat.node_tree
    tree.nodes.clear()
    node_map = {}
    for nd in backup['nodes']:
        try:
            node = tree.nodes.new(nd['type'])
            node.name = nd['name']
            node.location = nd['location']
            # Restore input default values safely
            for inp_name, val in nd['inputs'].items():
                if inp_name not in node.inputs:
                    continue
                inp = node.inputs[inp_name]
                if not hasattr(inp, 'default_value'):
                    continue
                try:
                    cur = inp.default_value
                    if isinstance(val, list) and hasattr(cur, '__iter__'):
                        # Match length
                        for i in range(min(len(val), len(cur))):
                            cur[i] = val[i]
                    elif isinstance(val, (int, float)) and not hasattr(cur, '__iter__'):
                        inp.default_value = val
                except:
                    pass
            # Restore image
            if 'image' in nd and nd['image'] in bpy.data.images:
                node.image = bpy.data.images[nd['image']]
                if 'colorspace' in nd:
                    try:
                        node.image.colorspace_settings.name = nd['colorspace']
                    except: pass
            node_map[nd['name']] = node
        except: pass
    for lk in backup['links']:
        try:
            fn = node_map[lk['from_node']]
            tn = node_map[lk['to_node']]
            fs = fn.outputs[lk['from_socket']]
            ts = tn.inputs[lk['to_socket']]
            tree.links.new(fs, ts)
        except: pass


def bake_and_simplify(target_objects, resolution=1024):
    """Bake complex materials, simplify them, return backups for restore."""
    tex_dir = os.path.join(_state.exchange_folder, "textures")
    os.makedirs(tex_dir, exist_ok=True)

    orig_engine = bpy.context.scene.render.engine
    orig_active = bpy.context.view_layer.objects.active
    orig_selected = [o for o in bpy.context.selected_objects]
    
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 4
    bpy.context.scene.cycles.device = 'CPU'

    mat_backups = {}
    baked_mats = set()

    for obj in target_objects:
        if obj.type != 'MESH' or not obj.data or not obj.data.materials:
            continue
        if not obj.data.uv_layers:
            print(f"[LiveLink] {obj.name}: No UV, skip")
            continue

        for mat_idx, mat_slot in enumerate(obj.material_slots):
            mat = mat_slot.material
            if not mat or not mat.use_nodes or not mat.node_tree:
                continue
            if mat.name in baked_mats:
                continue

            principled = None
            for node in mat.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    principled = node
                    break
            if not principled:
                continue

            is_simple = True
            for inp_name in ['Base Color', 'Metallic', 'Roughness', 'Normal']:
                inp = principled.inputs.get(inp_name)
                if inp and inp.links:
                    fn = inp.links[0].from_node
                    if fn.type not in ('TEX_IMAGE', 'NORMAL_MAP'):
                        is_simple = False
                        break
            if is_simple:
                continue

            mat_backups[mat.name] = backup_material(mat)
            print(f"[LiveLink] Baking: {mat.name} on {obj.name}")

            # Select only this object
            for o in bpy.context.scene.objects:
                o.select_set(False)
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            obj.active_material_index = mat_idx

            # Check if object has UV - if not, create one
            created_uv = False
            if not obj.data.uv_layers:
                print(f"[LiveLink]   No UV found, creating auto UV...")
                bake_uv = obj.data.uv_layers.new(name="UVMap")
                obj.data.uv_layers.active = bake_uv
                try:
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02, scale_to_bounds=True)
                    bpy.ops.object.mode_set(mode='OBJECT')
                    created_uv = True
                    print(f"[LiveLink]   Auto UV created")
                except Exception as e:
                    print(f"[LiveLink]   Auto UV failed: {e}")
                    try: bpy.ops.object.mode_set(mode='OBJECT')
                    except: pass

            safe = mat.name.replace('/','_').replace('\\','_').replace('.','_').replace(' ','_')
            textures = {}

            for ch_name, bake_type in [('base_color', 'DIFFUSE'), ('roughness', 'ROUGHNESS'), ('normal', 'NORMAL')]:
                img_name = f"bake_{safe}_{ch_name}"
                filepath = os.path.join(tex_dir, f"{img_name}.png")

                if img_name in bpy.data.images:
                    bimg = bpy.data.images[img_name]
                    bimg.scale(resolution, resolution)
                else:
                    bimg = bpy.data.images.new(img_name, resolution, resolution, alpha=False)
                bimg.colorspace_settings.name = 'sRGB' if ch_name == 'base_color' else 'Non-Color'

                img_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
                img_node.image = bimg
                img_node.name = "_bake_"
                mat.node_tree.nodes.active = img_node

                try:
                    if bake_type == 'DIFFUSE':
                        bpy.context.scene.render.bake.use_pass_direct = False
                        bpy.context.scene.render.bake.use_pass_indirect = False
                        bpy.context.scene.render.bake.use_pass_color = True
                    bpy.ops.object.bake(type=bake_type, margin=16, margin_type='EXTEND')
                    bimg.filepath_raw = filepath
                    bimg.file_format = 'PNG'
                    bimg.save()
                    textures[ch_name] = filepath
                    print(f"[LiveLink]   OK: {ch_name}")
                except Exception as e:
                    print(f"[LiveLink]   FAIL: {ch_name}: {e}")

                if "_bake_" in mat.node_tree.nodes:
                    mat.node_tree.nodes.remove(mat.node_tree.nodes["_bake_"])

            if textures:
                simplify_material(mat, textures)
                baked_mats.add(mat.name)
            else:
                if mat.name in mat_backups:
                    restore_material(mat, mat_backups[mat.name])
                    del mat_backups[mat.name]

    bpy.context.scene.render.engine = orig_engine
    for o in bpy.context.scene.objects:
        o.select_set(o in orig_selected)
    bpy.context.view_layer.objects.active = orig_active

    return mat_backups


def simplify_material(mat, textures):
    tree = mat.node_tree
    tree.nodes.clear()
    output = tree.nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    principled = tree.nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    tree.links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    x, y = -400, 300
    for ch, filepath in textures.items():
        img_name = os.path.basename(filepath)
        img = bpy.data.images.get(img_name) or bpy.data.images.load(filepath)
        tex = tree.nodes.new('ShaderNodeTexImage')
        tex.image = img; tex.location = (x, y)
        if ch == 'base_color':
            img.colorspace_settings.name = 'sRGB'
            tree.links.new(tex.outputs['Color'], principled.inputs['Base Color'])
        elif ch == 'roughness':
            img.colorspace_settings.name = 'Non-Color'
            tree.links.new(tex.outputs['Color'], principled.inputs['Roughness'])
        elif ch == 'normal':
            img.colorspace_settings.name = 'Non-Color'
            nm = tree.nodes.new('ShaderNodeNormalMap')
            nm.location = (x+200, y)
            tree.links.new(tex.outputs['Color'], nm.inputs['Color'])
            tree.links.new(nm.outputs['Normal'], principled.inputs['Normal'])
        y -= 300


def restore_baked_materials(backups):
    """Restore all baked materials to original state."""
    for mat_name, backup in backups.items():
        if mat_name in bpy.data.materials:
            restore_material(bpy.data.materials[mat_name], backup)
            print(f"[LiveLink] Restored: {mat_name}")

# ============================================================================
# EXPORT
# ============================================================================

def clean_exchange_folder():
    exchange = _state.exchange_folder
    os.makedirs(exchange, exist_ok=True)
    tex_dir = os.path.join(exchange, "textures")
    if os.path.isdir(tex_dir):
        for f in os.listdir(tex_dir):
            try: os.remove(os.path.join(tex_dir, f))
            except: pass
    for f in os.listdir(exchange):
        fp = os.path.join(exchange, f)
        if os.path.isfile(fp):
            try: os.remove(fp)
            except: pass

def export_textures():
    tex_dir = os.path.join(_state.exchange_folder, "textures")
    os.makedirs(tex_dir, exist_ok=True)
    exported = {}
    for mat in bpy.data.materials:
        if not mat.use_nodes or not mat.node_tree: continue
        for node in mat.node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.image:
                img = node.image
                if img.name in exported: continue
                ext_map = {'PNG':'.png','JPEG':'.jpg','BMP':'.bmp','TARGA':'.tga','TIFF':'.tif','OPEN_EXR':'.exr'}
                fmt = img.file_format if img.file_format in ext_map else 'PNG'
                ext = ext_map.get(fmt, '.png')
                safe_name = img.name.replace('/','_').replace('\\','_')
                filepath = os.path.join(tex_dir, safe_name + ext)
                try:
                    orig_path = img.filepath_raw
                    orig_fmt = img.file_format
                    img.filepath_raw = filepath
                    img.file_format = fmt
                    img.save()
                    img.filepath_raw = orig_path
                    img.file_format = orig_fmt
                    exported[img.name] = filepath
                except:
                    try:
                        img.pack()
                        img.filepath_raw = filepath
                        img.file_format = fmt
                        img.save()
                        exported[img.name] = filepath
                    except: pass
    return exported

def export_material_info(tex_paths):
    materials = {}
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH' or not obj.data or not obj.data.materials: continue
        obj_mats = []
        for mat_slot in obj.material_slots:
            mat = mat_slot.material
            if not mat: continue
            mat_info = {"name": mat.name, "diffuse_color": list(mat.diffuse_color),
                        "metallic": mat.metallic, "roughness": mat.roughness,
                        "specular": mat.specular_intensity, "textures": {}}
            if mat.use_nodes and mat.node_tree:
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        role = "unknown"
                        for output in node.outputs:
                            for link in output.links:
                                sn = link.to_socket.name.lower()
                                if 'base color' in sn or 'color' in sn: role = "base_color"
                                elif 'normal' in sn: role = "normal"
                                elif 'metallic' in sn: role = "metallic"
                                elif 'roughness' in sn: role = "roughness"
                                elif 'emission' in sn: role = "emissive"
                        mat_info["textures"][role] = {
                            "image_name": node.image.name,
                            "filepath": tex_paths.get(node.image.name, ""),
                            "colorspace": node.image.colorspace_settings.name,
                        }
                    if node.type == 'BSDF_PRINCIPLED':
                        for inp_name in ['Base Color','Metallic','Roughness','Emission Color','Alpha']:
                            if inp_name in node.inputs:
                                val = node.inputs[inp_name].default_value
                                if hasattr(val, '__iter__'):
                                    mat_info[inp_name.lower().replace(' ','_')] = [round(v,4) for v in val]
                                else:
                                    mat_info[inp_name.lower().replace(' ','_')] = round(val,4)
            obj_mats.append(mat_info)
        if obj_mats:
            materials[obj.name] = obj_mats
    json_path = os.path.join(_state.exchange_folder, "materials.json")
    with open(json_path, 'w') as f:
        json.dump(materials, f, indent=2)
    return json_path

def export_fbx():
    fbx_path = os.path.join(_state.exchange_folder, "scene.fbx")
    for obj in bpy.context.scene.objects:
        obj.select_set(obj.type == 'MESH')
    if not any(o.select_get() for o in bpy.context.scene.objects):
        return None
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            with bpy.context.temp_override(area=area):
                bpy.ops.export_scene.fbx(
                    filepath=fbx_path, use_selection=True,
                    global_scale=1.0,
                    apply_unit_scale=True,
                    apply_scale_options='FBX_SCALE_ALL',
                    axis_forward='-Z', axis_up='Y',
                    use_mesh_modifiers=True, mesh_smooth_type='FACE',
                    path_mode='COPY', embed_textures=True, batch_mode='OFF',
                    use_space_transform=True,
                    bake_space_transform=False,
                )
            return fbx_path
    bpy.ops.export_scene.fbx(
        filepath=fbx_path, use_selection=False,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z', axis_up='Y',
        use_mesh_modifiers=True, mesh_smooth_type='FACE',
        path_mode='COPY', embed_textures=True, batch_mode='OFF',
        use_space_transform=True,
        bake_space_transform=False,
    )
    return fbx_path

def export_fbx_selected(selected_objects):
    fbx_path = os.path.join(_state.exchange_folder, "selected.fbx")
    try:
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
    except: pass
    for obj in bpy.context.scene.objects:
        obj.select_set(False)
    for obj in selected_objects:
        obj.select_set(True)
    if selected_objects:
        bpy.context.view_layer.objects.active = selected_objects[0]
    if not any(o.select_get() for o in bpy.context.scene.objects):
        return None
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            with bpy.context.temp_override(area=area):
                bpy.ops.export_scene.fbx(
                    filepath=fbx_path, use_selection=True,
                    global_scale=1.0,
                    apply_unit_scale=True,
                    apply_scale_options='FBX_SCALE_ALL',
                    axis_forward='-Z', axis_up='Y',
                    use_mesh_modifiers=True, mesh_smooth_type='FACE',
                    path_mode='COPY', embed_textures=True, batch_mode='OFF',
                    use_space_transform=True,
                    bake_space_transform=False,
                )
            return fbx_path
    return None

# ============================================================================
# ANIMATION EXPORT
# ============================================================================

def detect_armature(obj):
    """Find armature for a mesh object."""
    if obj.type == 'ARMATURE':
        return obj
    # Check parent
    if obj.parent and obj.parent.type == 'ARMATURE':
        return obj.parent
    # Check modifiers
    for mod in obj.modifiers:
        if mod.type == 'ARMATURE' and mod.object:
            return mod.object
    return None

def has_any_animation(obj):
    """Return True if the object has any animation (armature-based or object-level)."""
    # Direct armature
    if obj.type == 'ARMATURE':
        return True
    # Mesh driven by an armature (parent or modifier)
    if obj.type == 'MESH' and detect_armature(obj):
        return True
    # Object-level animation: active action, NLA strips, or drivers
    ad = obj.animation_data
    if ad:
        if ad.action:
            return True
        if ad.nla_tracks and len(ad.nla_tracks) > 0:
            for tr in ad.nla_tracks:
                if len(tr.strips) > 0:
                    return True
        if ad.drivers and len(ad.drivers) > 0:
            return True
    # Rigid body physics simulation
    if obj.rigid_body is not None:
        return True
    # Shape key animation
    if obj.type == 'MESH' and obj.data and obj.data.shape_keys:
        sk = obj.data.shape_keys
        if sk.animation_data and (sk.animation_data.action or len(sk.animation_data.nla_tracks) > 0):
            return True
    # Animation inherited from an animated parent
    par = obj.parent
    while par:
        pad = par.animation_data
        if pad and (pad.action or (pad.nla_tracks and any(len(t.strips) > 0 for t in pad.nla_tracks))):
            return True
        if par.type == 'ARMATURE':
            return True
        par = par.parent
    return False

def get_armature_meshes(armature):
    """Get all mesh children of an armature."""
    meshes = []
    for child in armature.children:
        if child.type == 'MESH':
            meshes.append(child)
    return meshes

def collect_animation_objects():
    """Collect selected armatures and their meshes, or meshes with armatures."""
    armatures = set()
    for obj in bpy.context.selected_objects:
        if obj.type == 'ARMATURE':
            armatures.add(obj)
        elif obj.type == 'MESH':
            arm = detect_armature(obj)
            if arm:
                armatures.add(arm)
    return list(armatures)

def get_action_fcurves(action):
    """Get fcurves from action, compatible with Blender 4.x and 5.x."""
    # Blender 5.0+: use channelbag API
    if hasattr(action, 'slots'):
        fcurves = []
        for slot in action.slots:
            for layer in action.layers:
                for strip in layer.strips:
                    if hasattr(strip, 'channelbags'):
                        for cb in strip.channelbags:
                            if cb.slot_handle == slot.handle:
                                fcurves.extend(cb.fcurves)
        return fcurves
    # Blender 4.x: legacy API
    if hasattr(action, 'fcurves'):
        return list(action.fcurves)
    return []

def get_actions_for_armature(armature):
    """Get all actions that belong to this armature."""
    actions = []
    # Current action
    if armature.animation_data and armature.animation_data.action:
        actions.append(armature.animation_data.action)
    # All actions that match this armature's bone names
    arm_bones = set(b.name for b in armature.pose.bones)
    for action in bpy.data.actions:
        if action in actions:
            continue
        # Check if action has fcurves for this armature's bones
        fcurves = get_action_fcurves(action)
        matched = False
        for fc in fcurves:
            dp = fc.data_path
            if 'pose.bones' in dp:
                bone_name = dp.split('"')[1] if '"' in dp else ''
                if bone_name in arm_bones:
                    matched = True
                    break
        if matched:
            actions.append(action)
    return actions

def export_fbx_animation(armature, action=None, all_actions=False):
    """Export armature with animation as FBX.

    NOTE: bake_anim_use_all_actions and bake_anim_use_nla_strips are FORCED to
    follow `all_actions`. When all_actions=False (Send Animation), only the
    SINGLE active action is exported -> exactly 1 animation asset in Unreal,
    no _001 _002 _003 duplicates from leftover/fake-user actions or NLA strips.
    """
    if all_actions:
        fbx_path = os.path.join(_state.exchange_folder, f"anim_{armature.name}_all.fbx")
    elif action:
        safe_name = action.name.replace('/','_').replace('\\','_').replace(' ','_')
        fbx_path = os.path.join(_state.exchange_folder, f"anim_{armature.name}_{safe_name}.fbx")
    else:
        fbx_path = os.path.join(_state.exchange_folder, f"anim_{armature.name}.fbx")

    try:
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
    except: pass

    # Select armature and its meshes
    for obj in bpy.context.scene.objects:
        obj.select_set(False)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    for child in armature.children:
        if child.type == 'MESH':
            child.select_set(True)

    # Set active action if specified
    orig_action = None
    if action and not all_actions:
        if armature.animation_data:
            orig_action = armature.animation_data.action
            armature.animation_data.action = action

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            with bpy.context.temp_override(area=area):
                bpy.ops.export_scene.fbx(
                    filepath=fbx_path, use_selection=True,
                    global_scale=1.0,
                    apply_unit_scale=True,
                    apply_scale_options='FBX_SCALE_ALL',
                    axis_forward='X', axis_up='Z',
                    use_mesh_modifiers=True,
                    mesh_smooth_type='FACE',
                    add_leaf_bones=False,
                    primary_bone_axis='Y',
                    secondary_bone_axis='X',
                    use_armature_deform_only=True,
                    bake_anim=True,
                    bake_anim_use_all_bones=True,
                    bake_anim_use_nla_strips=all_actions,
                    bake_anim_use_all_actions=all_actions,
                    bake_anim_force_startend_keying=True,
                    bake_anim_step=1.0,
                    bake_anim_simplify_factor=1.0,
                    path_mode='COPY',
                    embed_textures=True,
                    batch_mode='OFF',
                    use_space_transform=True,
                    bake_space_transform=False,
                )
            break

    # Restore original action
    if orig_action is not None and armature.animation_data:
        armature.animation_data.action = orig_action

    if os.path.exists(fbx_path):
        return fbx_path
    return None

def export_object_animation_as_skeletal(obj):
    """Convert an object-level animated mesh to a temp single-bone skeletal FBX.
    Creates a temporary armature, bakes the object's transform animation onto a
    bone, binds the mesh, exports, then cleans up everything."""
    scene = bpy.context.scene
    fbx_path = os.path.join(_state.exchange_folder, f"anim_{obj.name}.fbx")

    # Use the FULL scene timeline so the entire animation is baked, not just part
    f_start = scene.frame_start
    f_end = scene.frame_end
    # Extend to cover the action range if it goes beyond the scene range
    if obj.animation_data and obj.animation_data.action:
        fr = obj.animation_data.action.frame_range
        f_start = min(f_start, int(fr[0]))
        f_end = max(f_end, int(fr[1]))

    temp_arm = None
    temp_mesh = None
    created = []
    orig_active = bpy.context.view_layer.objects.active
    orig_selection = [o for o in bpy.context.selected_objects]

    try:
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # If the object uses rigid body physics, bake the simulation cache first
        # so the visual-keying bake captures the correct per-frame positions.
        if obj.rigid_body is not None:
            try:
                scene.frame_set(f_start)
                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        with bpy.context.temp_override(area=area):
                            bpy.ops.ptcache.bake_all(bake=True)
                        break
            except Exception as _pe:
                print(f"[LiveLink] Physics bake warning: {_pe}")

        # 1) Duplicate the mesh so we never touch the user's original
        for o in scene.objects: o.select_set(False)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.duplicate()
        temp_mesh = bpy.context.view_layer.objects.active
        created.append(temp_mesh)

        # Clear the duplicate's own animation (the bone will drive it)
        temp_mesh.animation_data_clear()
        # Reset the duplicate's transform to identity so ONLY the bone drives it
        # (otherwise the mesh's own transform + bone deform = double transform)
        temp_mesh.location = (0.0, 0.0, 0.0)
        temp_mesh.rotation_euler = (0.0, 0.0, 0.0)
        temp_mesh.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        temp_mesh.scale = (1.0, 1.0, 1.0)

        # 2) Create a single-bone armature at world origin
        arm_data = bpy.data.armatures.new("LL_TempArm")
        temp_arm = bpy.data.objects.new("LL_TempArm", arm_data)
        scene.collection.objects.link(temp_arm)
        created.append(temp_arm)

        bpy.context.view_layer.objects.active = temp_arm
        bpy.ops.object.mode_set(mode='EDIT')
        eb = arm_data.edit_bones.new("Bone")
        eb.head = (0, 0, 0)
        eb.tail = (0, 0, 1)
        bpy.ops.object.mode_set(mode='OBJECT')

        # 3) Constrain the bone to follow the original object, then bake
        pbone = temp_arm.pose.bones["Bone"]
        con = pbone.constraints.new('COPY_TRANSFORMS')
        con.target = obj

        for o in scene.objects: o.select_set(False)
        temp_arm.select_set(True)
        bpy.context.view_layer.objects.active = temp_arm
        bpy.ops.object.mode_set(mode='POSE')
        # Select all pose bones (compatible with Blender 4.x and 5.x)
        for b in temp_arm.data.bones:
            try: b.select = True
            except: pass
        try:
            bpy.ops.pose.select_all(action='SELECT')
        except: pass
        bpy.ops.nla.bake(
            frame_start=f_start, frame_end=f_end,
            only_selected=False, visual_keying=True,
            clear_constraints=True, bake_types={'POSE'}
        )
        bpy.ops.object.mode_set(mode='OBJECT')

        # 4) Bind the duplicated mesh to the armature (single bone, full weight)
        vg = temp_mesh.vertex_groups.new(name="Bone")
        vg.add([v.index for v in temp_mesh.data.vertices], 1.0, 'REPLACE')
        mod = temp_mesh.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = temp_arm
        temp_mesh.parent = temp_arm

        # 5) Export skeletal FBX
        for o in scene.objects: o.select_set(False)
        temp_arm.select_set(True)
        temp_mesh.select_set(True)
        bpy.context.view_layer.objects.active = temp_arm

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                with bpy.context.temp_override(area=area):
                    bpy.ops.export_scene.fbx(
                        filepath=fbx_path, use_selection=True,
                        global_scale=1.0, apply_unit_scale=True,
                        apply_scale_options='FBX_SCALE_ALL',
                        axis_forward='X', axis_up='Z',
                        use_mesh_modifiers=True, mesh_smooth_type='FACE',
                        add_leaf_bones=False, primary_bone_axis='Y',
                        secondary_bone_axis='X', use_armature_deform_only=True,
                        bake_anim=True, bake_anim_use_all_bones=True,
                        bake_anim_use_nla_strips=False,
                        bake_anim_use_all_actions=False,
                        bake_anim_force_startend_keying=True,
                        bake_anim_step=1.0, bake_anim_simplify_factor=1.0,
                        path_mode='COPY', embed_textures=True, batch_mode='OFF',
                        use_space_transform=True, bake_space_transform=False,
                    )
                break

    except Exception as e:
        import traceback
        print("[LiveLink] Object anim error:")
        traceback.print_exc()
        _state.status_message = f"Object anim error: {e}"
        fbx_path = None
    finally:
        # 6) Cleanup temp objects
        try:
            if bpy.context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        except: pass
        for o in created:
            try:
                bpy.data.objects.remove(o, do_unlink=True)
            except: pass
        # Restore original selection
        try:
            for o in scene.objects: o.select_set(False)
            for o in orig_selection:
                try: o.select_set(True)
                except: pass
            bpy.context.view_layer.objects.active = orig_active
        except: pass

    if fbx_path and os.path.exists(fbx_path):
        return fbx_path, f_start, f_end
    return None, f_start, f_end

def do_send_animation(all_actions=False):
    """Send armature with animation to Unreal."""
    if not _state.client_socket:
        return False

    armatures = collect_animation_objects()

    # If no armature found, check for object-level animated meshes
    if not armatures:
        obj_anim_meshes = []
        for o in bpy.context.selected_objects:
            if o.type == 'MESH' and not detect_armature(o):
                ad = o.animation_data
                has_anim = False
                if ad:
                    if ad.action:
                        has_anim = True
                    elif ad.nla_tracks and any(len(t.strips) > 0 for t in ad.nla_tracks):
                        has_anim = True
                # Rigid body physics simulation counts as animation
                if o.rigid_body is not None:
                    has_anim = True
                if has_anim:
                    obj_anim_meshes.append(o)

        if not obj_anim_meshes:
            _state.status_message = "No animated object selected"
            return False

        clean_exchange_folder()
        total = 0
        for o in obj_anim_meshes:
            _state.status_message = f"Baking object animation: {o.name}..."
            fbx_path, fs, fe = export_object_animation_as_skeletal(o)
            if fbx_path:
                msg = {
                    "exchange_folder": _state.exchange_folder,
                    "fbx_path": fbx_path,
                    "scene_name": bpy.context.scene.name,
                    "armature_name": o.name,
                    "mesh_names": [o.name],
                    "animation": True,
                    "all_actions": False,
                    "action_name": (o.animation_data.action.name if o.animation_data and o.animation_data.action else o.name),
                    "frame_start": fs,
                    "frame_end": fe,
                    "bone_count": 1,
                    "world_loc": [0, 0, 0],
                    "actor_rotation": [0, 0, 0],
                }
                if send_message(_state.client_socket, "import_animation", msg):
                    total += 1
        if total > 0:
            _state.status_message = f"Sent {total} object animation(s)"
            return True
        _state.status_message = "Object animation send failed"
        return False

    clean_exchange_folder()

    total_sent = 0
    for armature in armatures:
        meshes = get_armature_meshes(armature)

        if all_actions:
            # Send ALL actions baked into one FBX
            actions = get_actions_for_armature(armature)
            _state.status_message = f"Sending {armature.name} ({len(actions)} actions)..."
            fbx_path = export_fbx_animation(armature, all_actions=True)
            if fbx_path:
                action_names = [a.name for a in actions]
                aloc = armature.matrix_world.translation
                msg = {
                    "exchange_folder": _state.exchange_folder,
                    "fbx_path": fbx_path,
                    "scene_name": bpy.context.scene.name,
                    "armature_name": armature.name,
                    "mesh_names": [m.name for m in meshes],
                    "animation": True,
                    "all_actions": True,
                    "action_names": action_names,
                    "bone_count": len(armature.data.bones),
                    "world_loc": [aloc.x * 100, -aloc.y * 100, aloc.z * 100],
                    "actor_rotation": [0, 0, 90],
                }
                ok = send_message(_state.client_socket, "import_animation", msg)
                if ok: total_sent += 1
        else:
            # Send ONLY the active action
            active_action = None
            if armature.animation_data and armature.animation_data.action:
                active_action = armature.animation_data.action

            if not active_action:
                _state.status_message = "No active action on armature"
                return False

            _state.status_message = f"Sending {armature.name} - {active_action.name}..."
            fbx_path = export_fbx_animation(armature, action=active_action)
            if fbx_path:
                aloc = armature.matrix_world.translation
                msg = {
                    "exchange_folder": _state.exchange_folder,
                    "fbx_path": fbx_path,
                    "scene_name": bpy.context.scene.name,
                    "armature_name": armature.name,
                    "mesh_names": [m.name for m in meshes],
                    "animation": True,
                    "all_actions": False,
                    "action_name": active_action.name,
                    "frame_start": int(active_action.frame_range[0]),
                    "frame_end": int(active_action.frame_range[1]),
                    "bone_count": len(armature.data.bones),
                    "world_loc": [aloc.x * 100, -aloc.y * 100, aloc.z * 100],
                    "actor_rotation": [0, 0, 90],
                }
                ok = send_message(_state.client_socket, "import_animation", msg)
                if ok: total_sent += 1

    if total_sent > 0:
        _state.status_message = f"Sent {total_sent} animation(s)"
        return True
    _state.status_message = "Animation send failed"
    return False

# ============================================================================
# HELPERS
# ============================================================================

def get_mesh_children(obj):
    meshes = []
    for child in obj.children:
        if child.type == 'MESH':
            meshes.append(child)
        meshes.extend(get_mesh_children(child))
    return meshes

def collect_selected_meshes():
    result = set()
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            result.add(obj)
        for child in get_mesh_children(obj):
            result.add(child)
    return list(result)

# ============================================================================
# SEND FUNCTIONS
# ============================================================================

def do_send_scene(is_live=False):
    if not _state.client_socket: return False
    _state.status_message = "Live sync..." if is_live else "Exporting..."
    clean_exchange_folder()
    tex_paths = export_textures()
    mat_json = export_material_info(tex_paths)
    fbx_path = export_fbx()
    if not fbx_path:
        _state.status_message = "No meshes"; return False
    objects = []
    for o in bpy.context.scene.objects:
        if o.type == 'MESH':
            objects.append({
                "name": o.name,
                "location": [o.location.x * 100, -o.location.y * 100, o.location.z * 100],
                "rotation": [o.rotation_euler.x, o.rotation_euler.y, o.rotation_euler.z],
                "scale": [o.scale.x, o.scale.y, o.scale.z],
            })
    msg = {"exchange_folder": _state.exchange_folder, "fbx_path": fbx_path,
           "materials_json": mat_json, "scene_name": bpy.context.scene.name,
           "object_count": len(objects), "objects": objects}
    ok = send_message(_state.client_socket, "import_scene", msg)
    if ok:
        _state.last_scene_hash = compute_scene_hash()
        _state.last_send_time = time.time()
        _state.status_message = f"Live: {len(objects)} obj" if is_live else f"Sent {len(objects)} obj"
    else: _state.status_message = "Send failed"
    return ok

def do_send_selected():
    if not _state.client_socket: return False
    selected = collect_selected_meshes()
    if not selected:
        _state.status_message = "No mesh selected"; return False
    names = [o.name for o in selected]
    _state.status_message = f"Sending {len(selected)} selected..."
    clean_exchange_folder()
    tex_paths = export_textures()
    mat_json = export_material_info(tex_paths)
    fbx_path = export_fbx_selected(selected)
    if not fbx_path:
        _state.status_message = "Export failed"; return False
    objects = []
    for o in selected:
        objects.append({
            "name": o.name,
            "location": [o.location.x * 100, -o.location.y * 100, o.location.z * 100],
            "rotation": [o.rotation_euler.x, o.rotation_euler.y, o.rotation_euler.z],
            "scale": [o.scale.x, o.scale.y, o.scale.z],
        })
    msg = {"exchange_folder": _state.exchange_folder, "fbx_path": fbx_path,
           "materials_json": mat_json, "scene_name": bpy.context.scene.name,
           "object_count": len(objects), "objects": objects, "selected_only": True}
    ok = send_message(_state.client_socket, "import_scene", msg)
    _state.status_message = f"Sent: {', '.join(names)}" if ok else "Send failed"
    return ok

def do_bake_and_send(selected_only=False):
    """Bake complex materials, send, then restore originals."""
    if not _state.client_socket: return False

    if selected_only:
        targets = collect_selected_meshes()
        if not targets:
            _state.status_message = "No mesh selected"; return False
    else:
        targets = [o for o in bpy.context.scene.objects if o.type == 'MESH']

    _state.status_message = f"Baking {len(targets)} objects..."
    clean_exchange_folder()

    # Bake and get backups
    backups = {}
    try:
        backups = bake_and_simplify(targets)
    except Exception as e:
        print(f"[LiveLink] Bake error: {e}")
        _state.status_message = f"Bake error: {e}"

    # Export (materials are now simplified)
    tex_paths = export_textures()
    mat_json = export_material_info(tex_paths)

    if selected_only:
        fbx_path = export_fbx_selected(targets)
    else:
        fbx_path = export_fbx()

    # Restore original materials
    if backups:
        restore_baked_materials(backups)

    if not fbx_path:
        _state.status_message = "Export failed"; return False

    names = [o.name for o in targets]
    objects = [{"name": o.name} for o in targets]
    msg = {"exchange_folder": _state.exchange_folder, "fbx_path": fbx_path,
           "materials_json": mat_json, "scene_name": bpy.context.scene.name,
           "object_count": len(objects), "objects": objects}
    if selected_only:
        msg["selected_only"] = True
    ok = send_message(_state.client_socket, "import_scene", msg)
    _state.status_message = f"Baked & sent: {len(targets)} obj" if ok else "Send failed"
    return ok

# ============================================================================
# LIVE SYNC
# ============================================================================

def live_sync_timer():
    if not _state.is_live or not _state.client_socket:
        _state.live_timer_running = False; return None
    now = time.time()
    interval = _state.min_interval
    try: interval = bpy.context.scene.livelink_props.sync_interval
    except: pass
    if now - _state.last_send_time < interval: return 0.5

    # Skip during edit mode - wait until user exits
    try:
        if bpy.context.mode != 'OBJECT':
            return 0.5
    except: pass

    # Skip if Blender is busy (undo/redo, file operations)
    try:
        if bpy.context.scene is None:
            return 0.5
    except:
        return 0.5

    try:
        current_hash = compute_scene_hash()
        if current_hash != _state.last_scene_hash:
            # Longer debounce to let topology changes settle
            time.sleep(0.5)
            stable = compute_scene_hash()
            if stable != _state.last_scene_hash:
                # Double check we're still in object mode
                try:
                    if bpy.context.mode != 'OBJECT':
                        return 0.5
                except:
                    return 0.5
                print(f"[LiveLink] Change detected, syncing...")
                do_send_scene(is_live=True)
    except Exception as e:
        print(f"[LiveLink] Live sync error: {e}")
    return 0.5

@persistent
def on_depsgraph_update(scene, depsgraph):
    if _state.is_live and _state.client_socket:
        _state.scene_dirty = True

# ============================================================================
# SERVER
# ============================================================================

def start_server():
    try:
        _state.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _state.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _state.server_socket.settimeout(1.0)
        _state.server_socket.bind((_state.host, _state.port))
        _state.server_socket.listen(1)
        try: _state.all_sockets.append(_state.server_socket)
        except: _state.all_sockets = [_state.server_socket]
        _state.status_message = f"Waiting on port {_state.port}..."
        print(f"[LiveLink DEBUG] Server started on {_state.host}:{_state.port}")
        def listen():
            print(f"[LiveLink DEBUG] Listener thread started")
            while _state.is_connected:
                try:
                    client, addr = _state.server_socket.accept()
                    print(f"[LiveLink DEBUG] Accept! Client from {addr}")
                    client.settimeout(0.5)
                    _state.client_socket = client
                    _state.status_message = f"Unreal connected from {addr[0]}"
                    print(f"[LiveLink DEBUG] client_socket set, status: {_state.status_message}")
                    try:
                        scene_name = "Scene"
                        try:
                            scene_name = bpy.context.scene.name
                        except:
                            pass
                        send_message(client, "handshake", {"version":"3.3.1","blender_version":bpy.app.version_string,"scene_name":scene_name})
                        print(f"[LiveLink DEBUG] Handshake sent")
                    except Exception as he:
                        print(f"[LiveLink DEBUG] Handshake error: {he}")
                    while _state.is_connected:
                        try:
                            msg = receive_message(client)
                            if msg is None:
                                print(f"[LiveLink DEBUG] Received None, client disconnected")
                                break
                            if msg.get("type") == "ping":
                                send_message(client, "pong", {})
                        except socket.timeout: continue
                        except Exception as re:
                            print(f"[LiveLink DEBUG] Receive error: {re}")
                            break
                    _state.client_socket = None
                    _state.status_message = "Unreal disconnected"
                    print(f"[LiveLink DEBUG] Client disconnected, waiting again...")
                except socket.timeout: continue
                except Exception as ae:
                    print(f"[LiveLink DEBUG] Accept error: {ae}")
                    break
            print(f"[LiveLink DEBUG] Listener thread ended")
        _state.listener_thread = threading.Thread(target=listen, daemon=True)
        _state.listener_thread.start()
        return True
    except Exception as e:
        print(f"[LiveLink DEBUG] Server error: {e}")
        _state.status_message = f"Error: {e}"; return False

def stop_server():
    _state.is_connected = False; _state.is_live = False
    if _state.client_socket:
        try: send_message(_state.client_socket,"disconnect",{}); _state.client_socket.close()
        except: pass
        _state.client_socket = None
    # Close ALL sockets ever created (handles orphans from multiple Start presses)
    try:
        for s in _state.all_sockets:
            try: s.close()
            except: pass
        _state.all_sockets = []
    except: pass
    if _state.server_socket:
        try: _state.server_socket.close()
        except: pass
        _state.server_socket = None
    _state.status_message = "Disconnected"; _state.last_scene_hash = ""

# ============================================================================
# OPERATORS
# ============================================================================

class LIVELINK_OT_start(bpy.types.Operator):
    bl_idname = "livelink.start"
    bl_label = "Start Live Link"
    def execute(self, context):
        if _state.is_connected:
            self.report({'WARNING'},"Already running"); return {'CANCELLED'}
        props = context.scene.livelink_props
        _state.host = props.host; _state.port = props.port; _state.is_connected = True
        if start_server(): self.report({'INFO'},"Started")
        else: _state.is_connected = False; self.report({'ERROR'},"Failed")
        return {'FINISHED'}

class LIVELINK_OT_stop(bpy.types.Operator):
    bl_idname = "livelink.stop"
    bl_label = "Stop Live Link"
    def execute(self, context):
        stop_server(); self.report({'INFO'},"Stopped"); return {'FINISHED'}

class LIVELINK_OT_send_scene(bpy.types.Operator):
    bl_idname = "livelink.send_full_scene"
    bl_label = "Send Full Scene"
    def execute(self, context):
        if not _state.client_socket: self.report({'WARNING'},"Not connected"); return {'CANCELLED'}
        if do_send_scene(): self.report({'INFO'},"Sent")
        else: self.report({'ERROR'},"Failed")
        return {'FINISHED'}

class LIVELINK_OT_send_changes(bpy.types.Operator):
    bl_idname = "livelink.send_changes"
    bl_label = "Send Changes"
    def execute(self, context):
        if not _state.client_socket: self.report({'WARNING'},"Not connected"); return {'CANCELLED'}
        if do_send_scene(): self.report({'INFO'},"Sent")
        else: self.report({'ERROR'},"Failed")
        return {'FINISHED'}

class LIVELINK_OT_send_selected(bpy.types.Operator):
    bl_idname = "livelink.send_selected"
    bl_label = "Send Selected"
    bl_description = "Send selected objects (and children) to Unreal"
    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            if obj.type == 'MESH': return True
            for c in obj.children_recursive:
                if c.type == 'MESH': return True
        return False
    def execute(self, context):
        if not _state.client_socket: self.report({'WARNING'},"Not connected"); return {'CANCELLED'}
        if do_send_selected(): self.report({'INFO'},"Sent")
        else: self.report({'ERROR'},"Failed")
        return {'FINISHED'}

class LIVELINK_OT_bake_send_scene(bpy.types.Operator):
    bl_idname = "livelink.bake_send_scene"
    bl_label = "Bake & Send Scene"
    bl_description = "Bake complex materials to PBR textures, send, then restore originals"
    def execute(self, context):
        if not _state.client_socket: self.report({'WARNING'},"Not connected"); return {'CANCELLED'}
        if do_bake_and_send(selected_only=False): self.report({'INFO'},"Baked & Sent")
        else: self.report({'ERROR'},"Failed")
        return {'FINISHED'}

class LIVELINK_OT_bake_send_selected(bpy.types.Operator):
    bl_idname = "livelink.bake_send_selected"
    bl_label = "Bake & Send Selected"
    bl_description = "Bake selected objects' complex materials, send, then restore"
    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            if obj.type == 'MESH': return True
            for c in obj.children_recursive:
                if c.type == 'MESH': return True
        return False
    def execute(self, context):
        if not _state.client_socket: self.report({'WARNING'},"Not connected"); return {'CANCELLED'}
        if do_bake_and_send(selected_only=True): self.report({'INFO'},"Baked & Sent")
        else: self.report({'ERROR'},"Failed")
        return {'FINISHED'}

class LIVELINK_OT_start_live(bpy.types.Operator):
    bl_idname = "livelink.start_live"
    bl_label = "Start Live Sync"
    def execute(self, context):
        if not _state.client_socket: self.report({'WARNING'},"Not connected"); return {'CANCELLED'}
        _state.is_live = True; _state.last_scene_hash = compute_scene_hash(); _state.last_send_time = time.time()
        if not _state.live_timer_running:
            _state.live_timer_running = True; bpy.app.timers.register(live_sync_timer, first_interval=0.5)
        if on_depsgraph_update not in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)
        _state.status_message = "Live Sync: ON"; self.report({'INFO'},"Live Sync started"); return {'FINISHED'}

class LIVELINK_OT_stop_live(bpy.types.Operator):
    bl_idname = "livelink.stop_live"
    bl_label = "Stop Live Sync"
    def execute(self, context):
        _state.is_live = False
        if on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)
        _state.status_message = "Live Sync: OFF"; self.report({'INFO'},"Stopped"); return {'FINISHED'}

class LIVELINK_OT_open_url(bpy.types.Operator):
    bl_idname = "livelink.open_url"
    bl_label = "Open ArtStation"
    url: bpy.props.StringProperty(default="https://www.artstation.com/milad_kambari")
    def execute(self, context):
        import webbrowser; webbrowser.open(self.url); return {'FINISHED'}

class LIVELINK_OT_send_anim(bpy.types.Operator):
    bl_idname = "livelink.send_animation"
    bl_label = "Send Animation"
    bl_description = "Send selected object with current action to Unreal"
    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            if has_any_animation(obj): return True
        return False
    def execute(self, context):
        if not _state.client_socket: self.report({'WARNING'},"Not connected"); return {'CANCELLED'}
        if do_send_animation(all_actions=False): self.report({'INFO'},"Animation sent")
        else: self.report({'ERROR'},"Failed")
        return {'FINISHED'}

class LIVELINK_OT_send_all_anims(bpy.types.Operator):
    bl_idname = "livelink.send_all_animations"
    bl_label = "Send All Actions"
    bl_description = "Send selected object with all actions to Unreal"
    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            if has_any_animation(obj): return True
        return False
    def execute(self, context):
        if not _state.client_socket: self.report({'WARNING'},"Not connected"); return {'CANCELLED'}
        if do_send_animation(all_actions=True): self.report({'INFO'},"All animations sent")
        else: self.report({'ERROR'},"Failed")
        return {'FINISHED'}

class LIVELINK_OT_bake_anim(bpy.types.Operator):
    bl_idname = "livelink.bake_animation"
    bl_label = "Bake Animation to Model"
    bl_description = "Bake the current animation onto the selected object as clean keyframes (visual keying, full timeline)"
    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            if has_any_animation(obj): return True
        return False
    def execute(self, context):
        scene = context.scene
        f_start = scene.frame_start
        f_end = scene.frame_end
        targets = [o for o in context.selected_objects if has_any_animation(o)]
        if not targets:
            self.report({'ERROR'}, "No animated object selected"); return {'CANCELLED'}

        try:
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        except: pass

        baked = 0
        for obj in targets:
            try:
                for o in scene.objects: o.select_set(False)
                obj.select_set(True)
                context.view_layer.objects.active = obj

                if obj.type == 'ARMATURE':
                    bpy.ops.object.mode_set(mode='POSE')
                    try: bpy.ops.pose.select_all(action='SELECT')
                    except: pass
                    bpy.ops.nla.bake(frame_start=f_start, frame_end=f_end,
                                     only_selected=False, visual_keying=True,
                                     clear_constraints=False, use_current_action=True,
                                     bake_types={'POSE'})
                    bpy.ops.object.mode_set(mode='OBJECT')
                else:
                    bpy.ops.nla.bake(frame_start=f_start, frame_end=f_end,
                                     only_selected=True, visual_keying=True,
                                     clear_constraints=False, use_current_action=True,
                                     bake_types={'OBJECT'})
                baked += 1
            except Exception as e:
                self.report({'WARNING'}, f"{obj.name}: {e}")

        if baked:
            self.report({'INFO'}, f"Baked animation on {baked} object(s)")
            return {'FINISHED'}
        self.report({'ERROR'}, "Bake failed")
        return {'CANCELLED'}

# ============================================================================
# UI
# ============================================================================

class LiveLinkProperties(bpy.types.PropertyGroup):
    host: bpy.props.StringProperty(name="Host", default="127.0.0.1")
    port: bpy.props.IntProperty(name="Port", default=9876, min=1024, max=65535)
    sync_interval: bpy.props.FloatProperty(name="Sync Interval (sec)", default=1.0, min=0.5, max=10.0)

class LIVELINK_PT_panel(bpy.types.Panel):
    bl_label = "Live Link to Unreal"
    bl_idname = "LIVELINK_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Unreal'

    def draw(self, context):
        layout = self.layout
        props = context.scene.livelink_props
        # Status
        box = layout.box()
        if _state.is_connected and _state.client_socket:
            box.label(text="Status: Connected", icon='LINKED')
        elif _state.is_connected:
            box.label(text="Status: Waiting...", icon='TIME')
        else:
            box.label(text="Status: Disconnected", icon='UNLINKED')
        box.label(text=_state.status_message)
        if _state.is_live:
            box.label(text="LIVE SYNC ACTIVE", icon='REC')
        # Connection
        box2 = layout.box()
        box2.label(text="Connection", icon='WORLD')
        if not _state.is_connected:
            row = box2.row(); row.scale_y = 1.5
            row.operator("livelink.start", icon='PLAY')
            box2.prop(props, "host"); box2.prop(props, "port")
        else:
            row = box2.row(); row.scale_y = 1.5; row.alert = True
            row.operator("livelink.stop", icon='CANCEL')
        if _state.is_connected and _state.client_socket:
            # Live
            box_l = layout.box()
            box_l.label(text="Live Sync", icon='FILE_REFRESH')
            if not _state.is_live:
                r = box_l.row(); r.scale_y = 1.4; r.operator("livelink.start_live", text="Start Live Sync", icon='PLAY')
                box_l.prop(props, "sync_interval")
            else:
                r = box_l.row(); r.scale_y = 1.4; r.alert = True; r.operator("livelink.stop_live", text="Stop Live Sync", icon='PAUSE')
                box_l.prop(props, "sync_interval")
            # Send (simple materials)
            box3 = layout.box()
            box3.label(text="Send (Simple Materials)", icon='EXPORT')
            r = box3.row(); r.scale_y = 1.3; r.operator("livelink.send_full_scene", text="Send Full Scene", icon='SCENE_DATA')
            r = box3.row(); r.scale_y = 1.3; r.operator("livelink.send_selected", text="Send Selected", icon='RESTRICT_SELECT_OFF')
            # Bake & Send (complex materials)
            box_b = layout.box()
            box_b.label(text="Bake & Send (Complex Materials)", icon='RENDER_STILL')
            r = box_b.row(); r.scale_y = 1.3; r.operator("livelink.bake_send_scene", text="Bake & Send Scene", icon='SCENE_DATA')
            r = box_b.row(); r.scale_y = 1.3; r.operator("livelink.bake_send_selected", text="Bake & Send Selected", icon='RESTRICT_SELECT_OFF')
            box_b.label(text="(Bakes, sends, restores originals)", icon='INFO')
            # Selection
            sel = collect_selected_meshes()
            if sel:
                nm = ', '.join(o.name for o in list(sel)[:5])
                if len(sel) > 5: nm += f" +{len(sel)-5}"
                box_b.label(text=f"Selected: {nm} ({len(sel)})", icon='OBJECT_DATA')
            # Animation
            box_a = layout.box()
            box_a.label(text="Animation", icon='ARMATURE_DATA')
            r = box_a.row(); r.scale_y = 1.3; r.operator("livelink.send_animation", text="Send Animation", icon='ACTION')
            r = box_a.row(); r.scale_y = 1.3; r.operator("livelink.send_all_animations", text="Send All Actions", icon='NLA')
            r = box_a.row(); r.scale_y = 1.1; r.operator("livelink.bake_animation", text="Bake Animation to Model", icon='RENDER_ANIMATION')
            # Show armature info
            arm_sel = collect_animation_objects()
            if arm_sel:
                for arm in arm_sel:
                    actions = get_actions_for_armature(arm)
                    act_name = arm.animation_data.action.name if arm.animation_data and arm.animation_data.action else "None"
                    box_a.label(text=f"{arm.name}: {len(arm.data.bones)} bones, {len(actions)} actions", icon='BONE_DATA')
                    box_a.label(text=f"Active: {act_name}", icon='ACTION')
            # Info
            box4 = layout.box()
            box4.label(text="Scene Info", icon='INFO')
            mc = len([o for o in bpy.context.scene.objects if o.type == 'MESH'])
            matc = len([m for m in bpy.data.materials if m.users > 0])
            tc = len([i for i in bpy.data.images if i.users > 0 and i.name != 'Render Result'])
            box4.label(text=f"Meshes: {mc}  |  Materials: {matc}  |  Textures: {tc}")
        # Credit
        layout.separator()
        c = layout.box()
        c.label(text="Developer: Milad Kambari", icon='USER')
        c.label(text="3DRedbox Studio")
        c.operator("livelink.open_url", text="ArtStation", icon='URL')

# ============================================================================
# REGISTRATION
# ============================================================================

classes = (LiveLinkProperties, LIVELINK_OT_start, LIVELINK_OT_stop,
           LIVELINK_OT_send_scene, LIVELINK_OT_send_changes, LIVELINK_OT_send_selected,
           LIVELINK_OT_bake_send_scene, LIVELINK_OT_bake_send_selected,
           LIVELINK_OT_send_anim, LIVELINK_OT_send_all_anims, LIVELINK_OT_bake_anim,
           LIVELINK_OT_start_live, LIVELINK_OT_stop_live, LIVELINK_OT_open_url, LIVELINK_PT_panel)

def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Scene.livelink_props = bpy.props.PointerProperty(type=LiveLinkProperties)
    os.makedirs(_state.exchange_folder, exist_ok=True)
    print("[LiveLink] v3.3.1 registered")

def unregister():
    _state.is_live = False
    if on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)
    stop_server()
    for cls in reversed(classes): bpy.utils.unregister_class(cls)
    if hasattr(bpy.types.Scene, 'livelink_props'): del bpy.types.Scene.livelink_props

if __name__ == "__main__":
    register()

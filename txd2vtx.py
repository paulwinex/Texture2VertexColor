from __future__ import print_function as _pf
from pymel.core import *
import tempfile, os


def bake_texture(obj, uv_set='map1', map_size=1024, filename=None):
    filename = filename or tempfile.mktemp()
    filename = os.path.splitext(filename)[0]
    mel.surfaceSampler(target=obj, uvSet=uv_set,
                       source=obj, mapOutput='diffuseRGB', mapWidth=map_size, mapHeight=map_size,
                       max=1, mapSpace='tangent',
                       mapMaterials=1, shadows=0,
                       filename=filename, fileFormat="png",
                       superSampling=1, filterType=0,
                       filterSize=3, overscan=1, searchMethod=0,
                       useGeometryNormals=1, ignoreMirroredFaces=0, flipU=0, flipV=0
                       )
    f = PyNode(mel.createRenderNodeCB('-as2DTexture', "", 'file', ""))
    f.fileTextureName.set(filename + '.png')
    return f


def read_texture_by_vertexes(txd, obj):
    colors = []
    ind = []
    for v in obj.vtx:
        uv = v.getUV()
        clr = colorAtPoint(txd, o='RGB', u=uv[0], v=uv[1])
        colors.append(clr)
        ind.append(v.index())
    return colors, ind


def create_color_set(obj, set_name, representation='RGB'):
    cs = polyColorSet(obj, query=1, allColorSets=1) or []
    if set_name not in cs:
        polyColorSet(obj, create=1, clamped=1, rpt=representation, colorSet=set_name)
    polyColorSet(obj, currentColorSet=1, colorSet=set_name)
    # polyColorPerVertex(obj, colorDisplayOption=1)


def apply_api_colors(colors, indices, obj):
    import maya.api.OpenMaya as api
    colors = [api.MColor(i) for i in colors]
    selectionList = api.MSelectionList()
    selectionList.add(obj)
    nodeDagPath = selectionList.getDagPath(0)
    mfnMesh = api.MFnMesh(nodeDagPath)
    mfnMesh.setVertexColors(colors, indices)


def _delete_file(file_node):
    try:
        os.remove(file_node.fileTextureName.get())
    except:
        pass
    delete(file_node.inputs(type=nt.Place2dTexture))
    delete(file_node)


def transfer_diffuse_to_vertex_color(obj, set_name, uv_set='map1', map_size=1024, delete_file=True):
    obj = PyNode(obj)
    print('Bake texture for {}...'.format(obj))
    f = bake_texture(obj, uv_set=uv_set, map_size=map_size)
    print('texture to array...')
    clr, ind = read_texture_by_vertexes(f, obj)
    if delete_file:
        print('Cleanup texture file...')
        _delete_file(f)
    print('Create color set: {}'.count(set_name))
    create_color_set(obj, set_name)
    print('Asign colors...')
    apply_api_colors(clr, ind, obj.name())
    print('Complete {}'.format(obj))


def bake_selected():
    sel = selected(transforms=True)
    if not sel:
        PopupError('Objects not selected')
        return
    if not promptDialog(
        title='Bake Diffuse To Vertex Color',
        message='Enter Vertex Set Name:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel') == 'OK':
        return
    setname = promptDialog(query=True, text=True)
    for obj in sel:
        transfer_diffuse_to_vertex_color(obj, setname)

# PREVILGT ##############################################################


def rename_color_set(obj, new_name, old_name=None):
    import difflib
    old_name = old_name or 'colorSet1'
    all_sets = polyColorSet(obj, query=1, allColorSets=1)
    if not all_sets:
        return
    curr = difflib.get_close_matches(old_name, all_sets)
    if not curr:
        print('Color set not renamed')
        return
    polyColorSet(obj, rename=True, colorSet=old_name, newColorSet=new_name)


def prelight_object(obj, set_name):
    obj = PyNode(obj)
    with PrelightSetup():
        print('Start bake')
        mel.polyGeoSampler(obj, ids=True, su=True, cdo=True, colorBlend="overwrite", alphaBlend="overwrite")
        print('Rename color set')
        rename_color_set(obj, set_name)


class PrelightSetup(object):
    def __init__(self):
        self.objs = []

    def __enter__(self):
        print('Setup Lights')
        lst1 = ls(type='ambientLight')
        mel.CreateAmbientLight()
        lst2 = ls(type='ambientLight')
        al = list(set(lst2).difference(set(lst1)))[0]
        # mel.sets("ambientLight1", e=1, add= "defaultLightSet")
        dl = createNode('directionalLight')
        dl.intensity.set(0)
        self.objs.append(al.getTransform())
        self.objs.append(dl.getTransform())

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('Cleanup Lights')
        delete(self.objs)


def prelight_selcted():
    sel = selected(transforms=True)
    if not sel:
        PopupError('Objects not selected')
        return
    if not promptDialog(
        title='Bake Diffuse To Vertex Color',
        message='Enter Vertex Set Name:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel') == 'OK':
        return
    setname = promptDialog(query=True, text=True)
    for obj in sel:
        prelight_object(obj, setname)

# TXD2VTX

Maya script for bake texture diffuse component to vertex color.

## Install

Put file ``txd2vtx.py`` to PYTHONPATH

## Usage

### Bake texture

From code

```python
import txd2vtx
txd2vtx.transfer_diffuse_to_vertex_color(obj, 'clr_set_name')
```

Shelf button

```python
import txd2vtx
txd2vtx.bake_selected()
```

### Prelight

From code

```python
import txd2vtx
txd2vtx.prelight_object(obj, 'clr_set_name')
```

Shelf button

```python
import txd2vtx
txd2vtx.prelight_selcted()
```

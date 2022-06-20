#!/bin/bash
#Sebastian Porteiro
for f in /home/administrador/obplayer/mixter/gst_png/*.dot; do 
	dot -Tpng -o "${f%.dot}.png" "$f"
done

#!/usr/bin/env bash
# Makes the clear glass of the tea photograph see-through while the tea stays solid.
#   bash tools/clear-glass.sh            (reads tools/tea-source.webp, writes src/img/tea.webp)
# Colourless pixels (the glass) lose most of their opacity; coloured ones (tea, lime) keep
# it. Bright glints and dark rim lines keep more than the mid greys, so it still reads as glass.
GLASS=${GLASS:-0.30}   # opacity left in plain glass: 0 invisible, 1 unchanged
cd "$(dirname "$0")/.."
A="st(0,max(r(X,Y),max(g(X,Y),b(X,Y))));st(1,min(r(X,Y),min(g(X,Y),b(X,Y))));"   # brightest and darkest channel
A+="st(2,(ld(0)-ld(1))/max(ld(0),1));"                                          # saturation
A+="st(3,0.299*r(X,Y)+0.587*g(X,Y)+0.114*b(X,Y));"                              # lightness
A+="st(4,clip((ld(2)-0.14)/0.24,0,1));"                                         # 1 = tea or lime, 0 = glass
A+="st(5,clip($GLASS+clip((ld(3)-215)/35,0,1)*0.5+(1-clip((ld(3)-60)/60,0,1))*0.4,0,1));"
A+="alpha(X,Y)*(ld(4)+(1-ld(4))*ld(5))"
ffmpeg -loglevel error -y -i tools/tea-source.webp \
  -vf "crop=1094:1296:53:6,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='$A',scale=640:-2" \
  -c:v libwebp -q:v 84 src/img/tea.webp && echo "wrote src/img/tea.webp"

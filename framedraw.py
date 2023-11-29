#!/usr/bin/env python3
import svgwrite
import yaml
import sys
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def generateField(dwg, field, xstart, ystart, globalconfig):
    unitSize = globalconfig['unitsize']
    height = globalconfig['height']
    fontSize = globalconfig['fontsize']
    bottomSpace = globalconfig['bottomspace']

    frameg = dwg.g(stroke='black')
    if 'drawsize' in field:
        size = field['drawsize']
    else:
        size = field['size']
    end = xstart+unitSize*size
    frameg.add(dwg.rect((xstart, ystart), (end-xstart, height), fill='white'))
    txt=dwg.text(field['name'], (xstart+(end-xstart)/2, ystart+height/2), style='text-anchor:middle;dominant-baseline:middle')
    txt['font-size'] = fontSize
    txt['font-family'] = globalconfig['fontfamily']
    frameg.add(txt)
    if globalconfig['withsize']:
        if 'sizeunit' in field:
            unit = field['sizeunit']
        else:
            unit = globalconfig['sizeunit']
        txt=dwg.text(str(field['size'])+unit, (xstart+(end-xstart)/2,ystart+height+bottomSpace+fontSize), style='text-anchor:middle;dominant-baseline:middle')
        txt['font-size'] = fontSize
        txt['font-family'] = globalconfig['fontfamily']
        frameg.add(txt)
    
    if 'cut' in field:
        at = xstart + field['cut']*unitSize
        width = 4
        cutsize = unitSize*0.5
        #delete lines from the rectangle
        frameg.add(dwg.line((at, ystart),(at+cutsize, ystart), stroke='white'))
        frameg.add(dwg.line((at, ystart+height),(at+cutsize, ystart+height), stroke='white'))

        middle = 2
        frameg.add(dwg.polyline([(at,ystart-globalconfig['topspace']),(at-width,ystart+height/2+middle),(at+width,ystart+height/2-middle),(at,ystart+height+bottomSpace)], fill='white'))
        at = at + cutsize
        frameg.add(dwg.polyline([(at,ystart-globalconfig['topspace']),(at-width,ystart+height/2+middle),(at+width,ystart+height/2-middle),(at,ystart+height+bottomSpace)], fill='white'))

    if 'subframe' in field:
        subframesize = 0
        for subf in field['subframe']:
            if 'drawsize' in subf:
                subframesize = subframesize + subf['drawsize']
            else:
                subframesize = subframesize + subf['size']
        subframex=xstart+size*unitSize/2 #middle of current frame
        subframex=subframex-subframesize*unitSize/2 #mid-adjust with subframe size
        subframey=globalconfig['subframespacing']*field['subframerow']
        ln = dwg.line((xstart, ystart+height),(subframex, subframey), stroke = 'black')
        ln.dasharray([2,2])
        dwg.add(ln)

        for subf in field['subframe']:
            subframex = generateField(dwg, subf, subframex, subframey, globalconfig)

        ln = dwg.line((xstart+size*unitSize, ystart+height),(subframex, subframey), stroke = 'black')
        ln.dasharray([2,2])
        dwg.add(ln)
        




    dwg.add(frameg)
    return end

def draw(globalconfig, frameconfig):
    dwg = svgwrite.Drawing(globalconfig['name']+'.svg', profile='full')

    top = globalconfig['topspace']
    
    xstart = globalconfig['leftspace']
    for field in frameconfig:
        xstart = generateField(dwg, field, xstart, top, globalconfig)
    dwg.save(pretty=True)

def main():

    if len(sys.argv) < 2:
        print("Yaml file input required as argument\n")
        sys.exit(1)
    yamlfile = sys.argv[1]
    f = open(yamlfile, 'r')
    yconfig = yaml.load(f, Loader=Loader)
    f.close()
    draw(yconfig['global'], yconfig['frame'])

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import svgwrite
import yaml
import sys
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def generateField(dwg, field, bitoffset, xstart, yinitial, globalconfig):
    unitSize = globalconfig['unitsize']
    height = globalconfig['height']
    fontSize = globalconfig['fontsize']
    bottomSpace = globalconfig['bottomspace']
    maxheight = height
    if globalconfig['withbits']:
        ystart = yinitial + height
    else:
        ystart = yinitial

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
        maxheight = maxheight + bottomSpace + fontSize
    
    if globalconfig['withbits']:
        #in bits mode, we create a two line table, the first line containing bit numbers, with the first cell "Bit: N"
        frameg.add(dwg.rect((xstart, ystart-height), (end-xstart, height), fill='white'))
        if bitoffset == 0:
            bitrange = "Bits: "
        else:
            bitrange =""
        if field['size'] == 1:
            bitrange += str(bitoffset)
        else:
            bitrange += str(bitoffset) + "-" + str(bitoffset+field['size']-1)
        txt=dwg.text(bitrange, (xstart+(end-xstart)/2,ystart-height/2), style='text-anchor:middle;dominant-baseline:middle')
        txt['font-size'] = fontSize
        txt['font-family'] = globalconfig['fontfamily']
        frameg.add(txt)
        maxheight = maxheight + height
    
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

        subbitoffset = 0
        subframemaxheight = 0
        for subf in field['subframe']:
            subframex, subframeheight = generateField(dwg, subf, subbitoffset, subframex, subframey, globalconfig)
            subframemaxheight = max(subframemaxheight, subframeheight)
            if globalconfig['withbits']:
                subbitoffset = subbitoffset + subf['size']
        if subframemaxheight > 0:
            maxheight = max(maxheight, subframemaxheight + subframey)

        ln = dwg.line((xstart+size*unitSize, ystart+height),(subframex, subframey), stroke = 'black')
        ln.dasharray([2,2])
        dwg.add(ln)
        




    dwg.add(frameg)
    return end, maxheight

def draw(globalconfig, frameconfig):
    dwg = svgwrite.Drawing(globalconfig['name']+'.svg', profile='full')


    top = globalconfig['topspace']
    bitoffset = 0
    
    xstart = globalconfig['leftspace']
    maxheight = 0
    for field in frameconfig:
        xstart, fieldmaxheight = generateField(dwg, field, bitoffset, xstart, top, globalconfig)
        maxheight = max(maxheight, fieldmaxheight)
        if globalconfig['withbits']:
            bitoffset = bitoffset + field['size']
    
    #assume right space is the same as left space
    dwg.viewbox(0, 0, xstart + globalconfig['leftspace'], maxheight + globalconfig['topspace'] + globalconfig['bottomspace'])
    dwg['width'] = xstart + globalconfig['leftspace'] #assume right space is the same as left space
    dwg['height'] = maxheight + globalconfig['topspace'] + globalconfig['bottomspace']

    dwg['width'] = dwg['width']*globalconfig.get('scale', 1)
    dwg['height'] = dwg['height']*globalconfig.get('scale', 1)
    
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
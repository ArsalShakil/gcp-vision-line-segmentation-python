from shapely.geometry import Point, Polygon
import math
import copy
from box import Box

def getYMax(data):
    v = data.text_annotations[0].bounding_poly.vertices
    yArray = []
    for i in range(4):
        yArray.append(v[i].y)
    return max(yArray)

def invertAxis(data, yMax):
    data = fillMissingValues(data)
    for i in range(len(data.text_annotations)):
        v = data.text_annotations[i].bounding_poly.vertices
        for j in range(4):
            v[j].y = (yMax - v[j].y)
    return data

def fillMissingValues(data):
    for i in range(len(data.text_annotations)):
        v = data.text_annotations[i].bounding_poly.vertices
        for i, ver in enumerate(v):
            try:
                if (not ver.x):
                    ver.x = 0
            except:
                ver.x = 0
            try:
                if (not ver.y):
                    ver.y = 0
            except:
                ver.y = 0
            data.text_annotations[i].bounding_poly.vertices[i] = ver
    return data

def getBoundingPolygon(mergedArray):
    for i in range(len(mergedArray)):
        arr = []
        # calculate line height
        h1 = mergedArray[i].bounding_poly.vertices[0].y - mergedArray[i].bounding_poly.vertices[3].y
        h2 = mergedArray[i].bounding_poly.vertices[1].y - mergedArray[i].bounding_poly.vertices[2].y
        h = h1
        if(h2 > h1):
            h = h2
        avgHeight = h * 0.6

        arr.append(mergedArray[i].bounding_poly.vertices[1])
        arr.append(mergedArray[i].bounding_poly.vertices[0])
        line1 = getRectangle(copy.deepcopy(arr), True, avgHeight, True)

        arr = []
        arr.append(mergedArray[i].bounding_poly.vertices[2])
        arr.append(mergedArray[i].bounding_poly.vertices[3])
        line2 = getRectangle(copy.deepcopy(arr), True, avgHeight, False)

        mergedArray[i]['bigbb'] = createRectCoordinates(line1, line2)
        mergedArray[i]['lineNum'] = i
        mergedArray[i]['match'] = []
        mergedArray[i]['matched'] = False

    return mergedArray

def inside(point, polygon):
    p1 = Point(point[0], point[1])
    poly = Polygon(polygon)
    return p1.within(poly)

def combineBoundingPolygon(mergedArray):
    # select one word from the array
    for i in range(len(mergedArray)):
        bigBB = mergedArray[i]['bigbb']
        # iterate through all the array to find the match
        for k in range(i, len(mergedArray)):
            # Do not compare with the own bounding box and which was not matched with a line
            if(k != i and mergedArray[k]['matched'] == False):
                insideCount = 0
                for j in range(4):
                    coordinate = mergedArray[k].bounding_poly.vertices[j]
                    if(inside([coordinate.x, coordinate.y], bigBB)):
                        insideCount += 1

                # all four point were inside the big bb
                if(insideCount == 4):
                    match = {"matchCount": insideCount, "matchLineNum": k}
                    mergedArray[i]['match'].append(match)
                    mergedArray[k]['matched'] = True
    return mergedArray

def getRectangle(v, isRoundValues, avgHeight, isAdd):
    if (isAdd):
        v[1].y = v[1].y + avgHeight
        v[0].y = v[0].y + avgHeight

    else:
        v[1].y = v[1].y - avgHeight
        v[0].y = v[0].y - avgHeight

    yDiff = (v[1].y - v[0].y)
    xDiff = (v[1].x - v[0].x)

    gradient = yDiff / xDiff

    xThreshMin = 1
    xThreshMax = 2000

    if(gradient == 0):
        yMin = v[0].y
        yMax = v[0].y
    else:
        yMin = (v[0].y) - (gradient * (v[0].x - xThreshMin))
        yMax = (v[0].y) + (gradient * (xThreshMax - v[0].x))

    if(isRoundValues):
        yMin = round(yMin)
        yMax = round(yMax)
    return Box({"xMin" : xThreshMin, "xMax" : xThreshMax, "yMin": yMin, "yMax": yMax})

def createRectCoordinates(line1, line2):
    return [[line1.xMin, line1.yMin], [line1.xMax, line1.yMax], [line2.xMax, line2.yMax],[line2.xMin, line2.yMin]]
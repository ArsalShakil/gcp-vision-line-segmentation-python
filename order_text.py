import sys
import coordinatesHelper
import copy
import os
from google.cloud import vision
import cv2
from google.cloud.vision import types
import base64
from protobuf_to_dict import protobuf_to_dict
from box import Box
import numpy as np

def initLineSegmentation(data):
    data = Box(protobuf_to_dict(data))
    yMax = coordinatesHelper.getYMax(data)
    data = coordinatesHelper.invertAxis(data, yMax)

    # The first index refers to the auto identified words which belongs to a sings line
    lines = data.text_annotations[0].description.split('\n')

    # gcp vision full text
    rawText = copy.deepcopy(data.text_annotations)

    # reverse to use lifo, because array.shift() will consume 0(n)
    lines = list(reversed(list(lines)))
    rawText = list(reversed(list(rawText)))
    # to remove the zeroth element which gives the total summary of the text
    rawText.pop()

    mergedArray = getMergedLines(lines, rawText)
    mergedArray = coordinatesHelper.getBoundingPolygon(mergedArray)
    mergedArray = coordinatesHelper.combineBoundingPolygon(mergedArray)
    # This does the line segmentation based on the bounding boxes
    return constructLineWithBoundingPolygon(mergedArray)

def constructLineWithBoundingPolygon(mergedArray):
    finalArray = []

    for i in range(len(mergedArray)):
        if(not mergedArray[i]['matched']):
            if (len(mergedArray[i]['match']) == 0):
                finalArray.append(mergedArray[i].description)
            else:
                # arrangeWordsInOrder(mergedArray, i)
                # index = mergedArray[i]['match'][0]['matchLineNum']
                # secondPart = mergedArray[index].description
                # finalArray.append(mergedArray[i].description + ' ' +secondPart)
                line = arrangeWordsInOrder(mergedArray, i)
                finalArray.append(line)

    return finalArray

def getMergedLines(lines,rawText):

    mergedArray = []
    while (len(lines) != 1):
        l = lines.pop()
        l1 = copy.deepcopy(l)
        status = True

        data = ""

        while (True):
            wElement = rawText.pop()
            if( not wElement):
                break

            w = wElement.description

            index = l.index(w)
            # check if the word is inside
            l = l[index + len(w):]
            if(status):
                status = False
                # set starting coordinates
                mergedElement = wElement

            if(l == "" or not l):
                # set ending coordinates
                mergedElement.description = l1
                mergedElement.bounding_poly.vertices[1] = wElement.bounding_poly.vertices[1]
                mergedElement.bounding_poly.vertices[2] = wElement.bounding_poly.vertices[2]
                mergedArray.append(mergedElement)
                break

    return mergedArray

def arrangeWordsInOrder(mergedArray, k):
    mergedLine = ''
    mergedIndexes = [k]
    mergedX = [mergedArray[k].bounding_poly.vertices[0].x]
    merged_text = [mergedArray[k].description]
    line = mergedArray[k]['match']
    # [0]['matchLineNum']
    for i in range(len(line)):
        index = line[i]['matchLineNum']
        mergedIndexes.append(index)
        mergedX.append(mergedArray[index].bounding_poly.vertices[0].x)
        merged_text.append(mergedArray[index].description)
    sorted_indexes = np.argsort(mergedX)
    for current_index in sorted_indexes:
        mergedLine += merged_text[current_index] + " "
    return mergedLine

def order_text(response):
    return "\n".join(initLineSegmentation(response))
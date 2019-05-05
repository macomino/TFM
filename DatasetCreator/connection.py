import pygame as pg
import math

class Connection:

    margin = 20

    def GetConnectionLine(self, origin, destination, source, sink):

        linePoints = []

        rectSource = self.GetRectWithMargin(origin, self.margin)
        rectSink = self.GetRectWithMargin(destination, self.margin)
      
        startPoint = self.GetOffsetPoint(source, rectSource)
        endPoint = self.GetOffsetPoint(sink, rectSink)

        linePoints.append(startPoint)
        currentPoint = startPoint

        if not rectSink.collidepoint(currentPoint[0], currentPoint[1]) and not rectSource.collidepoint(endPoint[0], endPoint[1]):
            while True:
                if self.IsPointVisible(currentPoint, endPoint, [rectSource, rectSink]):
                    linePoints.append(endPoint)
                    currentPoint = endPoint
                    break

                neighbour = self.GetNearestVisibleNeighborSink(currentPoint, endPoint, sink, rectSource, rectSink)
                if not math.isnan(neighbour[0]):
                    linePoints.append(neighbour)
                    linePoints.append(endPoint)
                    currentPoint = endPoint

                if currentPoint == startPoint:
                    n, flag = self.GetNearestNeighborSource(source, endPoint, rectSource, rectSink)
                    linePoints.append(n)
                    currentPoint = n

                    if not self.IsRectVisible(currentPoint, rectSink, [rectSource]):
                        n1, n2 = self.GetOppositeCorners(source, rectSource)
                        if flag:
                            linePoints.append(n1)
                            currentPoint = n1
                        else:
                            linePoints.append(n2)
                            currentPoint = n2
                        
                        if not self.IsRectVisible(currentPoint, rectSink, [rectSource]):
                            if flag:
                                linePoints.append(n2)
                                currentPoint = n2
                            else:
                                linePoints.append(n1)
                                currentPoint = n1
                else:
                    s1, s2 = self.GetNeighborCorners(sink, rectSink)
                    n1, n2 = self.GetOppositeCorners(sink, rectSink)

                    n1Visible = self.IsPointVisible(currentPoint, n1, [rectSource, rectSink])
                    n2Visible = self.IsPointVisible(currentPoint, n2, [rectSource, rectSink])

                    if n1Visible and n2Visible:
                        if rectSource.collidepoint(n1):
                            linePoints.append(n2)
                            if rectSource.collidepoint(s2):
                                linePoints.append(n1)
                                linePoints.append(s1)
                            else:
                                linePoints.append(s2)
                            
                            linePoints.append(endPoint)
                            currentPoint = endPoint
                            break

                        if rectSource.collidepoint(n2):
                            linePoints.append(n1)
                            if rectSource.collidepoint(s1):
                                linePoints.append(n2)
                                linePoints.append(s2)
                            else:
                                linePoints.append(s1)
                            
                            linePoints.append(endPoint)
                            currentPoint = endPoint
                            break
                        
                        if self.Distance(n1, endPoint) <= self.Distance(n2, endPoint):
                            linePoints.append(n1)
                            if rectSource.collidepoint(s1):
                                linePoints.append(n2)
                                linePoints.append(s2)
                            else:
                                linePoints.append(s1)
                            linePoints.append(endPoint)
                            currentPoint = endPoint
                            break
                        else:
                            linePoints.append(n2)
                            if rectSource.collidepoint(s2):
                                linePoints.append(n1)
                                linePoints.append(s1)
                            else:
                                linePoints.append(s2)
                            linePoints.append(endPoint)
                            currentPoint=endPoint
                            break
                    elif n1Visible:
                        linePoints.append(n1)
                        if rectSource.collidepoint(s1):
                            linePoints.append(n2)
                            linePoints.append(s2)
                        else:
                            linePoints.append(s1)
                        linePoints.append(endPoint)
                        currentPoint = endPoint
                        break
                    else:
                        linePoints.append(n2)
                        if rectSource.collidepoint(s2):
                            linePoints.append(n1)
                            linePoints.append(s1)
                        else:
                            linePoints.append(s2)
                        linePoints.append(endPoint)
                        currentPoint = endPoint
                        break
        else:
            linePoints.append(endPoint)

        linePoints = self.OptimizeLinePoints(linePoints, [rectSource, rectSink], source, sink)
        self.CheckPathEnd(source, sink, linePoints)

        return linePoints

    def CheckPathEnd(self, source, sink, linePoints):
        startPoint = (0, 0)
        endPoint = (0, 0)
        marginPath = 15

        if source['position'] == 'left':
            startPoint = (source['RealX'] - marginPath, source['RealY'])

        if source['position'] == 'top':
            startPoint = (source['RealX'], source['RealY'] - marginPath)

        if source['position'] == 'right':
            startPoint = (source['RealX']  + marginPath, source['RealY'])

        if source['position'] == 'bottom':
            startPoint = (source['RealX']  , source['RealY']+ marginPath)

        if sink['position'] == 'left':
            endPoint = (sink['RealX'] - marginPath, sink['RealY'])

        if sink['position'] == 'top':
            endPoint = (sink['RealX'], sink['RealY'] - marginPath)

        if sink['position'] == 'right':
            endPoint = (sink['RealX']  + marginPath, sink['RealY'])

        if sink['position'] == 'bottom':
            endPoint = (sink['RealX']  , sink['RealY']+ marginPath)

        #linePoints.insert(0, startPoint)
        #linePoints.append(endPoint)
        linePoints.insert(0, (source['RealX'], source['RealY']))
        linePoints.append((sink['RealX'], sink['RealY']))

    def OptimizeLinePoints(self, linePoints, rectangles, sourceOrientation, sinkOrientation):
        points = []
        cut = 0

        for i in range(0, len(linePoints)):
            if i >= cut:
                for k in range(len(linePoints)-1, i, -1):
                    if self.IsPointVisible(linePoints[i], linePoints[k], rectangles):
                        cut = k
                        break
                points.append(linePoints[i])

        for j in range(0, len(points)-1):
            if points[j][0] != points[j+1][0] and points[j][1] != points[j+1][1]:
                if j==0:
                    orientationFrom = sourceOrientation['position']
                else:
                    orientationFrom = self.GetOrientation(points[j], points[j-1])

                if j == len(points)-2:
                    orientationTo = sinkOrientation['position']
                else:
                    orientationTo = self.GetOrientation(points[j+1], points[j+2])

                if (orientationFrom == 'left' or orientationFrom == 'right') and (orientationTo == 'left' or orientationTo == 'right'):
                    centerX = int(min(points[j][0], points[j+1][0]) + abs(points[j][0] - points[j + 1][0]) / 2)
                    points.insert(j+1, (centerX, points[j][1]))
                    points.insert(j+2, (centerX, points[j +2][1]))
                    if len(points) -1 > j +3:
                        points.pop(j + 3)
                    return points
                
                if (orientationFrom == 'top' or orientationFrom == 'bottom') and (orientationTo == 'top' or orientationTo == 'bottom'):
                    centerY = int(min(points[j][1], points[j+1][1]) + abs(points[j][1] - points[j + 1][1]) / 2)
                    points.insert(j+1, (points[j][0], centerY))
                    points.insert(j +2, (points[j+2][0], centerY))
                    if len(points) -1 > j+3:
                        points.pop(j+3)
                    return points

                if (orientationFrom == 'left' or orientationFrom == 'right') and (orientationTo == 'top' or orientationTo == 'bottom'):
                    points.insert(j +1, (points[j + 1][0], points[j][1]))

                if (orientationFrom == 'top' or orientationFrom == 'bottom') and (orientationTo == 'left' or orientationTo == 'right'):
                    points.insert(j+1, (points[j][0], points[j + 1][1]))

        return points

    def GetOrientation(self, p1, p2):
        if p1[0] == p2[0]:
            if p1[1] == p2[1]:
                return 'bottom'
            else:
                return 'top'
        elif p1[1] == p2[1]:
            if p1[0] == p2[0]:
                return 'right'
            else:
                return 'left'

    def GetOppositeCorners(self, connector, rect):
        if connector['position'] == 'left':
            return rect.topright, rect.bottomright

        if connector['position'] == 'top':
            return rect.bottomleft, rect.bottomright

        if connector['position'] == 'right':
            return rect.topleft, rect.bottomleft

        if connector['position'] == 'bottom':
            return rect.topleft, rect.topright

        return None



    def IsRectVisible(self, fromPoint, targetRect, rectangles):
        if self.IsPointVisible(fromPoint, targetRect.topleft, rectangles):
            return True

        if self.IsPointVisible(fromPoint, targetRect.topright, rectangles):
            return True

        if self.IsPointVisible(fromPoint, targetRect.bottomleft, rectangles):
            return True

        if self.IsPointVisible(fromPoint, targetRect.bottomright, rectangles):
            return True

    def GetNearestNeighborSource(self, source, endPoint, rectSource, rectSink):
        n1, n2 = self.GetNeighborCorners(source, rectSource)

        if rectSink.collidepoint(n1):
            return n2, False

        if rectSink.collidepoint(n2):
            return n1, True

        if self.Distance(n1, endPoint) <= self.Distance(n2, endPoint):
            return n1, True
        else:
            return n2, False



    def GetNearestVisibleNeighborSink(self, currentPoint, endPoint, sink, rectSource, rectSink):
        
        s1, s2 = self.GetNeighborCorners(sink, rectSink)
        flag1 = self.IsPointVisible(currentPoint, s1, [rectSource, rectSink])
        flag2 = self.IsPointVisible(currentPoint, s2, [rectSource, rectSink])        
        
        if flag1:
            if flag2:
                if rectSink.collidepoint(s1[0], s1[1]):
                    return s2
                if rectSink.collidepoint(s2[0], s2[1]):
                    return s1
                if self.Distance(s1, endPoint) <= self.Distance(s2, endPoint):
                    return s1
                else:
                    return s2
            else:
                return s1
        else:
            if flag2:
                return s2
            else:
                return (float('nan'), float('nan'))


    def Distance(self, p1, p2):
        return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5

    def GetNeighborCorners(self, connector, rect):
        if connector['position'] == 'left':
            return rect.topleft, rect.bottomleft
        if connector['position'] == 'top':
            return rect.topleft, rect.topright
        if connector['position'] == 'right':
            return rect.topright, rect.bottomright
        if connector['position'] == 'bottom':
            return rect.bottomleft, rect.bottomright   

        return None    

    def IsPointVisible(self, fromPoint, targetPoint, rectangles):
        for rect in rectangles:
            if self.RectangleIntersectsLine(rect, fromPoint, targetPoint):
                return False
        return True

    def RectangleIntersectsLine(self, rect, startPoint, endPoint):
        rect = rect.inflate(-1, -1)

        minX = min(startPoint[0], endPoint[0])
        minY = min(startPoint[1], endPoint[1])
        maxX = max(startPoint[0], endPoint[0])
        maxY = max(startPoint[1], endPoint[1])

        rect2 = pg.Rect(minX, minY, maxX - minX, maxY - minY)

        
        collinsion = rect.colliderect(rect2)
        return collinsion

    def GetOffsetPoint(self, connector, rect):
        if connector['position'] == 'left':
            return (rect.left, connector['RealY'])
        if connector['position'] == 'top':
            return (connector['RealX'], rect.top)
        if connector['position'] == 'right':
            return (rect.right, connector['RealY'])
        if connector['position'] == 'bottom':
            return (connector['RealX'], rect.bottom)

        return None

    def GetRectWithMargin(self, component, margin):
        rect = pg.Rect(component[4], component[5], component[6] - component[4], component[7] - component[5])

        return rect.inflate(margin, margin)

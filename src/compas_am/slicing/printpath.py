import compas

class PrintPath(object):
    def __init__(self, polygon):
        self.points = points
        self.is_closed = is_closed

    def get_lines_for_plotter(self, color = (255,0,0)):
        lines = []
        for i, pt in enumerate(self.points):
            if self.is_closed:
                line = {}
                line['start'] = pt
                line['end'] = self.points[(i+1)%(len(self.points) -1)]
                line['width'] = 1.0
                line['color'] = color
                lines.append(line)
            else: 
                if i<len(self.points) -1:
                    line = {}
                    line['start'] = pt
                    line['end'] = self.points[i+1]
                    line['width'] = 1.0
                    line['color'] = color
                    lines.append(line)
        return lines


##########################

class Contour(PrintPath):
    def __init__(self, points, is_closed):
        self.points = points
        self.is_closed = is_closed

class Support(PrintPath):
    def __init__(self):
        pass

class Infill(PrintPath):
    def __init__(self):
        pass



if __name__ == '__main__':
    pass
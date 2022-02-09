import math
from operator import attrgetter
import itertools

def define_triangles(outline):

    # calculate the distance between 2 points
    def distance(p1, p2):
        return math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2))

    # calcucate the smallest distance of other 2 sides of a triangle
    def sides(p1, p2, p3):
        s1 = distance(p1, p3)
        s2 = distance(p2, p3)
        return s1 + s2

    # create the class 'line' with two points
    class line:
        def __init__(self, p1, p2):
            self.p1 = p1
            self.p2 = p2

    # create the class 'triangle' with three points and the result of the function "sides'
    class triangle:
        def __init__(self, p1, p2, p3, sides):
            self.p1 = p1
            self.p2 = p2
            self.p3 = p3
            self.sides = sides

    # side of a triangle can be represented as a linear function
    def linear_functions(line):
        if line.p1[0] - line.p2[0] == 0:
            return 1
        elif line.p1[1] - line.p2[1] == 0:
            return 2
        else:
            a = (line.p1[1] - line.p2[1])/(line.p1[0] - line.p2[0])
            c = line.p1[1] - line.p1[0] * a
            return [a, c]

    # find out if 2 lines cross each other or not
    def check_crossing(line1, line2):
        ac1 = linear_functions(line1)
        ac2 = linear_functions(line2)
        if (ac1 == 1 and ac2 == 1) or (ac1 == 2 and ac2 == 2):
            return None
        elif ac1 == 1 and ac2 == 2:
            return [line1.p1[0], line2.p1[1]]
        elif ac1 == 2 and ac2 == 1:
            return [line2.p1[0], line1.p1[1]]
        elif ac1 == 1 and isinstance(ac2, list):
            x = line1.p1[0]
            y = ac2[0] * x + ac2[1]
            return [x, y]
        elif ac1 == 2 and isinstance(ac2, list):
            y = line1.p1[1]
            x = (y - ac2[1])/ac2[0]
            return [x, y]
        elif isinstance(ac1, list) and ac2 == 1:
            x = line2.p1[0]
            y = ac1[0] * x + ac1[1]
            return [x, y]
        elif isinstance(ac1, list) and ac2 == 2:
            y = line2.p1[1]
            x = (y - ac1[1])/ac1[0]
            return [x, y]
        elif isinstance(ac1, list) and isinstance(ac2, list):
            if ac1[0] - ac2[0] == 0:
                return None
            else:
                x = (ac2[1] - ac1[1])/(ac1[0] - ac2[0])
                y = ac1[0] * x + ac1[1]
            return [x, y]

    # check if a side of a triangle has been already used
    def check_line_in_outline(p1, p2, lines):
        if len(lines) == 0:
            return False
        else:
            for lin in lines:
                if (p1 == lin.p1 and p2 == lin.p2) or (p1 == lin.p2 and p2 == lin.p1):
                    return True
            return False

    # create a line between two middle points, this function is used in the next function
    def midpoint_line(p1, p2, point):
        index_p1 = outline.index(p1)
        index_point = outline.index(point)
        if index_p1 > index_point:
            midpoint1 = [(p2[0] + point[0]) / 2, (p2[1] + point[1]) / 2]
        else:
            midpoint1 = [(p1[0] + point[0]) / 2, (p1[1] + point[1]) / 2]
        midpoint2 = [(p1[0] + p2[0])/2, (p1[1] + p2[1])/2]
        return line(midpoint1, midpoint2)

    # find all points in the outline which can be crossed by a line between two middle points
    def check_point_in_outline(points, lines):
        points_in_outline = []
        for point in points:
            if point != None:
                for l1ne in lines:
                    if math.isclose(distance(l1ne.p1, l1ne.p2), distance(l1ne.p1, point) + distance(l1ne.p2, point), abs_tol=0.00001):
                        if point not in points_in_outline:
                            points_in_outline.append(point)
                        break
        return points_in_outline

    # count how many times a line between two middle points has crossed the outline
    # an even number means that a side of a triangle between two middle points is laying out of the outline
    def check_outside(midpoints, points_in_outline):
        count = 0
        for point in points_in_outline:
            if math.isclose(distance(midpoints.p1, point), distance(midpoints.p1, midpoints.p2) + distance(midpoints.p2, point), abs_tol=0.00001):
                count = count + 1
        if (count % 2) == 0:
            return True
        else:
            return False

    # it is executed when all lines in the outline have been used, create a new polyline inside of the outline to generate triangles inside of the outline
    def check_trianlges_inside(used_lines_inside, other_triangles):
        indexes = []

        for used_line_inside in used_lines_inside:
            indexes.append([outline.index(used_line_inside.p1), outline.index(used_line_inside.p2)])

        remove_dublicates = []

        for i in range(len(indexes) - 1):
            for j in range(len(indexes) - i - 1):
                if (indexes[i][0] == indexes[i + j + 1][0] and indexes[i][1] == indexes[i + j + 1][1]) or (
                        indexes[i][0] == indexes[i + j + 1][1] and indexes[i][1] == indexes[i + j + 1][0]):
                    remove_dublicates.append(i + j + 1)

        output = []

        for i in range(len(indexes)):
            if i not in remove_dublicates:
                output.append(indexes[i])

        combinations = list(itertools.combinations(output, other_triangles + 2))
        for combination in combinations:
            element_list = (list(itertools.chain.from_iterable(list(combination))))
            if len(list(dict.fromkeys(element_list))) == other_triangles + 2:
                break
        polygon = list(dict.fromkeys(element_list))
        polygon.sort()
        polygon_outline = []
        for point_index in polygon:
            polygon_outline.append(outline[point_index])
        polygon_outline.append(polygon_outline[0])
        return define_triangles(polygon_outline)

    # check if a side of a triangle crosses the outline
    def check_crossing_lines_outside(line, outside_lines):
        count = -2
        for outside_line in outside_lines:
            if check_crossing(line, outside_line) != None:
                crossing_point =  check_crossing(line, outside_line)
                if math.isclose(distance(line.p1, line.p2), distance(line.p1, crossing_point) + distance(line.p2, crossing_point), abs_tol=0.00001):
                    if math.isclose(distance(outside_line.p1, outside_line.p2), distance(outside_line.p1, crossing_point) + distance(outside_line.p2, crossing_point), abs_tol=0.00001):
                        count = count + 1
        if count > 2:
            return True
        else:
            return False

    # check if a side of a triangle crosses sides of the generated triangles
    def check_crossing_lines_inside(line, inside_lines):
        count = 0
        for inside_line in inside_lines:
            if check_crossing(line, inside_line) != None:
                if line.p1 != inside_line.p1 and line.p2 != inside_line.p2 and line.p2 != inside_line.p1 and line.p1 != inside_line.p2:
                    crossing_point =  check_crossing(line, inside_line)
                    if math.isclose(distance(line.p1, line.p2), distance(line.p1, crossing_point) + distance(line.p2, crossing_point), abs_tol=0.00001):
                        if math.isclose(distance(inside_line.p1, inside_line.p2), distance(inside_line.p1, crossing_point) + distance(inside_line.p2, crossing_point), abs_tol=0.00001):
                            count = count + 1
        if count == 0:
            return False
        else:
            True

    lines = []

    # create lines which represent the outline
    for i in range(len(outline) - 1):
        lines.append(line(outline[i], outline[i + 1]))

    temp_triangles = []
    used_lines = []
    used_lines_inside = []
    triangles = []
    used_points = []

    # check all possible triangles that can be generated, to avoid crossing and repeating the functions described above are used
    # each line of the outline is connected with the points of the outline
    for i in range(len(lines) - 2):
        for lin in lines:
            if check_line_in_outline(lin.p1, lin.p2, used_lines):
                continue
            else:
                for point in outline:
                    if lin.p1 != point and lin.p2 != point and point not in used_points:
                        crossing_points = []
                        for ln in lines:
                            crossing_points.append(check_crossing(midpoint_line(lin.p1, lin.p2, point), ln))
                            crossing_points_in_outline = check_point_in_outline(crossing_points, lines)
                        if not check_outside(midpoint_line(lin.p1, lin.p2, point), crossing_points_in_outline):
                            if check_crossing_lines_outside(line(lin.p1, point),lines) == False and (check_crossing_lines_inside(line(lin.p1, point),used_lines_inside)) == False:
                                if check_crossing_lines_outside(line(lin.p2, point),lines) == False and (check_crossing_lines_inside(line(lin.p2, point),used_lines_inside)) == False:
                                    temp_triangles.append(triangle(lin.p1, lin.p2, point, sides(lin.p1, lin.p2, point)))

        # that means that there is no more triangles with sides which are laying in the outline
        if len(temp_triangles) == 0:
            triangles_inside = check_trianlges_inside(used_lines_inside, other_triangles = len(lines) - 2 - i)
            for triangle_inside in triangles_inside:
                triangles.append(triangle_inside)
            # output of triangles
            return triangles
        else:
            # find a triangle with the shortest sides to keep the mesh being more precise
            min_triangle = min(temp_triangles, key=attrgetter('sides'))
            triangles.append(min_triangle)
            # all sides of a triangle have to be store to avoid repeating
            used_lines.append(line(min_triangle.p1, min_triangle.p2))
            if check_line_in_outline(min_triangle.p2, min_triangle.p3, lines):
                used_lines.append(line(min_triangle.p2, min_triangle.p3))
                used_points.append(min_triangle.p2)
            else:
                used_lines_inside.append(line(min_triangle.p2, min_triangle.p3))
            if check_line_in_outline(min_triangle.p1, min_triangle.p3, lines):
                used_lines.append(line(min_triangle.p1, min_triangle.p3))
                used_points.append(min_triangle.p1)
            else:
                used_lines_inside.append(line(min_triangle.p1, min_triangle.p3))
            temp_triangles = []
    # output of triangles
    return triangles




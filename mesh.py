import ifcopenshell
import time
import triangles

# outline of the object
outline = [[-3,-20, 0.2], [3,-20,0.2],[3,8,0],[10,0,0],[5,10,0], [33,10,1], [5,16,0], [3,18,0] ,[3,46,-0.2], [-3,46,-0.2], [-3,18,0], [-5,16,50], [-33,16,0], [-33,10,0],[-5,10,0], [-3,8,0],[-3,-20,0.2]]

# height of the object
height = 25

# create a ifc-file and add some information about creator, that is used by creating objects as an attribute
ifc = ifcopenshell.file(schema='IFC4')
organization = ifc.createIFCORGANIZATION(None, 'CS50', None, None, None)
person = ifc.createIFCPERSON(None, None, 'Kirill Kuklin', None, None, None, None, None)
person_organisation = ifc.createIFCPERSONANDORGANIZATION(person, organization, None)
application = ifc.createIFCAPPLICATION(organization, '0.6', 'IfcOpenShell', '')
timestamp = time.time()
owner_history = ifc.createIFCOWNERHISTORY(person_organisation, application, None, 'ADDED', None, None, None, int(timestamp))


# define project placement using a point for setting up the coordination axises which can be rotated by their relationship to each other
cartesian_point = ifc.createIFCCARTESIANPOINT((0.,0.,0.))
project_placement = ifc.createIFCAXIS2PLACEMENT3D(cartesian_point, None, None)

# put into the project a site, that is used to connect objects "mesh" with the site
context = ifc.createIFCGEOMETRICREPRESENTATIONCONTEXT(None, 'Model', 3,1.E-05, project_placement, None)
subcontext = ifc.createIFCGEOMETRICREPRESENTATIONSUBCONTEXT('Body', 'Model', None, None, None, None, context, None, 'MODEL_VIEW', None)

project = ifc.createIFCPROJECT(ifcopenshell.guid.new(), owner_history, None, 'Project', None, None, None, [context], None)
site_axis2placement = ifc.createIFCAXIS2PLACEMENT3D(cartesian_point, None, None)
site_local_placemnet = ifc.createIFCLOCALPLACEMENT(None, site_axis2placement)
site = ifc.createIfcSite(ifcopenshell.guid.new(), owner_history,'Site', None, None, site_local_placemnet, None, None, 'ELEMENT', None, None, None, None, None)

# create a structure for the project
container_project = ifc.createIFCRELAGGREGATES(ifcopenshell.guid.new(), owner_history, None, None, project, [site])

# set a placement for objects
mesh_axis2placement = ifc.createIFCAXIS2PLACEMENT3D(cartesian_point, None, None)
mesh_local_placement = ifc.createIFCLOCALPLACEMENT(site_local_placemnet, mesh_axis2placement)

# call a function called triangles which makes triangles from the given outline
triangles = triangles.define_triangles(outline)

points_triangles = []

# creating upper part of the object
for tr1angle in triangles:
    points_triangles.append([(float(tr1angle.p1[0]),float(tr1angle.p1[1]), float(tr1angle.p1[2])),
                         (float(tr1angle.p2[0]),float(tr1angle.p2[1]), float(tr1angle.p2[2])),
                         (float(tr1angle.p3[0]),float(tr1angle.p3[1]), float(tr1angle.p3[2]))])

# creating lower part of the object
for tr1angle in triangles:
    points_triangles.append([(float(tr1angle.p1[0]), float(tr1angle.p1[1]), float(tr1angle.p1[2]) - height),
                         (float(tr1angle.p2[0]),float(tr1angle.p2[1]), float(tr1angle.p2[2]) - height),
                         (float(tr1angle.p3[0]),float(tr1angle.p3[1]), float(tr1angle.p3[2]) - height)])

# creating sides of the object
for i in range(len(outline) - 1):
    points_triangles.append([(float(outline[i][0]),float(outline[i][1]), float(outline[i][2])),
                             (float(outline[i + 1][0]), float(outline[i + 1][1]), float(outline[i + 1][2])),
                             (float(outline[i][0]), float(outline[i][1]), float(outline[i][2]) - height)])
    points_triangles.append([(float(outline[i][0]),float(outline[i][1]), float(outline[i][2]) - height),
                             (float(outline[i + 1][0]), float(outline[i + 1][1]), float(outline[i + 1][2])),
                             (float(outline[i + 1][0]), float(outline[i + 1][1]), float(outline[i + 1][2]) - height)])

point_list = []

# write point of each triangle
for triangle_points in points_triangles:
        point_list.append([ifc.createIFCCARTESIANPOINT(triangle_points[0]),
                          ifc.createIFCCARTESIANPOINT(triangle_points[1]),
                          ifc.createIFCCARTESIANPOINT(triangle_points[2])])

# according to the IFC-Structure there is need to combine three points into a polyline
pls = []
for row in point_list:
    pls.append(ifc.createIFCPOLYLOOP(row))

# after the previous step a polyline has to be converted into a face
connected_faces = []
for pl in pls:
    connected_faces.append(ifc.createIFCFACE([ifc.createIFCFACEOUTERBOUND(pl, True)]))

# before the mesh gets created, all faces related to the mesh must be connected with each other
surface_model = ifc.createIFCFACEBASEDSURFACEMODEL([ifc.createIFCCONNECTEDFACESET(connected_faces)])

# generate a shape of the mesh
mesh_representation = ifc.createIfcShapeRepresentation(subcontext, 'Body', 'SurfaceModel', [surface_model])
mesh_shape = ifc.createIfcProductDefinitionShape(None, None, [mesh_representation])

# put the mesh as a object, the mesh can be modified as well (for instance change the colour)
mesh = ifc.createIfcBuildingElementProxy(ifcopenshell.guid.new(), owner_history,'No Dynamo', None, None, mesh_local_placement,mesh_shape, None, 'NOTDEFINED')
mesh_type = ifc.createIFCBUILDINGELEMENTPROXYTYPE(ifcopenshell.guid.new(), owner_history, 'No dynamo', None, None, None, None, None, None, 'NOTDEFINED')
ifc.createIFCRELDEFINESBYTYPE(ifcopenshell.guid.new(), owner_history, None, None, [mesh], mesh_type)

# generate a placeholder for the mesh in the structure of the ifc-file
container_mesh = ifc.createIfcRelContainedInSpatialStructure(ifcopenshell.guid.new(), owner_history, 'Mesh', None, [mesh], site)

# write the ifc file
ifc.write('mesh.ifc')


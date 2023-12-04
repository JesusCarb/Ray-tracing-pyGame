from config import *
import sphere
import camera
import plane


class Scene:
    """
        Holds pointers to all objects in the scene
    """


    def __init__(self):

        def add_plane(self, normal, tangent, bitangent, u_min, u_max, v_min, v_max, center, color, roughness):
            new_plane = plane.Plane(
                normal=normal,
                tangent=tangent,
                bitangent=bitangent,
                uMin=u_min,
                uMax=u_max,
                vMin=v_min,
                vMax=v_max,
                center=center,
                color=color,
                roughness=roughness,
            )
            self.planes.append(new_plane)

            def randomColor():
                color = [
                            np.random.uniform(low = 0.3, high = 1.0),
                            np.random.uniform(low = 0.3, high = 1.0),
                            np.random.uniform(low = 0.3, high = 1.0)
                        ]
                return color

        """
            Set up scene objects.
        """
        # list of spheres, 32 in this case, random positions, colors and attributes
        # all in front of cam
        self.spheres = [
            sphere.Sphere(
                center = [
                    np.random.uniform(low = 3.0, high = 10.0),
                    np.random.uniform(low = -5.0, high = 5.0),
                    np.random.uniform(low = -5.0, high = 5.0)
                ],
                radius = np.random.uniform(low = 0.1, high = 2.0),
                color = [
                    np.random.uniform(low = 0.3, high = 1.0),
                    np.random.uniform(low = 0.3, high = 1.0),
                    np.random.uniform(low = 0.3, high = 1.0)
                ],
                roughness = np.random.uniform(low = 0.1, high = 0.9)
            ) for i in range(10)

            # sphere.Sphere(
            #     center = [
            #         0,1,-3
            #     ],
            #     radius = 2.0,
            #     color = [
            #         .9,.9,.9
            #     ],
            #     roughness = .1
            # )
        ]


        self.planes = []
        

        planes = add_plane(self, [0, 0, 1], [1, 0, 0], [0, 1, 0], -11, 11, -11, 11, [0, 0, -10], [.8,.8,.8]  , .8)

        self.camera = camera.Camera(
            position = [-2, 0, 0]
        )
        
        
        #bottom bottom top
        # planes = add_plane(self, [0, 0, 1], [1, 0, 0], [0, 1, 0], -11, 11, -11, 11, [0, 0, -10], [1,1,1]  , .8)
        # planes = add_plane(self, [0, 0, -1], [1, 0, 0], [0, 1, 0], -11, 11, -11, 11, [0, 0, 10], [1,1,1]  , .8)
        
        # #back
        # planes = add_plane(self, [-1, 0, 0], [0, 1, 0], [0, 0, 1], -11, 11, -11, 11,[10, 0, 0], [1,1,1]   , .8)
        
        # # rightleft
        # planes = add_plane(self, [0, -1, 0], [1, 0, 0], [0, 0, 1], -11, 11, -11, 11, [0, 10, 0], [0,1,0] , .8)
        # planes = add_plane(self, [0, 1, 0], [1, 0, 0], [0, 0, -1], -11, 11, -11, 11, [0, -10, 0], [1,0,0] , .8)
        # self.camera = camera.Camera(
        #     position = [-10, 0, 0]
        # )

        self.outDated = True
        # self.planes =  [
        #     # plane.Plane(
        #     #     normal = [0, 0, 1],
        #     #     tangent = [1, 0, 0],
        #     #     bitangent = [0, 1, 0],
        #     #     uMin = -10,
        #     #     uMax = 10,
        #     #     vMin = -10,
        #     #     vMax = 10,
        #     #     center = [0, 0, -7],
        #     #     # color = randomColor(),
        #     #     color = [0,0,0] ,
        #     #     roughness = np.random.uniform(low = 0.1, high = 0.9),
        #     # )
        # ]
                # position of camera

# # self, normal, tangent, bitangent, u_min, u_max, v_min, v_max, center, color, roughness
        # self.planes.add_plane([0, 0, 1], [1, 0, 0], [0, 1, 0], -10, 10, -10, 10, [0, 0, 7], [0,1,0] , .5)



    





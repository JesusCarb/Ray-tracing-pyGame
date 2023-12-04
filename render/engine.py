from config import *
import screen_quad
import material
import megatexture

class Engine:
    """
        Responsible for drawing scenes
    """

    def __init__(self, width: int, height: int):
        """
            Initialize a flat raytracing context
            
                Parameters:
                    width (int): width of screen
                    height (int): height of screen
        """
        self.screenWidth = width
        self.screenHeight = height

        self.makeAssets()
    
    def makeAssets(self) -> None:
        """ Make all the stuff. """

        self.screenQuad = screen_quad.ScreenQuad()

        self.colorBuffer = material.Material(self.screenWidth, self.screenHeight)
        
        self.createResourceMemory()
        self.createNoiseTexture()
        self.createMegaTexture()
        self.shader = self.createShader("shaders/frameBufferVertex.glsl",
                                        "shaders/frameBufferFragment.glsl")
        
        self.rayTracerShader = self.createComputeShader("shaders/rayTracer.glsl")
     
    def createResourceMemory(self):
        # packing data into a 1024 image
        # center, radius, color
        # (x, y, z, radius), (r, g, b, roughness) (----) (----) (----)
        # (cx cy cz tx) (ty tz bx by) ( bz nx ny nz) (umin umax vmin vmax) (material)
        objectData = []

        for object in range(1024):
            for attribute in range(20):
                objectData.append(0.0)
        self.objectData = np.array(objectData, dtype = np.float32)

        # initialize all at once
        # self.objectData = np.zeros(8 * 1024, dtype = np.float32)

        self.objectDataTexture = glGenTextures(1)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.objectDataTexture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, 5, 1024, 0, GL_RGBA, GL_FLOAT, bytes(self.objectData))
    
    def createNoiseTexture(self):
        #generate four screens worth of noise
        # packing data into a 1024 image
        # center, radius, color
        # (x, y, z, radius), (r, g, b, _)
        noise = []

        #random noise (x y z 0)
        for i in range(self.screenHeight):
            for attribute in range(4 * self.screenWidth):
                radius = np.random.uniform(low = 0.0, high = 0.99)
                theta = np.random.uniform(low = 0.0, high = 2 * np.pi)
                phi = np.random.uniform(low = 0.0, high = np.pi)
                noise.append(radius * np.cos(theta) * np.cos(phi))
                noise.append(radius * np.sin(theta) * np.cos(phi))
                noise.append(radius * np.cos(phi))
                noise.append(0.0)

        self.noiseData = np.array(noise, dtype = np.float32)

        # initialize all at once
        # self.objectData = np.zeros(8 * 1024, dtype = np.float32)

        self.noiseTexture = glGenTextures(1)
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, self.noiseTexture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F,
                    4 * self.screenWidth, self.screenHeight,
                    0, GL_RGBA, GL_FLOAT, bytes(self.noiseData))
    def createMegaTexture(self) -> None:
        """
            Load all the textures.
        """

        filenames = [
            "AlienArchitecture", "AlternatingColumnsConcreteTile", "BiomechanicalPlumbing", 
            "CarvedStoneFloorCheckered", "ChemicalStrippedConcrete", "ClayBrick",
            "CrumblingBrickWall", "DiamondSquareFlourishTiles", "EgyptianHieroglyphMetal"
        ]

        self.megaTexture = megatexture.MegaTexture(filenames)

    def createShader(self, vertexFilepath, fragmentFilepath) -> int:
        """
            Read source code, compile and link shaders.
            Returns the compiled and linked program.
        """

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader
    
    def createComputeShader(self, filepath) -> int:
        """
            Read source code, compile and link shaders.
            Returns the compiled and linked program.
        """

        with open(filepath,'r') as f:
            compute_src = f.readlines()
        
        shader = compileProgram(compileShader(compute_src, GL_COMPUTE_SHADER))
        
        return shader

    # passes all the information to raytrace/compute shader
    def recordSphere(self, i, _sphere): 

        # sphere formating
        # [ x1, y1, z1, .... x2, y2, z2]

        # filliing in from 0-6
        self.objectData[20 * i] = _sphere.center[0]
        self.objectData[20 * i + 1] = _sphere.center[1]
        self.objectData[20 * i + 2] = _sphere.center[2]

        self.objectData[20 * i + 3] = _sphere.radius

        self.objectData[20 * i + 4] = _sphere.color[0]
        self.objectData[20 * i + 5] = _sphere.color[1]
        self.objectData[20 * i + 6] = _sphere.color[2]
        
        self.objectData[20 * i + 7] = _sphere.roughness


    def recordPlane(self, i, _plane):
    
        self.objectData[20 * i]     = _plane.center[0]
        self.objectData[20 * i + 1] = _plane.center[1]
        self.objectData[20 * i + 2] = _plane.center[2]

        self.objectData[20 * i + 3] = _plane.tangent[0]
        self.objectData[20 * i + 4] = _plane.tangent[1]
        self.objectData[20 * i + 5] = _plane.tangent[2]

        self.objectData[20 * i + 6] = _plane.bitangent[0]
        self.objectData[20 * i + 7] = _plane.bitangent[1]
        self.objectData[20 * i + 8] = _plane.bitangent[2]

        self.objectData[20 * i + 9] = _plane.normal[0]
        self.objectData[20 * i + 10] = _plane.normal[1]
        self.objectData[20 * i + 11] = _plane.normal[2]


        self.objectData[20 * i + 12] = _plane.uMin
        self.objectData[20 * i + 13] = _plane.uMax
        self.objectData[20 * i + 14] = _plane.vMin
        self.objectData[20 * i + 15] = _plane.vMax

        # self.objectData[20 * i + 16] = _plane.color[0]
        # self.objectData[20 * i + 17] = _plane.color[1]
        # self.objectData[20 * i + 18] = _plane.color[2]

        # self.objectData[20 * i + 19] = _plane.roughness

        self.objectData[20 * i + 16] = _plane.material_index

    def updateScene(self, _scene):

        _scene.outDated = False
        glUseProgram(self.rayTracerShader)

        glUniform1f(glGetUniformLocation(self.rayTracerShader, "sphereCount"), len(_scene.spheres))

        # looping through spheres and passing in sphere info
        # passes sphers as uniforms
        for i,_sphere in enumerate(_scene.spheres):
            # updates buffer
            self.recordSphere(i, _sphere)
            
            # glUniform3fv(glGetUniformLocation(self.rayTracerShader, f"spheres[{i}].center"), 1, _sphere.center)
            # glUniform1f(glGetUniformLocation(self.rayTracerShader, f"spheres[{i}].radius"), _sphere.radius)
            # glUniform3fv(glGetUniformLocation(self.rayTracerShader, f"spheres[{i}].color"), 1, _sphere.color)
        glUniform1f(glGetUniformLocation(self.rayTracerShader, "planeCount"), len(_scene.planes))
        
        for i,_plane in enumerate(_scene.planes):
        # updates buffer
             self.recordPlane(i + len(_scene.spheres), _plane)
        # updates texture that we're using to pass data/ for img not in use
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.objectDataTexture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, 5, 1024, 0, GL_RGBA, GL_FLOAT, bytes(self.objectData))

    def prepareScene(self, _scene):

        glUseProgram(self.rayTracerShader)
        
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.position"), 1, _scene.camera.position)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.forwards"), 1, _scene.camera.forwards)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.right"), 1, _scene.camera.right)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.up"), 1, _scene.camera.up)

        if _scene.outDated:
            self.updateScene(_scene)

        glActiveTexture(GL_TEXTURE1)
        glBindImageTexture(1, self.objectDataTexture, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)
        glActiveTexture(GL_TEXTURE2)
        glBindImageTexture(2, self.noiseTexture, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)
        glActiveTexture(GL_TEXTURE3)
        glBindImageTexture(3, self.megaTexture.texture, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)        # glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.sphereDataBuffer)
        # glBufferSubData(GL_SHADER_STORAGE_BUFFER ,0, 8 * 4 * len(_scene.spheres), self.sphereData)
        # glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, self.sphereDataBuffer)
    
    def renderScene(self, _scene) -> None:
        """
            Draw all objects in the scene
        """
        # using the ray tracer to calculate color of each picture of screen
        glUseProgram(self.rayTracerShader)
       
        self.prepareScene(_scene)
        # see material file
        self.colorBuffer.writeTo()
        
        # sets gpu to work as syncronously as possible to render 2d image on screen
        glDispatchCompute(int(self.screenWidth/8), int(self.screenHeight/8), 1)
        # glDispatchCompute(int(self.screenWidth/8), int(self.screenHeight/8), 1)
  
        # make sure writing to image has finished before read
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)
        # glBindImageTexture(0,0,0,GL_FALSE,0, GL_WRITE_ONLY, GL_RGBA32F)

        self.drawScreen()

    def drawScreen(self):
        #switches to regular shader, 
        glUseProgram(self.shader)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        
        # glActiveTexture(GL_TEXTURE0)
        # glBindTexture(GL_TEXTURE_2D, self.colorBuffer)
        # glBindTexture(GL_TEXTURE_2D, self.megaTexture.texture)
        #under material

        self.colorBuffer.readFrom()
        
        #under mesh
        self.screenQuad.draw()
        pg.display.flip()
    
    def destroy(self):
        """
            Free any allocated memory
        """
        glDeleteProgram(self.rayTracerShader)
        self.screenQuad.destroy()
        self.colorBuffer.destroy()
        glDeleteProgram(self.shader)
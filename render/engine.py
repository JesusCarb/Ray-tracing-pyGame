from config import *
import screen_quad
import material

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

        self.shader = self.createShader("shaders/frameBufferVertex.glsl",
                                        "shaders/frameBufferFragment.glsl")
        
        self.rayTracerShader = self.createComputeShader("shaders/rayTracer.glsl")
    
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

    def renderScene(self) -> None:
        """
            Draw all objects in the scene
        """
        # using the ray tracer to calculate color of each picture of screen
        glUseProgram(self.rayTracerShader)
       
        # see material file
        self.colorBuffer.writeTo()
        
        # sets gpu to work as syncronously as possible to render 2d image on screen
        glDispatchCompute(int(self.screenWidth), int(self.screenHeight), 1)
        # glDispatchCompute(int(self.screenWidth/8), int(self.screenHeight/8), 1)
  
        # make sure writing to image has finished before read
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

        self.drawScreen()

    def drawScreen(self):
        #switches to regular shader, 
        glUseProgram(self.shader)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

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
from config import *

class MegaTexture:

    def __init__(self, filenames):

        texture_size = 1024
        texture_count = len(filenames)
        width = 5 * texture_size
        height = texture_count * texture_size
        textureData = pg.Surface((width, height)).convert()

        for i, filename in enumerate(filenames):

            #albedo
            image = pg.image.load(f"../textures\{filename}\{filename}_albedo.png").convert()
            textureData.blit(image, (0, (texture_count -i - 1) * texture_size))

            #emissive
            image = pg.image.load(f"../textures\{filename}\{filename}_emissive.png").convert()
            textureData.blit(image, (texture_size, (texture_count -i - 1) * texture_size))
            #glossmap
            image = pg.image.load(f"../textures\{filename}\{filename}_glossiness.png").convert()
            textureData.blit(image, ( 2 * texture_size, (texture_count -i - 1) * texture_size))
            #normal
            image = pg.image.load(f"../textures\{filename}\{filename}_normal.png").convert()
            textureData.blit(image, ( 3 * texture_size, (texture_count -i - 1) * texture_size))
            #specular
            image = pg.image.load(f"../textures\{filename}\{filename}_specular.png").convert()
            textureData.blit(image, ( 4 * texture_size, (texture_count -i - 1) * texture_size))
            pass
            
        image_data = pg.image.tostring(textureData, "RGBA")


        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def destroy(self):
        glDeleteTextures(1, self.texture)
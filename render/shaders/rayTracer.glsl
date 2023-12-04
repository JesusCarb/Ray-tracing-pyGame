#version 430

struct Sphere {

    vec3 center;
    float radius;
    vec3 color;
    float roughness;

};

struct Camera {
    vec3 position;
    vec3 forwards;
    vec3 right;
    vec3 up;
};

struct Ray {
    vec3 origin;
    vec3 direction;
};

struct Plane {
    vec3 center;
    vec3 tangent;
    vec3 bitangent;
    vec3 normal;
    float uMin;
    float uMax;
    float vMin;
    float vMax;

    vec3 color;
    float roughness;

    float material;
};


struct RenderState{

    // tracks how far 
    float t;
    // color of the hit
    vec3 color;
    // if hit
    // vec3 emissive;
    vec3 position;
    vec3 normal;
    bool hit;

    float roughness;
    // float specular;
};

struct Material {
    vec3 albedo;
    vec3 emissive;
    float gloss;
    vec3 normal;
    vec3 specular;
};
// input/output
layout(local_size_x = 8, local_size_y = 8) in;
// layout(local_size_x = 1, local_size_y = 1) in;
layout(rgba32f, binding = 0) uniform image2D img_output;

// Scene Data
uniform Camera viewer;
// uniform Sphere spheres[32];
layout(rgba32f, binding = 1) readonly uniform image2D objects;
layout(rgba32f, binding = 2) readonly uniform image2D noise;
layout(rgba32f, binding = 3) readonly uniform image2D megaTexture;


uniform float sphereCount;
uniform float planeCount;
// layout(std430, binding = 1) readonly buffer sceneData
// {
//     Sphere[] spheres;
// };


RenderState trace(Ray ray);
// tracks which info we get from ray hitting something
RenderState hit(Ray ray, Sphere sphere, float tMin, float tMax, RenderState renderState);
RenderState hit(Ray ray, Plane plane, float tMin, float tMax, RenderState renderState);

Material sample_material(float index, float u, float v);

Sphere unpackSphere(int index);

Plane unpackPlane(int index);
void main() {

    // GlobalInvocationID, gives integer vector of the pixels of the camera
    ivec2 pixel_coords = ivec2(gl_GlobalInvocationID.xy);

    // imageSize(returns size of screen as ivec2) as length/width
    ivec2 screen_size = imageSize(img_output);

    vec3 finalColor = vec3(0.0);
    // sampling for aa
    for (int i = 0; i < 4; i++)
    {
        vec2 screenDeflection = imageLoad(
            noise,
            ivec2(pixel_coords.x + i * screen_size.x, pixel_coords.y)
        ).xy;

        // 0*2 -screensize/ screensize = -1
        // 200 * 2 = 400 - (800) / 800 = -.5
        // gets point offset on the quad from either left, right, up, down of the camera
        // and normalizes it from 0 - 1
        // we then use this to calculate the direction of rays, camera and this point give us ray
        // normalize based on x cause it's the larger dimention
        float horizontalCoefficient = (float(pixel_coords.x) + screenDeflection.x);
        horizontalCoefficient = ((float(pixel_coords.x) * 2 - screen_size.x) / screen_size.x);
            
        float verticalCoefficient = (float(pixel_coords.y) + screenDeflection.y);
        verticalCoefficient = ((float(pixel_coords.y) * 2 - screen_size.y) / screen_size.x);

        // define camera sphere and rays

        Ray ray;
        ray.origin = viewer.position;
        ray.direction = viewer.forwards + horizontalCoefficient * viewer.right + verticalCoefficient * viewer.up;

        // ray tracer writes color on buffer
        vec3 pixel = vec3(1.0);
        for (int bounce = 0; bounce < 100; bounce++)
        {
            RenderState renderState = trace(ray);
            // if dind't hit anything dont reflect
            if(!renderState.hit)
            {
                break;
            }
            // unpack color
            // pixel = pixel * renderState.color + renderState.emissive;
            pixel = pixel * renderState.color;

            // set up ray for next trace
            ray.origin = renderState.position;
            vec3 variation = imageLoad(
                noise,
                ivec2(pixel_coords.x + bounce * screen_size.x, pixel_coords.y)
            ).xyz;

            ray.direction = reflect(ray.direction, renderState.normal);
            // ray.direction = normalize(ray.direction + renderState.roughness * variation);
            // ray.direction = normalize(ray.direction + renderState.roughness);
            ray.direction = normalize(ray.direction);
            
        }
        finalColor = finalColor + .5 * pixel;

    }

    // sends it to texture, and regular shader draws buffer on screen
    imageStore(img_output, pixel_coords, vec4(finalColor,1.0));
}

RenderState trace(Ray ray)
{

    // init vars
    float nearestHit = 999999999;
    RenderState renderState;
    renderState.hit = false;
    renderState.color = vec3(1.0);

    for(int i = 0; i < sphereCount; i++)
    {
        RenderState newRenderState = hit(ray, unpackSphere(i), 0.001, nearestHit, renderState);

        if (newRenderState.hit)
        {
            nearestHit = newRenderState.t;
            renderState = newRenderState;
        }
    }

    for(int i = int(sphereCount); i < (sphereCount) + (planeCount); i++)
    {
        RenderState newRenderState = hit(ray, unpackPlane(i), 0.001, nearestHit, renderState);

        if (newRenderState.hit)
        {
            nearestHit = newRenderState.t;
            renderState = newRenderState;
        }
    }

    return renderState;
}

RenderState hit(Ray ray, Sphere sphere, float tMin, float tMax, RenderState renderState)
{
    vec3 co = ray.origin - sphere.center;
    float a = dot(ray.direction, ray.direction);
    float b = 2 * dot(ray.direction, co);
    float c = dot(co, co) - sphere.radius * sphere.radius;
    float discriminant = b * b - ( 4 * a * c);

    // checks for negative discriminant
    if (discriminant > 0.0)
    {
        float t = (-b - sqrt(discriminant)) / ( 2 * a);

        if( t> tMin && t < tMax)
        {
            renderState.position = ray.origin + t * ray.direction;
            // points from center of sphere towards position
            renderState.normal = normalize(renderState.position - sphere.center);
            renderState.t = t;
            renderState.color = sphere.color;
            renderState.roughness = sphere.roughness;
            // renderState.emissive = vec3(0);
            renderState.hit = true;

            return renderState;
        }
    }
    renderState.hit = false;
    return renderState;
}

RenderState hit(Ray ray, Plane plane, float tMin, float tMax, RenderState renderState)
{
    float denominator = dot(plane.normal, ray.direction);

    if(denominator < 0.000001)
    {
        float t = dot(plane.center - ray.origin, plane.normal) / denominator;

        if( t > tMin && t < tMax) {
            vec3 testPoint = ray.origin + t * ray.direction;
            vec3 testDirection = testPoint - plane.center;

            float u = dot(testDirection, plane.tangent);
            float v = dot(testDirection, plane.bitangent);

            if(u > plane.uMin && u < plane.uMax && v > plane.vMin && v < plane.vMax)
            {

                u = (u - plane.uMin) / (plane.uMax - plane.uMin);
                v = (v - plane.vMin)/ (plane.vMax - plane.vMin);

                vec3 alb = vec3(.1,.1,.1);
                ivec2 pixel_coords = ivec2(gl_GlobalInvocationID.xy);

                // float lambertianReflectance = max(0, dot(normalize(plane.normal), normalize(ray.direction)));
                // Material material = sample_material(plane.material, u, v);
                // vec3 diffuseColor = 0.5 + lambertianReflectance  * vec3(.5,.5,.5) + 1.0;

                vec3 dir = renderState.normal;
                vec3 finalColor = 0.7 * plane.color;
            
                renderState.position = testPoint;
                // points from center of sphere towards position
                renderState.normal = plane.normal;
                renderState.t = t;
                renderState.color = finalColor;
                // renderState.color = material.albedo;
                // renderState.emissive = material.emissive;
                // renderState.roughness = max(0.0, 1.0 - material.gloss);
                mat3 TBN = mat3(plane.tangent, plane.bitangent, plane.normal);
                // renderState.normal = TBN * material.normal;

                renderState.hit = true;
                renderState.roughness = plane.roughness;

                return renderState;
            }
        }
    }
    renderState.hit = false;
    return renderState;

}
// for image buffer
Sphere unpackSphere(int index)
{
    Sphere sphere;
    // gets position
    vec4 attributeChunk = imageLoad(objects, ivec2(0, index));
    sphere.center = attributeChunk.xyz;
    sphere.radius = attributeChunk.w;
    // gets color
    attributeChunk = imageLoad(objects, ivec2(1, index));
    sphere.color = attributeChunk.xyz;
    sphere.roughness = attributeChunk.w;


    return sphere;
}

Plane unpackPlane(int index)
{    // gets position

    // plane (cx cy cz tx ) (ty tz bx by ) (bz nx ny nz) (umin umax vmini vmax) (r g b _)
    Plane plane;
    vec4 attributeChunk = imageLoad(objects, ivec2(0, index));
    plane.center = attributeChunk.xyz;
    plane.tangent.x = attributeChunk.w;
    // gets color
    attributeChunk = imageLoad(objects, ivec2(1, index));
    plane.tangent.yz = attributeChunk.xy;
    plane.bitangent.xy = attributeChunk.zw;

    attributeChunk = imageLoad(objects, ivec2(2, index));
    plane.bitangent.z = attributeChunk.x;
    plane.normal = attributeChunk.yzw;

    attributeChunk = imageLoad(objects, ivec2(3, index));
    plane.uMin = attributeChunk.x;
    plane.uMax = attributeChunk.y;
    plane.vMin = attributeChunk.z;
    plane.vMax = attributeChunk.w;

    attributeChunk = imageLoad(objects, ivec2(4, index));
    // plane.material = attributeChunk.x;
    plane.color = attributeChunk.xyz;
    plane.roughness = attributeChunk.w;
    return plane;
}

Material sample_material(float index, float u, float v)
{
    Material material;

    // getting data from mega texture, split into 1024 cause compute shader needs to be done in ints
    material.albedo = imageLoad(megaTexture, ivec2(floor(1024 * u), floor(1024 * (v + index)))).rgb;
    // material.emissive = imageLoad(megaTexture, ivec2(floor(1024 * (u + 1)), floor(1024 * (v + index)))).rgb;
    material.gloss = imageLoad(megaTexture, ivec2(floor(1024*(u + 2)), floor(1024 * (v + index)))).r;
    material.normal = imageLoad(megaTexture, ivec2(floor(1024*(u + 3)), floor(1024 * (v + index)))).rgb;
    material.normal = 2.0 * material.normal - vec3(1.0);
    material.specular = imageLoad(megaTexture, ivec2(floor(1024*(u + 4)), floor(1024 * (v + index)))).rgb;

    return material;
}




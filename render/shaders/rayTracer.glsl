#version 430

struct Sphere {

    vec3 center;
    float radius;
    vec3 color;
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

struct RenderState{

    // tracks how far 
    float t;

    // color of the hit
    vec3 color;

    // if hit
    bool hit;
};

// input/output
layout(local_size_x = 8, local_size_y = 8) in;
// layout(local_size_x = 1, local_size_y = 1) in;
layout(rgba32f, binding = 0) uniform image2D img_output;

// Scene Data
uniform Camera viewer;
//
// uniform Sphere spheres[32];
layout(rgba32f, binding = 1) readonly uniform image2D spheres;

// layout(std430, binding = 1) readonly buffer sceneData
// {
//     Sphere[] spheres;
// };

uniform float sphereCount;

vec3 rayColor(Ray ray);
// tracks which info we get from ray hitting something
RenderState hit(Ray ray, Sphere sphere, float tMin, float tMax, RenderState renderState);
Sphere unpackSphere(int index);

void main() {

    // GlobalInvocationID, gives integer vector of the pixels of the camera
    ivec2 pixel_coords = ivec2(gl_GlobalInvocationID.xy);

    // imageSize(returns size of screen as ivec2) as length/width
    ivec2 screen_size = imageSize(img_output);

    // 0*2 -screensize/ screensize = -1
    // 200 * 2 = 400 - (800) / 800 = -.5
    // gets point offset on the quad from either left, right, up, down of the camera
    // and normalizes it from 0 - 1
    // we then use this to calculate the direction of rays, camera and this point give us ray
    // normalize based on x cause it's the larger dimention
    float horizontalCoefficient = ((float(pixel_coords.x) * 2 - screen_size.x) / screen_size.x);
    float verticalCoefficient = ((float(pixel_coords.y) * 2 - screen_size.y) / screen_size.x);

    // define camera sphere and rays

    Ray ray;
    ray.origin = viewer.position;
    ray.direction = viewer.forwards + horizontalCoefficient * viewer.right + verticalCoefficient * viewer.up;

    // ray tracer writes color on buffer
    vec3 pixel = rayColor(ray);
    
    // sends it to texture, and regular shader draws buffer on screen
    imageStore(img_output, pixel_coords, vec4(pixel,1.0));
}

vec3 rayColor(Ray ray)
{
    vec3 color = vec3(0.0);

    // init vars
    float nearestHit = 999999999;
    bool hitSomething = false;
    RenderState renderState;

    for(int i = 0; i < sphereCount; i++)
    {
        renderState = hit(ray, unpackSphere(i), 0.001, nearestHit, renderState);

        if (renderState.hit)
        {
            nearestHit = renderState.t;
            hitSomething = true;
        }
    }

    if (hitSomething)
    {
        color = renderState.color;
    }

    return color;
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
            renderState.t = t;
            renderState.color = sphere.color;
            renderState.hit = true;
            return renderState;
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
    vec4 attributeChunk = imageLoad(spheres, ivec2(0, index));
    sphere.center = attributeChunk.xyz;
    sphere.radius = attributeChunk.w;
    // gets color
    attributeChunk = imageLoad(spheres, ivec2(1, index));
    sphere.color = attributeChunk.xyz;

    return sphere;
}
#version 430

// input/output
// layout(local_size_x = 8, local_size_y = 8) in;
layout(local_size_x = 1, local_size_y = 1) in;

layout(rgba32f, binding = 0) uniform image2D img_output;

struct Sphere {

    vec3 center;
    float radius;
    vec3 color;
};

struct Camera{
    vec3 position;
    vec3 forward;
    vec3 right;
    vec3 up;

};

struct Ray {
    vec3 origin;
    vec3 direction;
};


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

    // ray tracer writes color on buffer
    vec3 pixel = vec3(0.0, 0.0, 0.0);
    
    // define camera sphere and rays
    Camera camera; 
    camera.position = vec3(0.0);
    camera.forward = vec3(1.0, 0.0, 0.0);
    camera.right = vec3(0.0, 1.0, 0.0);
    camera.up = vec3(0.0, 0.0, 1.0);

    Sphere sphere;
    sphere.center = vec3(3.0, 0.0, 0.0);
    sphere.radius = 1.0;
    sphere.color = vec3(1.0, 0.3, 0.7);

    Ray ray;
    ray.origin = camera.position;
    ray.direction = camera.forward + horizontalCoefficient * camera.right + verticalCoefficient * camera.up;

    // begin tracing  // see ray calculation formula
    float a = dot(ray.direction, ray.direction);
    float b = 2.0 * dot(ray.direction, ray.origin - sphere.center);
    float c = dot(ray.origin - sphere.center, ray.origin - sphere.center) - sphere.radius * sphere.radius;
    float discriminant = (b * b) - (4.0 * a * c);

    if(discriminant > 0)
    // ray hit sphere
    {
        pixel += sphere.color;
    }

    // sends it to texture, and regular shader draws buffer on screen
    imageStore(img_output, pixel_coords, vec4(pixel,1.0));
}
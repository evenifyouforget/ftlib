shader_type canvas_item;

vec4 premult_mix(vec4 color1, vec4 color2, float t) {
    vec3 premul1 = color1.rgb * color1.a;
    vec3 premul2 = color2.rgb * color2.a;

    vec3 rgb = mix(premul1, premul2, t);
    float a = mix(color1.a, color2.a, t);

    rgb = (a > 0.0) ? rgb / a : vec3(0.0);

    return vec4(rgb, a);
}

//from https://www.shadertoy.com/view/Nlc3zf
float sdRoundedRect(vec2 position, vec2 halfSize, float cornerRadius) {
    position = abs(position) - halfSize + cornerRadius;
    return length(max(position, 0.0)) + min(max(position.x, position.y), 0.0) - cornerRadius;
}

float sdCirc(vec2 p, vec2 c, float r) {
    return length(p - c) - r;
}

//from https://iquilezles.org/articles/distfunctions2d/
float sdTriangle( in vec2 p, in vec2 p0, in vec2 p1, in vec2 p2 ) {
    vec2 e0 = p1-p0, e1 = p2-p1, e2 = p0-p2;
    vec2 v0 = p -p0, v1 = p -p1, v2 = p -p2;
    vec2 pq0 = v0 - e0*clamp( dot(v0,e0)/dot(e0,e0), 0.0, 1.0 );
    vec2 pq1 = v1 - e1*clamp( dot(v1,e1)/dot(e1,e1), 0.0, 1.0 );
    vec2 pq2 = v2 - e2*clamp( dot(v2,e2)/dot(e2,e2), 0.0, 1.0 );
    float s = sign( e0.x*e2.y - e0.y*e2.x );
    vec2 d = min(min(vec2(dot(pq0,pq0), s*(v0.x*e0.y-v0.y*e0.x)),
                     vec2(dot(pq1,pq1), s*(v1.x*e1.y-v1.y*e1.x))),
                     vec2(dot(pq2,pq2), s*(v2.x*e2.y-v2.y*e2.x)));
    return -sqrt(d.x)*sign(d.y);
}

//inexact! works for my purposes tho
float sdPoweredDecal(vec2 p) {
    float d1 = sdCirc(p, vec2(0.5, 0.5), 0.35297619047);
    float d2 = sdCirc(p, vec2(0.27344, 0.53), 0.125);
    float d3 = sdCirc(p, vec2(0.575, 0.575), 0.18035714285);
    float d4 = sdTriangle(p, vec2(0.61875, 0.63125), vec2(0.825, 0.83125), vec2(0.6, 0.84375));
    float d5 = sdTriangle(p, vec2(0.63125, 0.55), vec2(0.53125, 1.59375), vec2(-1., 0.55));
    return min(max(min(max(d1, -d5), d2), -d3), d4);
}

//inexact! works for my purposes tho
float sdUnpoweredDecalHalf(vec2 p) {
    float d1 = sdCirc(p, vec2(0.5, 0.5), 0.35297619047);
    float d2 = sdCirc(p, vec2(0.4227, 0.575030012), 0.276);
    float d3 = distance(p, vec2(0.64945, 0.273)) + distance(p, vec2(0.795, 0.455)) - 0.29439;
    float d4 = sdTriangle(p, vec2(0., 0.63), vec2(1., 0.29), vec2(1., 2.));
    return min(max(max(d1, -d2), -d4), d3);
}

//inexact! works for my purposes tho
float sdUnpoweredDecal(vec2 p) {
    return min(sdUnpoweredDecalHalf(p), sdUnpoweredDecalHalf(vec2(1.) - p));
}

varying flat int id;
void vertex() {
    id = INSTANCE_ID;
}

const uint SDF_CW = 1u;
const uint SDF_CCW = 2u;
const uint SDF_UPW = 3u;

instance uniform float aaWidth;
instance uniform int layerID;

uniform sampler2D data;
uniform ivec2 dataLayerSize;

void fragment() {
    vec4 packed = texelFetch(data, ivec2(id % dataLayerSize.x + layerID * dataLayerSize.x, id / dataLayerSize.y), 0);

    // Step 1: Retrieve the raw 32-bit integers
    uint int1 = floatBitsToUint(packed.r);
    uint int2 = floatBitsToUint(packed.g);
    uint int3 = floatBitsToUint(packed.b);
    uint int4 = floatBitsToUint(packed.a);

    // Step 2: Rebuild 40-bit color from int1 and int2
    uint color_bits = (int1 << 8u) | (int2 >> 24u);

    uint r10 = (int1 >> 22u) & 0x3FFu;
    uint g10 = (int1 >> 12u) & 0x3FFu;
    uint b10 = (int1 >> 2u) & 0x3FFu;
    uint a10 = ((int1 << 8u) | (int2 >> 24u)) & 0x3FFu;

    vec4 color = vec4(float(r10) / 1024., float(g10) / 1024., float(b10) / 1024., float(a10) / 1024.);

    uint size_x = int2 & 0xFFFFFFu;
    uint size_y = (int3 >> 8u) & 0xFFFFFFu;
    vec2 size = vec2(float(size_x), float(size_y)) / 8.0;

    uint radius = ((int3 << 11u) | (int4 >> 21u)) & 0x7FFFFu;
    float corner_radius = float(radius) / 8.0;

    uint thickness = (int4 >> 2u) & 0x7FFFFu;
    float border_thickness = float(thickness) / 8.0;

    uint sdf_type = int4 & 0x3u;

    const vec4 outsideColor = vec4(0.);
    vec4 borderColor = color;
    const vec4 insideColor = vec4(0.);
    float cornerRadius = corner_radius;
    float borderThickness = border_thickness;
    vec2 center = size * 0.5;

    vec2 sizeWithAA = size + vec2(aaWidth) * 2.;
    vec2 pixelPos = UV * sizeWithAA - vec2(aaWidth) - center;
    float d;

    switch(sdf_type) {
        case SDF_CW:
            d = sdPoweredDecal(vec2(UV.x, 1. - UV.y)) * sizeWithAA.x; //decal SDF assumed fixed size
            break;
        case SDF_CCW:
            d = sdPoweredDecal(vec2(1. - UV.x, 1. - UV.y)) * sizeWithAA.x; //flip horizontally for CCW decal
            break;
        case SDF_UPW:
            d = sdUnpoweredDecal(vec2(1. - UV.x, UV.y)) * sizeWithAA.x;
            break;
        default:
            d = sdRoundedRect(pixelPos, size / 2., cornerRadius);
            break;
    }

    float outsideA = clamp((d + aaWidth) / (2. * aaWidth), 0.0, 1.0);
    float insideA  = clamp(1.0 - (d + borderThickness + aaWidth) / (2. * aaWidth), 0.0, 1.0);
    float borderA  = clamp(1.0 - outsideA - insideA, 0.0, 1.0);

    vec4 outsideColorPremult = outsideColor;
    vec4 borderColorPremult = borderColor;
    vec4 insideColorPremult  = insideColor;
    outsideColorPremult.rgb *= outsideColorPremult.a;
    borderColorPremult.rgb *= borderColorPremult.a;
    insideColorPremult.rgb  *= insideColorPremult.a;

    vec4 colPremult = outsideColorPremult * outsideA + borderColorPremult * borderA + insideColorPremult * insideA;

    COLOR = vec4(colPremult.a == 0. ? vec3(0.) : colPremult.rgb / colPremult.a, colPremult.a);
}
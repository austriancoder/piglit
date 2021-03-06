// [config]
// expect_result: pass
// glsl_version: 1.40
// check_link: true
// require_extensions: GL_ARB_enhanced_layouts GL_ARB_explicit_attrib_location
// [end config]
//
// From Section 4.4.1 (Input Layout Qualifiers) of the GLSL 4.50 spec:
//
//   "Further, when location aliasing, the aliases sharing the location must
//   have the same underlying numerical type (floating-point or integer) and
//   the same auxiliary storage and interpolation qualification"
//
//   ...
//
//   "The one exception where component aliasing is permitted is for two input
//   variables (not block members) to a vertex shader, which are allowed to
//   have component aliasing. This vertex-variable component aliasing is
//   intended only to support vertex shaders where each execution path
//   accesses at most one input per each aliased component.  Implementations
//   are permitted, but not required, to generate link-time errors if they
//   detect that every path through the vertex shader executable accesses
//   multiple inputs aliased to any single component."
//
//   Issue 16 from the ARB_enhanced_layouts spec:
//
//   "We do allow this for vertex shader inputs, because we've supported
//   "aliasing" behavior since OpenGL 2.0. This allows for an "uber-shader"
//    with variables like:
//
//          layout(location=3) in float var1;
//          layout(location=3) in int var2;
//
//   where sometimes it uses <var1> and sometimes <var2>.  Since we don't
//   treat the code above (with overlapping components) as an error, it
//   would be strange to treat non-overlapping component assignments as an
//   error."

#version 140
#extension GL_ARB_enhanced_layouts: require
#extension GL_ARB_explicit_attrib_location: require

uniform int i;

// consume X/Y/Z components
layout(location = 0) in ivec3 a;

// consumes W component
layout(location = 0, component = 3) in uint b;

void main()
{
  if (i == 1)
    gl_Position = vec4(a, 1.0);
  else
    gl_Position = vec4(b);
}

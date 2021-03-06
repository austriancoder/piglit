// [config]
// expect_result: pass
// glsl_version: 1.20
// check_link: true
// [end config]
//
// Check that bulk assignment to a built-in array is allowed in GLSL 1.20.
//
// From section 5.8 of the GLSL 1.20 spec:
//     Variables that are built-in types, entire structures or arrays,
//     structure fields, l-values with the field selector ( . )
//     applied to select components or swizzles without repeated
//     fields, l-values within parentheses, and l-values dereferenced
//     with the array subscript operator ( [] ) are all l-values.

#version 120
varying vec4 gl_TexCoord[gl_MaxTextureCoords];

void f(vec4[gl_MaxTextureCoords] x)
{
  gl_TexCoord = x;
}

void main()
{
  vec4[gl_MaxTextureCoords] x;
  f(x);
  gl_Position = vec4(0.0);
}

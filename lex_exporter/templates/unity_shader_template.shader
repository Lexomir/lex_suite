Shader "{ShaderName}" {
  Properties{
    {ParameterList}
  }
  
  SubShader{
    Tags{ "RenderType" = "Opaque" }
    CGPROGRAM

    #pragma surface surf Lambert

    struct Input {
        {InputVariableDeclarations}
    };

    {ParameterVariableDeclarations}

    void surf(Input IN, inout SurfaceOutput o) {
        {Dependencies}

        o.Albedo = {Albedo};
        o.Normal = {Normal};
    }

    ENDCG
  }
    Fallback "Diffuse"
}
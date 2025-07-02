#ifndef FTRENDER_H
#define FTRENDER_H

#include "core/object/ref_counted.h"
#include "scene/main/node.h"
#include "core/math/color.h"
#include "scene/resources/material.h"
#include "core/variant/variant.h"
#include "scene/2d/multimesh_instance_2d.h"
#include "scene/resources/mesh.h"
#include "scene/resources/3d/primitive_meshes.h"
#include "scene/resources/image_texture.h"

struct ObjType {
    enum Type : uint8_t {
        STATIC_RECT_BORDER, STATIC_RECT_INSIDE,
        STATIC_CIRC_BORDER, STATIC_CIRC_INSIDE,
        DYNAMIC_RECT_BORDER, DYNAMIC_RECT_INSIDE,
        DYNAMIC_CIRC_BORDER, DYNAMIC_CIRC_INSIDE,
        GP_RECT_BORDER, GP_RECT_INSIDE,
        GP_CIRC_BORDER, GP_CIRC_INSIDE,
        UPW_BORDER, UPW_INSIDE, UPW_DECAL,
        CW_BORDER, CW_INSIDE, CW_DECAL,
        CCW_BORDER, CCW_INSIDE, CCW_DECAL,
        WATER_BORDER, WATER_INSIDE,
        WOOD_BORDER, WOOD_INSIDE,
        BUILD_BORDER, BUILD_INSIDE,
        GOAL_BORDER, GOAL_INSIDE,
        JOINT_NORMAL, JOINT_WHEEL_CENTER,
        OBJ_TYPE_SIZE,
    };
};

struct PieceType {
    enum Type : uint8_t {
        STATIC_RECT, STATIC_CIRC, DYNAMIC_RECT, DYNAMIC_CIRC, GP_RECT, GP_CIRC, UPW, CW, CCW, WATER, WOOD, BUILD, GOAL, PIECE_TYPE_SIZE
    };
};

struct SdfType {
    enum Type : uint8_t {
        ROUNDED_RECT, UPW, CW, CCW, SDF_TYPE_SIZE
    };
};

static const int LAYER_COUNT = 3;

struct RenderLayer {
    MultiMeshInstance2D* mmi;
    PackedVector2Array sizes;
    PackedFloat32Array rotations;
    PackedVector2Array poses;
    Vector<ObjType::Type> objTypes;
    uint32_t layerID;

    int32_t renderCount = 0;
    void addRenderObject(Vector2 pos, Vector2 size, float rotation, ObjType::Type type,
        int32_t multimeshInstanceCount);

    void resetRender();

    void renderPartial(float scale, Vector2 shift, float aaWidth,
        PackedColorArray colors, PackedFloat32Array cornerRadii, PackedFloat32Array borderThicknesses,
        bool (*getObjIsCircle)(ObjType::Type), SdfType::Type(*getObjSdfType)(ObjType::Type), Ref<Image>& renderImg,
        Vector2i dataImageSize) const;

    void init(MultiMeshInstance2D* mmi_, uint32_t layerID_, int32_t multimeshInstanceCount);
};

class FTRender : public Node {
    GDCLASS(FTRender, Node);

protected:
    static void _bind_methods();

private:
    int32_t layerMultimeshInstanceCount;
    Vector2i layerDataImageSize;

    PackedColorArray colors;
    PackedFloat32Array cornerRadii;
    PackedFloat32Array borderThicknesses;

    float aaWidth;
    float jointDiameter;
    float innerJointThresholdDiameter;
    Vector2 woodSizePadding;
    Vector2 waterSizePadding;
    float ghostRodPadding;

public:
    void setColors(const PackedColorArray colors_);
    PackedColorArray getColors() const;

    void setColor(ObjType::Type objType, Color color);
    Color getColor(ObjType::Type objType) const;

    void setCornerRadii(const PackedFloat32Array cornerRadii_);
    PackedFloat32Array getCornerRadii() const;

    void setCornerRadius(ObjType::Type objType, double cornerRadius);
    double getCornerRadius(ObjType::Type objType) const;

    void setBorderThicknesses(const PackedFloat32Array borderThicknesses_);
    PackedFloat32Array getBorderThicknesses() const;

    void setBorderThickness(ObjType::Type objType, double borderThickness);
    double getBorderThickness(ObjType::Type objType) const;

    static ObjType::Type getPieceBorder(PieceType::Type piece);
    static ObjType::Type getPieceInside(PieceType::Type piece);
    static ObjType::Type getPieceDecal(PieceType::Type piece);
    static bool getObjIsCircle(ObjType::Type obj);
    static SdfType::Type getObjSdfType(ObjType::Type obj);

private:
    Ref<ShaderMaterial> shaderMaterial;
    RenderLayer layers[LAYER_COUNT]; //0: areas, 1: borders, 2: insides
    Ref<Image> renderImg;
    Ref<ImageTexture> renderTex;
    void setupRenderData();

public:
    void resetRender();

    void render(float scale, Vector2 shift);

private:
    void addRoundedRect(Vector2 pos, Vector2 size, float rotation, PieceType::Type type,
        RenderLayer& borderLayer, RenderLayer& insideLayer);
    void addRoundedRectPiece(Vector2 pos, Vector2 size, float rotation, PieceType::Type type);
    void addArea(Vector2 pos, Vector2 size, float rotation, PieceType::Type type);
    void addCirclePiece(Vector2 pos, float diameter, float rotation, PieceType::Type type);
    void addJoint(Vector2 pos, float rotation, ObjType::Type type);
    void addRectJoints(Vector2 pos, Vector2 size, float rotation);
    void addJointedRect(Vector2 pos, Vector2 size, float rotation, PieceType::Type type);
    void addRodJoints(Vector2 pos, Vector2 size, float rotation);
    void addJointedRod(Vector2 pos, Vector2 size, float rotation, PieceType::Type type);
    void addCircleJoints(Vector2 pos, float diameter, float rotation, PieceType::Type type);
    void addJointedCircle(Vector2 pos, float diameter, float rotation, PieceType::Type type);
    void addDecalCircle(Vector2 pos, float diameter, float rotation, PieceType::Type type);

public:
    void addStaticRect(Vector2 pos, Vector2 size, float rotation);
    void addStaticCirc(Vector2 pos, float diameter, float rotation);
    void addDynamicRect(Vector2 pos, Vector2 size, float rotation);
    void addDynamicCirc(Vector2 pos, float diameter, float rotation);
    void addGPRect(Vector2 pos, Vector2 size, float rotation);
    void addGPCirc(Vector2 pos, float diameter, float rotation);
    void addWood(Vector2 pos, Vector2 size, float rotation);
    void addWater(Vector2 pos, Vector2 size, float rotation);
    void addCW(Vector2 pos, float diameter, float rotation);
    void addCCW(Vector2 pos, float diameter, float rotation);
    void addUPW(Vector2 pos, float diameter, float rotation);
    void addBuildArea(Vector2 pos, Vector2 size, float rotation);
    void addGoalArea(Vector2 pos, Vector2 size, float rotation);
    void addPiece(PieceType::Type type, Vector2 pos, Vector2 size, float rotation); //if circle, pos.x is used as diameter

    void initLayers(int32_t layerMultimeshInstanceCount_, Vector2i layerDataImageSize);
    void initResources(Ref<ShaderMaterial> shaderMaterial_, MultiMeshInstance2D* mmiAreas, MultiMeshInstance2D* mmiBorders, MultiMeshInstance2D* mmiInsides);
    void initVisuals(PackedColorArray colors_, PackedFloat32Array cornerRadii_, PackedFloat32Array borderThicknesses,
        float aaWidth, float jointDiameter_, float innerJointThresholdDiameter_, Vector2 woodSizePadding,
        Vector2 waterSizePadding, float ghostRodPadding);
};

VARIANT_ENUM_CAST(ObjType::Type);
VARIANT_ENUM_CAST(PieceType::Type);
VARIANT_ENUM_CAST(SdfType::Type);

#endif // FTRENDER_H

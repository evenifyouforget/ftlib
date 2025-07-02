#include "render.h"
#include "core/math/vector2.h"
#include "core/os/memory.h"
#include "core/string/print_string.h"
#include "scene/2d/sprite_2d.h"
#include "scene/resources/image_texture.h"
#include <cmath>
#include <cstdint>

float uintBitsToFloat(uint32_t u) {
	union Pun {
		uint32_t u;
		float f;
	};
	Pun p;
	p.u = u;
	return p.f;
}

// data layout:
// color: 40 bits as fixed point (10 bits per channel)
// size: 48 bits as fixed point (24 per coord)
// corner radius: 19 bits as fixed point
// border thickness: 19 bits as fixed point
// SDF used: 2 bits
// size, radius, and thickness all stored to the precision of 1/8th of a pixel
Color packDataToColor(Color color, Vector2 size, float cornerRadius, float borderThickness, SdfType::Type sdfType) {
	uint32_t r = static_cast<uint32_t>(CLAMP(color.r * 1024., 0, 1023));
	uint32_t g = static_cast<uint32_t>(CLAMP(color.g * 1024., 0, 1023));
	uint32_t b = static_cast<uint32_t>(CLAMP(color.b * 1024., 0, 1023));
	uint32_t a = static_cast<uint32_t>(CLAMP(color.a * 1024., 0, 1023));

	uint32_t sizeX = static_cast<uint32_t>(CLAMP(size.x * 8, 0, 0xFFFFFF));
	uint32_t sizeY = static_cast<uint32_t>(CLAMP(size.y * 8, 0, 0xFFFFFF));

	uint32_t radiusBits = static_cast<uint32_t>(CLAMP(cornerRadius * 8, 0, 0x7FFFF));
	uint32_t thicknessBits = static_cast<uint32_t>(CLAMP(borderThickness * 8, 0, 0x7FFFF));

	uint32_t sdfBits = static_cast<uint32_t>(sdfType) & 0x3;

	uint32_t i1 = (r << 22) | (g << 12) | (b << 2) | (a >> 8);
	uint32_t i2 = (a << 24) | (sizeX >> 0);
	uint32_t i3 = (sizeY << 8) | (radiusBits >> 11);
	uint32_t i4 = (radiusBits << 21) | (thicknessBits << 2) | sdfBits;

	return Color{ uintBitsToFloat(i1), uintBitsToFloat(i2), uintBitsToFloat(i3), uintBitsToFloat(i4) };
}

void RenderLayer::addRenderObject(Vector2 pos, Vector2 size, float rotation, ObjType::Type type,
	int32_t multimeshInstanceCount) {
	ERR_FAIL_COND_MSG(renderCount >= multimeshInstanceCount, "Too many objects to render!");

	sizes.set(renderCount, size);
	rotations.set(renderCount, rotation);
	poses.set(renderCount, pos);
	objTypes.set(renderCount, type);

	renderCount++;
}

void RenderLayer::resetRender() {
	renderCount = 0;
}

void RenderLayer::renderPartial(float scale, Vector2 shift, float aaWidth,
	PackedColorArray colors, PackedFloat32Array cornerRadii, PackedFloat32Array borderThicknesses,
	bool (*getObjIsCircle)(ObjType::Type), SdfType::Type(*getObjSdfType)(ObjType::Type), Ref<Image>& renderImg,
	Vector2i dataImageSize) const {
	Ref<MultiMesh> mm = mmi->get_multimesh();
	mmi->set_instance_shader_parameter("aaWidth", aaWidth);
	mm->set_visible_instance_count(renderCount);
	for (int i = 0; i < renderCount; i++) {
		Transform2D transform(rotations[i],
			(sizes[i] + Vector2{ aaWidth, aaWidth }) * scale,
			0,
			poses[i] * scale + shift);
		mm->set_instance_transform_2d(i, transform);

		ObjType::Type type = objTypes[i];
		Color color = colors[type];
		Vector2 size = sizes[i] * scale;
		float cornerRadius = getObjIsCircle(type) ? size.x * 0.5 : cornerRadii[type] * scale;
		float borderThickness = type == ObjType::JOINT_NORMAL || type == ObjType::JOINT_WHEEL_CENTER
			? borderThicknesses[type] * scale
			: INFINITY;
		SdfType::Type sdfType = getObjSdfType(type);

		Color data = packDataToColor(color, size, cornerRadius, borderThickness, sdfType);
		renderImg->set_pixel(i % dataImageSize.x + layerID * dataImageSize.x, i / dataImageSize.y, data);
	}
}

void RenderLayer::init(MultiMeshInstance2D* mmi_, uint32_t layerID_, int32_t multimeshInstanceCount) {
	layerID = layerID_;
	mmi = mmi_;
	mmi->set_instance_shader_parameter("layerID", layerID_);

	sizes.resize(multimeshInstanceCount);
	rotations.resize(multimeshInstanceCount);
	poses.resize(multimeshInstanceCount);
	objTypes.resize(multimeshInstanceCount);
}

#define BIND_ENUM_CLASS_CONSTANT(m_class, m_constant) ::ClassDB::bind_integer_constant(get_class_static(), \
        __constant_get_enum_name(m_class :: m_constant, #m_class "::" #m_constant), #m_class "_" #m_constant, m_class :: m_constant);

void FTRender::_bind_methods() {
	BIND_ENUM_CLASS_CONSTANT(ObjType, STATIC_RECT_BORDER);
	BIND_ENUM_CLASS_CONSTANT(ObjType, STATIC_RECT_INSIDE);
	BIND_ENUM_CLASS_CONSTANT(ObjType, STATIC_CIRC_BORDER);
	BIND_ENUM_CLASS_CONSTANT(ObjType, STATIC_CIRC_INSIDE);
	BIND_ENUM_CLASS_CONSTANT(ObjType, DYNAMIC_RECT_BORDER);
	BIND_ENUM_CLASS_CONSTANT(ObjType, DYNAMIC_RECT_INSIDE);
	BIND_ENUM_CLASS_CONSTANT(ObjType, DYNAMIC_CIRC_BORDER);
	BIND_ENUM_CLASS_CONSTANT(ObjType, DYNAMIC_CIRC_INSIDE);
	BIND_ENUM_CLASS_CONSTANT(ObjType, GP_RECT_BORDER);
	BIND_ENUM_CLASS_CONSTANT(ObjType, GP_RECT_INSIDE);
	BIND_ENUM_CLASS_CONSTANT(ObjType, GP_CIRC_BORDER);
	BIND_ENUM_CLASS_CONSTANT(ObjType, GP_CIRC_INSIDE);
	BIND_ENUM_CLASS_CONSTANT(ObjType, WOOD_BORDER);
	BIND_ENUM_CLASS_CONSTANT(ObjType, WOOD_INSIDE);
	BIND_ENUM_CLASS_CONSTANT(ObjType, WATER_BORDER);
	BIND_ENUM_CLASS_CONSTANT(ObjType, WATER_INSIDE);
	BIND_ENUM_CLASS_CONSTANT(ObjType, CW_BORDER);
	BIND_ENUM_CLASS_CONSTANT(ObjType, CW_INSIDE);
	BIND_ENUM_CLASS_CONSTANT(ObjType, CW_DECAL);
	BIND_ENUM_CLASS_CONSTANT(ObjType, CCW_BORDER);
	BIND_ENUM_CLASS_CONSTANT(ObjType, CCW_INSIDE);
	BIND_ENUM_CLASS_CONSTANT(ObjType, CCW_DECAL);
	BIND_ENUM_CLASS_CONSTANT(ObjType, UPW_BORDER);
	BIND_ENUM_CLASS_CONSTANT(ObjType, UPW_INSIDE);
	BIND_ENUM_CLASS_CONSTANT(ObjType, UPW_DECAL);
	BIND_ENUM_CLASS_CONSTANT(ObjType, BUILD_BORDER);
	BIND_ENUM_CLASS_CONSTANT(ObjType, BUILD_INSIDE);
	BIND_ENUM_CLASS_CONSTANT(ObjType, GOAL_BORDER);
	BIND_ENUM_CLASS_CONSTANT(ObjType, GOAL_INSIDE);
	BIND_ENUM_CLASS_CONSTANT(ObjType, JOINT_NORMAL);
	BIND_ENUM_CLASS_CONSTANT(ObjType, JOINT_WHEEL_CENTER);
	BIND_ENUM_CLASS_CONSTANT(ObjType, OBJ_TYPE_SIZE);

	BIND_ENUM_CLASS_CONSTANT(PieceType, STATIC_RECT);
	BIND_ENUM_CLASS_CONSTANT(PieceType, STATIC_CIRC);
	BIND_ENUM_CLASS_CONSTANT(PieceType, DYNAMIC_RECT);
	BIND_ENUM_CLASS_CONSTANT(PieceType, DYNAMIC_CIRC);
	BIND_ENUM_CLASS_CONSTANT(PieceType, GP_RECT);
	BIND_ENUM_CLASS_CONSTANT(PieceType, GP_CIRC);
	BIND_ENUM_CLASS_CONSTANT(PieceType, WOOD);
	BIND_ENUM_CLASS_CONSTANT(PieceType, WATER);
	BIND_ENUM_CLASS_CONSTANT(PieceType, CW);
	BIND_ENUM_CLASS_CONSTANT(PieceType, CCW);
	BIND_ENUM_CLASS_CONSTANT(PieceType, UPW);
	BIND_ENUM_CLASS_CONSTANT(PieceType, BUILD);
	BIND_ENUM_CLASS_CONSTANT(PieceType, GOAL);
	BIND_ENUM_CLASS_CONSTANT(PieceType, PIECE_TYPE_SIZE);

	BIND_ENUM_CLASS_CONSTANT(SdfType, ROUNDED_RECT);
	BIND_ENUM_CLASS_CONSTANT(SdfType, CW);
	BIND_ENUM_CLASS_CONSTANT(SdfType, CCW);
	BIND_ENUM_CLASS_CONSTANT(SdfType, UPW);
	BIND_ENUM_CLASS_CONSTANT(SdfType, SDF_TYPE_SIZE);

	BIND_CONSTANT(LAYER_COUNT);

	ClassDB::bind_method(D_METHOD("setColors", "colors"), &FTRender::setColors);
	ClassDB::bind_method(D_METHOD("getColors"), &FTRender::getColors);
	ClassDB::bind_method(D_METHOD("setColor", "objType", "color"), &FTRender::setColor);
	ClassDB::bind_method(D_METHOD("getColor", "objType"), &FTRender::getColor);

	ClassDB::bind_method(D_METHOD("setCornerRadii", "cornerRadii"), &FTRender::setCornerRadii);
	ClassDB::bind_method(D_METHOD("getCornerRadii"), &FTRender::getCornerRadii);
	ClassDB::bind_method(D_METHOD("setCornerRadius", "objType", "cornerRadius"), &FTRender::setCornerRadius);
	ClassDB::bind_method(D_METHOD("getCornerRadius", "objType"), &FTRender::getCornerRadius);

	ClassDB::bind_method(D_METHOD("setBorderThicknesses", "borderThicknesses"), &FTRender::setBorderThicknesses);
	ClassDB::bind_method(D_METHOD("getBorderThicknesses"), &FTRender::getBorderThicknesses);
	ClassDB::bind_method(D_METHOD("setBorderThickness", "objType", "borderThickness"), &FTRender::setBorderThickness);
	ClassDB::bind_method(D_METHOD("getBorderThickness", "objType"), &FTRender::getBorderThickness);

	ADD_PROPERTY(PropertyInfo(Variant::PACKED_COLOR_ARRAY, "colors"), "setColors", "getColors");
	ADD_PROPERTY(PropertyInfo(Variant::PACKED_FLOAT64_ARRAY, "cornerRadii"), "setCornerRadii", "getCornerRadii");
	ADD_PROPERTY(PropertyInfo(Variant::PACKED_FLOAT64_ARRAY, "borderThicknesses"), "setBorderThicknesses", "getBorderThicknesses");

	ClassDB::bind_method(D_METHOD("resetRender"), &FTRender::resetRender);
	ClassDB::bind_method(D_METHOD("render", "scale", "shift"), &FTRender::render);

	ClassDB::bind_method(D_METHOD("addStaticRect", "pos", "size", "rotation"), &FTRender::addStaticRect);
	ClassDB::bind_method(D_METHOD("addStaticCirc", "pos", "diameter", "rotation"), &FTRender::addStaticCirc);
	ClassDB::bind_method(D_METHOD("addDynamicRect", "pos", "size", "rotation"), &FTRender::addDynamicRect);
	ClassDB::bind_method(D_METHOD("addDynamicCirc", "pos", "diameter", "rotation"), &FTRender::addDynamicCirc);
	ClassDB::bind_method(D_METHOD("addGPRect", "pos", "size", "rotation"), &FTRender::addGPRect);
	ClassDB::bind_method(D_METHOD("addGPCirc", "pos", "diameter", "rotation"), &FTRender::addGPCirc);
	ClassDB::bind_method(D_METHOD("addWood", "pos", "size", "rotation"), &FTRender::addWood);
	ClassDB::bind_method(D_METHOD("addWater", "pos", "size", "rotation"), &FTRender::addWater);
	ClassDB::bind_method(D_METHOD("addCW", "pos", "diameter", "rotation"), &FTRender::addCW);
	ClassDB::bind_method(D_METHOD("addCCW", "pos", "diameter", "rotation"), &FTRender::addCCW);
	ClassDB::bind_method(D_METHOD("addUPW", "pos", "diameter", "rotation"), &FTRender::addUPW);
	ClassDB::bind_method(D_METHOD("addBuildArea", "pos", "size", "rotation"), &FTRender::addBuildArea);
	ClassDB::bind_method(D_METHOD("addGoalArea", "pos", "size", "rotation"), &FTRender::addGoalArea);
	ClassDB::bind_method(D_METHOD("addPiece", "type", "pos", "size", "rotation"), &FTRender::addPiece);

	ClassDB::bind_method(D_METHOD("initLayers", "layerMultimeshInstanceCount", "layerDataImageSize"), &FTRender::initLayers);
	ClassDB::bind_method(D_METHOD("initResources", "shaderMaterial", "mmiAreas", "mmiBorders", "mmiInsides"), &FTRender::initResources);
	ClassDB::bind_method(D_METHOD("initVisuals", "colors", "cornerRadii", "borderThicknesses", "aaWidth",
		"jointDiameter", "innerJointThresholdDiameter", "woodSizePadding", "waterSizePadding", "ghostRodPadding"), &FTRender::initVisuals);
}

void FTRender::setColors(PackedColorArray colors_) {
	colors = colors_;
}

PackedColorArray FTRender::getColors() const {
	return colors;
}

void FTRender::setColor(ObjType::Type objType, Color color) {
	colors.set(objType, color);
}

Color FTRender::getColor(ObjType::Type objType) const {
	return colors[objType];
}

void FTRender::setCornerRadii(PackedFloat32Array cornerRadii_) {
	cornerRadii = cornerRadii_;
}

PackedFloat32Array FTRender::getCornerRadii() const {
	return cornerRadii;
}

void FTRender::setCornerRadius(ObjType::Type objType, double cornerRadius) {
	cornerRadii.set(objType, cornerRadius);
}

double FTRender::getCornerRadius(ObjType::Type objType) const {
	return cornerRadii[objType];
}

void FTRender::setBorderThicknesses(PackedFloat32Array borderThicknesses_) {
	borderThicknesses = borderThicknesses_;
}

PackedFloat32Array FTRender::getBorderThicknesses() const {
	return borderThicknesses;
}

void FTRender::setBorderThickness(ObjType::Type objType, double borderThickness) {
	borderThicknesses.set(objType, borderThickness);
}

double FTRender::getBorderThickness(ObjType::Type objType) const {
	return borderThicknesses[objType];
}

ObjType::Type FTRender::getPieceBorder(PieceType::Type piece) {
	switch (piece) {
	case PieceType::STATIC_RECT:
		return ObjType::STATIC_RECT_BORDER;
	case PieceType::STATIC_CIRC:
		return ObjType::STATIC_CIRC_BORDER;
	case PieceType::DYNAMIC_RECT:
		return ObjType::DYNAMIC_RECT_BORDER;
	case PieceType::DYNAMIC_CIRC:
		return ObjType::DYNAMIC_CIRC_BORDER;
	case PieceType::GP_RECT:
		return ObjType::GP_RECT_BORDER;
	case PieceType::GP_CIRC:
		return ObjType::GP_CIRC_BORDER;
	case PieceType::UPW:
		return ObjType::UPW_BORDER;
	case PieceType::CW:
		return ObjType::CW_BORDER;
	case PieceType::CCW:
		return ObjType::CCW_BORDER;
	case PieceType::WATER:
		return ObjType::WATER_BORDER;
	case PieceType::WOOD:
		return ObjType::WOOD_BORDER;
	case PieceType::BUILD:
		return ObjType::BUILD_BORDER;
	case PieceType::GOAL:
		return ObjType::GOAL_BORDER;
	default:
		ERR_FAIL_V_MSG(ObjType::OBJ_TYPE_SIZE, "Invalid piece type!");
	}
}

ObjType::Type FTRender::getPieceInside(PieceType::Type piece) {
	switch (piece) {
	case PieceType::STATIC_RECT:
		return ObjType::STATIC_RECT_INSIDE;
	case PieceType::STATIC_CIRC:
		return ObjType::STATIC_CIRC_INSIDE;
	case PieceType::DYNAMIC_RECT:
		return ObjType::DYNAMIC_RECT_INSIDE;
	case PieceType::DYNAMIC_CIRC:
		return ObjType::DYNAMIC_CIRC_INSIDE;
	case PieceType::GP_RECT:
		return ObjType::GP_RECT_INSIDE;
	case PieceType::GP_CIRC:
		return ObjType::GP_CIRC_INSIDE;
	case PieceType::UPW:
		return ObjType::UPW_INSIDE;
	case PieceType::CW:
		return ObjType::CW_INSIDE;
	case PieceType::CCW:
		return ObjType::CCW_INSIDE;
	case PieceType::WATER:
		return ObjType::WATER_INSIDE;
	case PieceType::WOOD:
		return ObjType::WOOD_INSIDE;
	case PieceType::BUILD:
		return ObjType::BUILD_INSIDE;
	case PieceType::GOAL:
		return ObjType::GOAL_INSIDE;
	default:
		ERR_FAIL_V_MSG(ObjType::OBJ_TYPE_SIZE, "Invalid piece type!");
	}
}

ObjType::Type FTRender::getPieceDecal(PieceType::Type piece) {
	switch (piece) {
	case PieceType::UPW:
		return ObjType::UPW_DECAL;
	case PieceType::CW:
		return ObjType::CW_DECAL;
	case PieceType::CCW:
		return ObjType::CCW_DECAL;
	default:
		ERR_FAIL_V_MSG(ObjType::OBJ_TYPE_SIZE, "This piece type doesn't have a decal!");
	}
}

bool FTRender::getObjIsCircle(ObjType::Type obj) {
	switch (obj) {
	case ObjType::STATIC_CIRC_BORDER:
	case ObjType::STATIC_CIRC_INSIDE:
	case ObjType::DYNAMIC_CIRC_BORDER:
	case ObjType::DYNAMIC_CIRC_INSIDE:
	case ObjType::GP_CIRC_BORDER:
	case ObjType::GP_CIRC_INSIDE:
	case ObjType::UPW_BORDER:
	case ObjType::UPW_INSIDE:
	case ObjType::UPW_DECAL:
	case ObjType::CW_BORDER:
	case ObjType::CW_INSIDE:
	case ObjType::CW_DECAL:
	case ObjType::CCW_BORDER:
	case ObjType::CCW_INSIDE:
	case ObjType::CCW_DECAL:
	case ObjType::JOINT_NORMAL:
	case ObjType::JOINT_WHEEL_CENTER:
		return true;
	default:
		return false;
	}
}

SdfType::Type FTRender::getObjSdfType(ObjType::Type obj) {
	switch (obj) {
	case ObjType::UPW_DECAL:
		return SdfType::UPW;
	case ObjType::CW_DECAL:
		return SdfType::CW;
	case ObjType::CCW_DECAL:
		return SdfType::CCW;
	default:
		return SdfType::ROUNDED_RECT;
	}
}

void FTRender::setupRenderData() {
	renderImg = Image::create_empty(layerDataImageSize.x * LAYER_COUNT, layerDataImageSize.y,
		false, Image::FORMAT_RGBAF);
	renderTex = ImageTexture::create_from_image(renderImg);
}

void FTRender::resetRender() {
	for (auto& layer : layers) {
		layer.resetRender();
	}
}

void FTRender::render(float scale, Vector2 shift) {
	for (int i = 0; i < LAYER_COUNT; i++) {
		layers[i].renderPartial(scale, shift, aaWidth, colors, cornerRadii, borderThicknesses,
			&FTRender::getObjIsCircle, &FTRender::getObjSdfType, renderImg, layerDataImageSize);
	}
	renderTex->update(renderImg);
	shaderMaterial->set_shader_parameter("dataLayerSize", layerDataImageSize);
	shaderMaterial->set_shader_parameter("data", renderTex);
}

float getRealInsideSize(float size, float borderThickness) {
	return abs(size - 2 * borderThickness);
}

float getRealBorderSize(float size, float insideSize, float ghostRodPadding) {
	return MAX(size, insideSize + ghostRodPadding * 2);
}

void FTRender::addRoundedRect(Vector2 pos, Vector2 size, float rotation, PieceType::Type type,
	RenderLayer& borderLayer, RenderLayer& insideLayer) {
	ObjType::Type borderType = FTRender::getPieceBorder(type);
	ObjType::Type insideType = FTRender::getPieceInside(type);
	Vector2 borderThickness{ borderThicknesses[borderType], borderThicknesses[borderType] };
	Vector2 insideSize{ getRealInsideSize(size.x, borderThickness.x), getRealInsideSize(size.y, borderThickness.y) };
	Vector2 borderSize{ getRealBorderSize(size.x, insideSize.x, ghostRodPadding), getRealBorderSize(size.y, insideSize.y, ghostRodPadding) };
	borderLayer.addRenderObject(pos, borderSize, rotation, borderType, layerMultimeshInstanceCount);
	insideLayer.addRenderObject(pos, insideSize, rotation, insideType, layerMultimeshInstanceCount);
}

void FTRender::addRoundedRectPiece(Vector2 pos, Vector2 size, float rotation, PieceType::Type type) {
	addRoundedRect(pos, size, rotation, type, layers[1], layers[2]);
}

void FTRender::addArea(Vector2 pos, Vector2 size, float rotation, PieceType::Type type) {
	addRoundedRect(pos, size, rotation, type, layers[0], layers[0]);
}

void FTRender::addCirclePiece(Vector2 pos, float diameter, float rotation, PieceType::Type type) {
	addRoundedRect(pos, Vector2{ diameter, diameter }, rotation, type, layers[1], layers[2]);
}

void FTRender::addJoint(Vector2 pos, float rotation, ObjType::Type type) {
	static const Vector2 size = Vector2{ jointDiameter, jointDiameter };
	layers[2].addRenderObject(pos, size, rotation, type, layerMultimeshInstanceCount);
}

void FTRender::addRectJoints(Vector2 pos, Vector2 size, float rotation) {
	addJoint(pos, 0, ObjType::JOINT_WHEEL_CENTER);
	addJoint(Vector2(size.x * 0.5, size.y * 0.5).rotated(rotation) + pos, 0, ObjType::JOINT_NORMAL);
	addJoint(Vector2(-size.x * 0.5, size.y * 0.5).rotated(rotation) + pos, 0, ObjType::JOINT_NORMAL);
	addJoint(Vector2(size.x * 0.5, -size.y * 0.5).rotated(rotation) + pos, 0, ObjType::JOINT_NORMAL);
	addJoint(Vector2(-size.x * 0.5, -size.y * 0.5).rotated(rotation) + pos, 0, ObjType::JOINT_NORMAL);
}

void FTRender::addJointedRect(Vector2 pos, Vector2 size, float rotation, PieceType::Type type) {
	addRoundedRectPiece(pos, size, rotation, type);
	addRectJoints(pos, size, rotation);
}

void FTRender::addRodJoints(Vector2 pos, Vector2 size, float rotation) {
	addJoint(Vector2(size.x * 0.5, 0).rotated(rotation) + pos, 0, ObjType::JOINT_NORMAL);
	addJoint(Vector2(-size.x * 0.5, 0).rotated(rotation) + pos, 0, ObjType::JOINT_NORMAL);
}

void FTRender::addJointedRod(Vector2 pos, Vector2 size, float rotation, PieceType::Type type) {
	addRoundedRectPiece(pos, size, rotation, type);
	addRodJoints(pos, size, rotation);
}

void FTRender::addCircleJoints(Vector2 pos, float diameter, float rotation, PieceType::Type type) {
	addJoint(pos, 0, ObjType::JOINT_WHEEL_CENTER);
	float radius = diameter * 0.5;
	addJoint(Vector2(radius, 0).rotated(rotation) + pos, 0, ObjType::JOINT_NORMAL);
	addJoint(Vector2(-radius, 0).rotated(rotation) + pos, 0, ObjType::JOINT_NORMAL);
	addJoint(Vector2(0, radius).rotated(rotation) + pos, 0, ObjType::JOINT_NORMAL);
	addJoint(Vector2(0, -radius).rotated(rotation) + pos, 0, ObjType::JOINT_NORMAL);
	if (diameter > innerJointThresholdDiameter) {
		addJoint(Vector2(innerJointThresholdDiameter, 0).rotated(rotation) + pos, 0, ObjType::JOINT_NORMAL);
		addJoint(Vector2(-innerJointThresholdDiameter, 0).rotated(rotation) + pos, 0, ObjType::JOINT_NORMAL);
		addJoint(Vector2(0, innerJointThresholdDiameter).rotated(rotation) + pos, 0, ObjType::JOINT_NORMAL);
		addJoint(Vector2(0, -innerJointThresholdDiameter).rotated(rotation) + pos, 0, ObjType::JOINT_NORMAL);
	}
}

void FTRender::addJointedCircle(Vector2 pos, float diameter, float rotation, PieceType::Type type) {
	addCirclePiece(pos, diameter, rotation, type);
	addCircleJoints(pos, diameter, rotation, type);
}

void FTRender::addDecalCircle(Vector2 pos, float diameter, float rotation, PieceType::Type type) {
	addCirclePiece(pos, diameter, rotation, type);
	ObjType::Type borderType = FTRender::getPieceBorder(type);
	ObjType::Type decalType = FTRender::getPieceDecal(type);
	float borderThickness = borderThicknesses[borderType];
	float insideDiameter = getRealInsideSize(diameter, borderThickness);
	Vector2 insideSize{ insideDiameter, insideDiameter };
	layers[2].addRenderObject(pos, insideSize, rotation, decalType, layerMultimeshInstanceCount);
	addCircleJoints(pos, diameter, rotation, type);
}

void FTRender::addStaticRect(Vector2 pos, Vector2 size, float rotation) {
	addRoundedRectPiece(pos, size, rotation, PieceType::STATIC_RECT);
}

void FTRender::addStaticCirc(Vector2 pos, float diameter, float rotation) {
	addCirclePiece(pos, diameter, rotation, PieceType::STATIC_CIRC);
}

void FTRender::addDynamicRect(Vector2 pos, Vector2 size, float rotation) {
	addRoundedRectPiece(pos, size, rotation, PieceType::DYNAMIC_RECT);
}

void FTRender::addDynamicCirc(Vector2 pos, float diameter, float rotation) {
	addCirclePiece(pos, diameter, rotation, PieceType::DYNAMIC_CIRC);
}

void FTRender::addGPRect(Vector2 pos, Vector2 size, float rotation) {
	addJointedRect(pos, size, rotation, PieceType::GP_RECT);
}

void FTRender::addGPCirc(Vector2 pos, float diameter, float rotation) {
	addJointedCircle(pos, diameter, rotation, PieceType::GP_CIRC);
}

void FTRender::addWood(Vector2 pos, Vector2 size, float rotation) {
	addRoundedRectPiece(pos, size + woodSizePadding, rotation, PieceType::WOOD);
	addRodJoints(pos, size, rotation);
}

void FTRender::addWater(Vector2 pos, Vector2 size, float rotation) {
	addRoundedRectPiece(pos, size + waterSizePadding, rotation, PieceType::WATER);
	addRodJoints(pos, size, rotation);
}

void FTRender::addCW(Vector2 pos, float diameter, float rotation) {
	addDecalCircle(pos, diameter, rotation, PieceType::CW);
}

void FTRender::addCCW(Vector2 pos, float diameter, float rotation) {
	addDecalCircle(pos, diameter, rotation, PieceType::CCW);
}

void FTRender::addUPW(Vector2 pos, float diameter, float rotation) {
	addDecalCircle(pos, diameter, rotation, PieceType::UPW);
}

void FTRender::addBuildArea(Vector2 pos, Vector2 size, float rotation) {
	addArea(pos, size, rotation, PieceType::BUILD);
}

void FTRender::addGoalArea(Vector2 pos, Vector2 size, float rotation) {
	addArea(pos, size, rotation, PieceType::GOAL);
}

void FTRender::addPiece(PieceType::Type type, Vector2 pos, Vector2 size, float rotation) {
	switch(type) {
	case PieceType::STATIC_RECT:
		addStaticRect(pos, size, rotation);
		break;
	case PieceType::STATIC_CIRC:
		addStaticCirc(pos, size.x, rotation);
		break;
	case PieceType::DYNAMIC_RECT:
		addDynamicRect(pos, size, rotation);
		break;
	case PieceType::DYNAMIC_CIRC:
		addDynamicCirc(pos, size.x, rotation);
		break;
	case PieceType::GP_RECT:
		addGPRect(pos, size, rotation);
		break;
	case PieceType::GP_CIRC:
		addGPCirc(pos, size.x, rotation);
		break;
	case PieceType::UPW:
		addUPW(pos, size.x, rotation);
		break;
	case PieceType::CW:
		addCW(pos, size.x, rotation);
		break;
	case PieceType::CCW:
		addCCW(pos, size.x, rotation);
		break;
	case PieceType::WATER:
		addWater(pos, size, rotation);
		break;
	case PieceType::WOOD:
		addWood(pos, size, rotation);
		break;
	case PieceType::BUILD:
		addBuildArea(pos, size, rotation);
		break;
	case PieceType::GOAL:
		addBuildArea(pos, size, rotation);
		break;
	}
}

void FTRender::initLayers(int32_t layerMultimeshInstanceCount_, Vector2i layerDataImageSize_) {
	layerMultimeshInstanceCount = layerMultimeshInstanceCount_;
	layerDataImageSize = layerDataImageSize_;
}

void FTRender::initResources(Ref<ShaderMaterial> shaderMaterial_, MultiMeshInstance2D* mmiAreas,
	MultiMeshInstance2D* mmiBorders, MultiMeshInstance2D* mmiInsides) {

	shaderMaterial = shaderMaterial_;

	layers[0].init(mmiAreas, 0, layerMultimeshInstanceCount);
	layers[1].init(mmiBorders, 1, layerMultimeshInstanceCount);
	layers[2].init(mmiInsides, 2, layerMultimeshInstanceCount);

	setupRenderData();
}

void FTRender::initVisuals(PackedColorArray colors_, PackedFloat32Array cornerRadii_, PackedFloat32Array borderThicknesses_,
	float aaWidth_, float jointDiameter_, float innerJointThresholdDiameter_, Vector2 woodSizePadding_,
	Vector2 waterSizePadding_, float ghostRodPadding_) {
	colors = colors_;
	cornerRadii = cornerRadii_;
	borderThicknesses = borderThicknesses_;
	aaWidth = aaWidth_;
	jointDiameter = jointDiameter_;
	innerJointThresholdDiameter = innerJointThresholdDiameter_;
	woodSizePadding = woodSizePadding_;
	waterSizePadding = waterSizePadding_;
	ghostRodPadding = ghostRodPadding_;
}
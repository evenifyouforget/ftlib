extends Node

@onready var render: FTRender = $FTRender

var scale: float = 1
var shift: Vector2 = Vector2(0, 0)
const maxScale = 100
const minScale = 0.01
func zoom(deltaScale: float, screen_pos: Vector2):
    var old_scale = scale
    scale *= deltaScale
    scale = clamp(scale, minScale, maxScale)
    shift -= (screen_pos - shift) * (scale / old_scale - 1)

func _unhandled_input(event): # TODO: remove
    if event is InputEventKey && event.pressed:
        if event.keycode == KEY_I:
            zoom(1.1, get_viewport().get_mouse_position())
        elif event.keycode == KEY_O:
            zoom(1. / 1.1, get_viewport().get_mouse_position())
    if event is InputEventMouseButton:
        if event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
            zoom(1. / 1.1, get_viewport().get_mouse_position())
        elif event.button_index == MOUSE_BUTTON_WHEEL_UP:
            zoom(1.1, get_viewport().get_mouse_position())

const layerMultimeshInstanceCount: int = 16384
const layerDataSize: Vector2i = Vector2(128, 128)
@onready var shaderMaterial: ShaderMaterial = load("res://render/render.tres")
@onready var mmAreas: MultiMeshInstance2D = $FTRender/mmAreas
@onready var mmBorders: MultiMeshInstance2D = $FTRender/mmBorders
@onready var mmInsides: MultiMeshInstance2D = $FTRender/mmInsides
@export var colors: PackedColorArray = (func() -> PackedColorArray:
    var arr: PackedColorArray
    arr.resize(FTRender.ObjType_OBJ_TYPE_SIZE)
    arr[FTRender.ObjType_STATIC_RECT_BORDER] = Color("#008009"); arr[FTRender.ObjType_STATIC_RECT_INSIDE] = Color("#00be01")
    arr[FTRender.ObjType_STATIC_CIRC_BORDER] = Color("#008009"); arr[FTRender.ObjType_STATIC_CIRC_INSIDE] = Color("#00be01")
    arr[FTRender.ObjType_DYNAMIC_RECT_BORDER] = Color("#c6560c"); arr[FTRender.ObjType_DYNAMIC_RECT_INSIDE] = Color("#f9da2f")
    arr[FTRender.ObjType_DYNAMIC_CIRC_BORDER] = Color("#c6560c"); arr[FTRender.ObjType_DYNAMIC_CIRC_INSIDE] = Color("#f9da2f")
    arr[FTRender.ObjType_GP_RECT_BORDER] = Color("#bb6666"); arr[FTRender.ObjType_GP_RECT_INSIDE] = Color("#ff6666")
    arr[FTRender.ObjType_GP_CIRC_BORDER] = Color("#bb6666"); arr[FTRender.ObjType_GP_CIRC_INSIDE] = Color("#ff6666")
    arr[FTRender.ObjType_WOOD_BORDER] = Color("#b55900"); arr[FTRender.ObjType_WOOD_INSIDE] = Color("#6b3400")
    arr[FTRender.ObjType_WATER_BORDER] = Color("#ffffff"); arr[FTRender.ObjType_WATER_INSIDE] = Color("#0000ff")
    arr[FTRender.ObjType_CW_BORDER] = Color("#fc8003"); arr[FTRender.ObjType_CW_INSIDE] = Color("#ffec00"); arr[FTRender.ObjType_CW_DECAL] = Color("#fc8003")
    arr[FTRender.ObjType_CCW_BORDER] = Color("#d147a5"); arr[FTRender.ObjType_CCW_INSIDE] = Color("#ffcccc"); arr[FTRender.ObjType_CCW_DECAL] = Color("#d147a5")
    arr[FTRender.ObjType_UPW_BORDER] = Color("#0a69fd"); arr[FTRender.ObjType_UPW_INSIDE] = Color("#89fae3"); arr[FTRender.ObjType_UPW_DECAL] = Color("#4a69fd")
    arr[FTRender.ObjType_BUILD_BORDER] = Color("#7777ee"); arr[FTRender.ObjType_BUILD_INSIDE] = Color("#bcdbf9")
    arr[FTRender.ObjType_GOAL_BORDER] = Color("#bb6666"); arr[FTRender.ObjType_GOAL_INSIDE] = Color("#f19191")
    arr[FTRender.ObjType_JOINT_NORMAL] = Color("#838383"); arr[FTRender.ObjType_JOINT_WHEEL_CENTER] = Color("#ffffff");
    return arr
).call()
@export var cornerRadii: PackedFloat32Array = (func() -> PackedFloat32Array:
    var arr: PackedFloat32Array
    arr.resize(FTRender.ObjType_OBJ_TYPE_SIZE)
    arr.set(FTRender.ObjType_STATIC_RECT_BORDER, 3)
    arr.set(FTRender.ObjType_DYNAMIC_RECT_BORDER, 3)
    arr.set(FTRender.ObjType_GP_RECT_BORDER, 3)
    arr.set(FTRender.ObjType_WOOD_BORDER, 2)
    arr.set(FTRender.ObjType_WATER_BORDER, 2)
    arr.set(FTRender.ObjType_BUILD_BORDER, 2)
    arr.set(FTRender.ObjType_GOAL_BORDER, 2)
    return arr
).call()
@export var borderThicknesses: PackedFloat32Array = (func() -> PackedFloat32Array:
    var arr: PackedFloat32Array
    arr.resize(FTRender.ObjType_OBJ_TYPE_SIZE)
    arr.set(FTRender.ObjType_STATIC_RECT_BORDER, 4)
    arr.set(FTRender.ObjType_STATIC_CIRC_BORDER, 4)
    arr.set(FTRender.ObjType_DYNAMIC_RECT_BORDER, 4)
    arr.set(FTRender.ObjType_DYNAMIC_CIRC_BORDER, 4)
    arr.set(FTRender.ObjType_GP_RECT_BORDER, 4)
    arr.set(FTRender.ObjType_GP_CIRC_BORDER, 4)
    arr.set(FTRender.ObjType_WOOD_BORDER, 3)
    arr.set(FTRender.ObjType_WATER_BORDER, 3)
    arr.set(FTRender.ObjType_BUILD_BORDER, 4)
    arr.set(FTRender.ObjType_GOAL_BORDER, 4)
    arr.set(FTRender.ObjType_CW_BORDER, 4)
    arr.set(FTRender.ObjType_CCW_BORDER, 4)
    arr.set(FTRender.ObjType_UPW_BORDER, 4)
    arr.set(FTRender.ObjType_JOINT_NORMAL, 2)
    arr.set(FTRender.ObjType_JOINT_WHEEL_CENTER, 2)
    return arr
).call()
@export var aaWidth: float = 0.5
@export var jointRadius: float = 4
@export var innerJointThresholdRadius: float = 20
@export var woodSizePadding: Vector2 = Vector2(-2, 2)
@export var waterSizePadding: Vector2 = Vector2(-2, 6)
@export var ghostRodPadding: float = 1
func _ready() -> void:
    render.initLayers(layerMultimeshInstanceCount, layerDataSize)
    render.initResources(shaderMaterial, mmAreas, mmBorders, mmInsides)
    render.initVisuals(colors, cornerRadii, borderThicknesses, aaWidth, jointRadius, innerJointThresholdRadius, woodSizePadding, waterSizePadding, ghostRodPadding)

func _process(_delta: float) -> void:
    render.resetRender()

    #render.addBuildArea(Vector2(90, 109), Vector2(404, 166), 0)
    #render.addGoalArea(Vector2(562.8, 123.4), Vector2(159.10000000000002, 135.70000000000002), 0)
    #render.addStaticRect(Vector2(94.75, 228.35), Vector2(412, 92), 0)
    #render.addStaticRect(Vector2(528.8, 229.4), Vector2(254, 90), 0)
    #render.addStaticCirc(Vector2(-101.3, 231.75), 50, 0)
    #render.addStaticCirc(Vector2(662.1, 279.1), 93.4, 0)
    #render.addStaticCirc(Vector2(27.75, 27.749999999999996), 61.3, 0)
    #render.addStaticRect(Vector2(640.1500000000001, 35.8), Vector2(42.3, 68.60000000000001), 2.050224006112992)
    #render.addStaticCirc(Vector2(444.1, 268.8), 50, 0)
    #render.addStaticCirc(Vector2(158.4, 316.8), 96.4, 0)
    #render.addStaticCirc(Vector2(521.45, 305.5500000000001), 71.5, 0)
    #render.addGPCirc(Vector2(223.25, 63.54999999999999), 26 * 0.5, 0)
    #render.addCW(Vector2(152.25, 146.9), 40 * 0.5, 0)
    #render.addUPW(Vector2(102.25, 146.9), 40 * 0.5, 0)
    #render.addCCW(Vector2(52.25, 146.9), 40 * 0.5, 0)
    #render.addWater(Vector2(187.75, 105.225), Vector2(109.49074161772768, 4), -0.8652410242593587)
    #render.addWood(Vector2(272, 104.925), Vector2(150.85248589267596, 8), 1.7568161828669435)

    render.addBuildArea(Vector2(215.2, -348.05), Vector2(662.4, 346), 0);
    render.addGoalArea(Vector2(159.45, -96.95), Vector2(100, 100), 0);
    render.addDynamicRect(Vector2(-309.2, 368.7), Vector2(0, 200), 0.7616229195038193);
    render.addDynamicRect(Vector2(-287.5, 70.9), Vector2(0, 200), 1.5712846080060914);
    render.addDynamicRect(Vector2(224.15, 145.75), Vector2(0, 600), 0);
    render.addStaticRect(Vector2(-76.7, -154.1), Vector2(646.6, 44.6), 0);
    render.addStaticRect(Vector2(-80.25, 436.6), Vector2(640.4, 46.9), 0);
    render.addStaticRect(Vector2(70.8, -516), Vector2(383.9, 46.4), 0);
    render.addStaticRect(Vector2(224.0, 24.0), Vector2(47, 396.7), 0);
    render.addStaticRect(Vector2(-376.8, 142.15), Vector2(47.4, 634.2), 0);
    render.addStaticRect(Vector2(-418.05, 131.45), Vector2(58.9, 40.7), 0);
    render.addStaticRect(Vector2(-402.3, 239.4), Vector2(12, 200.3), 0);
    render.addStaticRect(Vector2(-410.7, 224.75), Vector2(12, 199.1), 0);
    render.addStaticRect(Vector2(-418.35, 218), Vector2(12, 181.9), 0);
    render.addStaticRect(Vector2(-426.5, 210.5), Vector2(12, 165.7), 0);
    render.addStaticRect(Vector2(-434.2, 203), Vector2(12, 149), 0);
    render.addStaticRect(Vector2(-441.4, 195.35), Vector2(12, 134.8), 0);
    render.addDynamicRect(Vector2(-423.75, 86.5), Vector2(47.3, 49.3), 0);
    render.addStaticRect(Vector2(-248.15, 254.15), Vector2(47.3, 147.2), 0);
    render.addStaticRect(Vector2(-87.0, 69.15), Vector2(377.9, 42.2), 0);
    render.addStaticRect(Vector2(46.3, -43.3), Vector2(361, 40.5), 0);
    render.addStaticRect(Vector2(-284.6, -43.35), Vector2(201.8, 39.8), 0);
    render.addStaticRect(Vector2(-82.55, 182.6), Vector2(43.8, 226), 0);
    render.addStaticRect(Vector2(140.7, 200.25), Vector2(214.3, 45.5), 0);
    render.addStaticRect(Vector2(73.0, -838.65), Vector2(44.5, 641.9), 0);
    render.addGPCirc(Vector2(-330.2, 360.6), 32 * 0.5, 0);
    render.addWater(Vector2(379.25, -196.075), Vector2(86.29671198834865, 4), 3.0586438866944072);
    render.addWater(Vector2(452.825, -195.55), Vector2(61.69734597209198, 4), 0.1333012777782165);
    render.addWater(Vector2(409.825, -191.975), Vector2(147.15374612968583, 4), -3.1344571987492262);
    render.addWater(Vector2(468.8, -191.35), Vector2(29.20068492347458, 4), 3.1347434456258823);
    render.addWater(Vector2(395.225, -191.875), Vector2(117.95662338334323, 4), -3.1309953394168);
    render.addWater(Vector2(352.1, -192.725), Vector2(204.22130765422037, 4), -3.1271470375307753);
    render.addWater(Vector2(245.5, -194.2), Vector2(181.53184293671455, 4), -3.122862061977511);
    render.addWater(Vector2(162.025, -194.375), Vector2(175.95034810991456, 4), -3.139603454735795);
    render.addWater(Vector2(293.125, -193.35), Vector2(86.26675199635127, 4), -3.121885060464321);
    render.addWater(Vector2(202.375, -195.05), Vector2(95.26516939574518, 4), -3.1237467792919253);
    render.addWater(Vector2(114.4, -195.225), Vector2(80.71129103167681, 4), 3.1248655892769728);
    render.addWater(Vector2(-21.7, -193.1), Vector2(191.52195696577445, 4), 3.126450207918391);
    render.addWater(Vector2(-63.15, -192.45), Vector2(108.61178573248861, 4), -0.01473189916762867);
    render.addWater(Vector2(32.6, -193.9), Vector2(82.91019237705319, 4), -0.015680258798107236);
    render.addWater(Vector2(514.05, -191.6), Vector2(61.30073409022155, 4), 3.1366987285498813);
    render.addWater(Vector2(405.125, -347.475), Vector2(444.5841483903805, 4), 2.2595011244730445);
    render.addWater(Vector2(274.4, -491.4), Vector2(546.8136428437019, 4), 3.0401042993549403);
    render.addWater(Vector2(546.25, -449.225), Vector2(139.75032200320686, 4), -1.568649639573619);
    render.addWater(Vector2(483.475, -195.7), Vector2(122.7045740793721, 4), 0.06442683942554964);
    render.addWood(Vector2(438.5749999999997, -222.50000000000023), Vector2(69.87712429686785, 8), -2.034443935795703);
    render.addWater(Vector2(464.97499999999974, -198.95000000000027), Vector2(26.487025125521328, 4), 2.5211237249947596);
    render.addWood(Vector2(449.34999999999985, -230.2), Vector2(70.75485849042454, 8), 0.7284029022430051);
    render.addWater(Vector2(375.5500000000001, -349.925), Vector2(463.2249372605065, 4), 2.319168724537061);
    render.addWater(Vector2(144.55000000000024, -299.125), Vector2(279.50467348507806, 4), -2.1237638752234416);
    render.addWater(Vector2(302.1500000000002, -468.85), Vector2(473.03970235065873, 4), -0.21646772040968099);
    render.addWater(Vector2(117.25000000000023, -379.225), Vector2(120.54195327768667, 4), -2.4416496870166715);
    render.addWater(Vector2(199.84999999999997, -334.2), Vector2(311.8070717607289, 4), 1.564061342035788);
    render.addWater(Vector2(-56.24999999999966, -321.25), Vector2(308.10274260382687, 4), -1.1802245913381395);
    render.addWater(Vector2(268.62499999999983, -286.3), Vector2(585.3227421687963, 4), -0.32356043383270094);
    render.addWater(Vector2(154.37500000000023, -346.325), Vector2(634.2669824293231, 4), -0.5565353606564786);
    render.addWater(Vector2(312.2749999999999, -346.075), Vector2(402.75472064272594, 4), 2.156836325693652);
    render.addWater(Vector2(495.0, -361.975), Vector2(324.449244875065, 4), -1.3334051685046733);
    render.addWater(Vector2(546.225, -434.175), Vector2(109.65028499734963, 4), -1.5685163489854193);
    render.addWater(Vector2(405.1, -332.425), Vector2(421.74538823797496, 4), 2.3047834407342354);
    render.addWood(Vector2(488.3500000000001, -190.7500000000001), Vector2(68.58141147570585, 8), 0.4062320114064488);
    render.addWood(Vector2(537.675, -310.62500000000006), Vector2(268.48162879422483, 8), 1.6123381174178268);
    render.addWater(Vector2(349.42499999999984, -421.09999999999985), Vector2(390.525047212084, 4), -0.12141709605955493);
    render.addWater(Vector2(345.7499999999999, -338.84999999999985), Vector2(397.9496576201573, 4), 0.2989423331866208);
    render.addWater(Vector2(534.0, -228.375), Vector2(103.81956703820325, 4), 1.607406467825042);
    render.addWood(Vector2(231.37499999999991, -349.2750000000001), Vector2(710.0056513859589, 8), -0.4927203566580412);
    render.addWood(Vector2(231.37499999999991, -349.2750000000001), Vector2(710.0056513859589, 8), -0.4927203566580412);
    render.addWood(Vector2(231.37499999999991, -349.2750000000001), Vector2(710.0056513859589, 8), -0.4927203566580412);
    render.addWood(Vector2(231.37499999999991, -349.2750000000001), Vector2(710.0056513859589, 8), -0.4927203566580412);
    render.addWood(Vector2(231.37499999999991, -349.2750000000001), Vector2(710.0056513859589, 8), -0.4927203566580412);
    render.addWater(Vector2(40.975000000000065, -260.87500000000006), Vector2(291.88947394519045, 4), 2.5653251506057138);
    render.addWater(Vector2(269.27499999999975, -337.10000000000014), Vector2(322.68246388671304, 4), -1.5371656007531562);
    render.addWater(Vector2(72.12499999999997, -179.84999999999985), Vector2(350.1532128940128, 4), 3.137308801457009);
    render.addWater(Vector2(514.0999999999999, -215.15), Vector2(24.82841114529855, 4), -1.229939817279838);
    render.addWater(Vector2(527.3250000000004, -197.60000000000025), Vector2(36.66677651498721, 4), 0.3247690877039665);
    render.addWater(Vector2(130.75, -335.625), Vector2(337.59933723276214, 4), -1.1558502302577351);
    render.addWater(Vector2(140.32500000000005, -180.67499999999984), Vector2(155.25290657504635, 4), 0.006119086266999844);
    render.addWater(Vector2(19.99999999999949, -287.775), Vector2(348.8034726031263, 4), 2.4615011758759584);
    render.addWater(Vector2(129.3250000000001, -268.6750000000004), Vector2(314.84130129320675, 4), 2.641929071123555);
    render.addWater(Vector2(163.4249999999999, -251.92500000000018), Vector2(363.985885715366, 4), 2.8133261184332174);
    render.addWood(Vector2(72.9500000000001, -194.5750000000004), Vector2(163.62146100068904, 8), 3.125396026019772);
    render.addWater(Vector2(-107.22499999999997, -335.4499999999998), Vector2(312.8168673521299, 4), -1.5981320167854722);
    render.addWater(Vector2(85.87499999999994, -338.7249999999999), Vector2(494.5099442882822, 4), 2.4397988389431307);
    render.addWater(Vector2(260.9499999999998, -339.47499999999997), Vector2(318.9377878207599, 4), 1.657127236708582);
    render.addWood(Vector2(232.025, -349.625), Vector2(711.4821325936441, 8), -0.49272289052708557);
    render.addWater(Vector2(-113.57500000000005, -452.3999999999999), Vector2(78.90920415262073, 4), 1.6234126917661362);
    render.addWater(Vector2(65.77499999999989, -296.79999999999995), Vector2(430.89428227814767, 4), 0.569657219266125);
    render.addWater(Vector2(-107.97500000000028, -335.4000000000002), Vector2(314.96939930729775, 4), -1.5223599878467753);
    render.addWood(Vector2(231.975, -349.4), Vector2(711.1812515104712, 8), -0.49223192003735156);
    render.addWood(Vector2(301.5999999999999, -327.3499999999998), Vector2(75.98348504773897, 8), -2.6850079053678657);
    render.addWater(Vector2(282.85, -283.44999999999993), Vector2(125.12465784169015, 4), 1.3229101316402645);
    render.addWater(Vector2(316.9499999999998, -266.6999999999997), Vector2(95.4729804709162, 4), -1.167142333853729);
    render.addWater(Vector2(370.0749999999998, -363.0), Vector2(315.1003371943612, 4), -1.0970717045624165);
    render.addWater(Vector2(185.05, -320.35000000000025), Vector2(464.3715968919716, 4), 0.6654249637962599);
    render.addWater(Vector2(315.77499999999975, -176.42500000000024), Vector2(103.85636716157573, 4), 3.130519442257947);
    render.addWater(Vector2(-109.30000000000001, -296.0499999999999), Vector2(234.2445303523651, 4), 1.516552882577663);
    render.addWood(Vector2(521.2383613395593, -230.95875350267696), Vector2(10.161133566986708, 8), -0.9419718692625559);
    render.addWood(Vector2(502.4807280900011, -204.3471359549996), Vector2(15.045913170991634, 8), -3.0220550653574283);
    render.addWater(Vector2(531.4750000000001, -209.30000000000024), Vector2(43.950113765495765, 4), 0.9250199090725243);
    render.addWater(Vector2(534.4633613395599, -213.4087535026772), Vector2(47.9120182982993, 4), -2.012311520187584);
    render.addWater(Vector2(197.4, -334.12499999999994), Vector2(317.63452661825, 4), 1.3830019044139767);
    render.addWater(Vector2(249.37500000000009, -331.5500000000001), Vector2(655.1964762573133, 4), -0.4859351721081133);
    render.addWater(Vector2(249.45000049999996, -331.5500000000002), Vector2(655.3291166726838, 4), -0.48582827041977533);
    render.addWater(Vector2(249.45000000000002, -331.5500000000002), Vector2(655.3291157883954, 4), -0.4858282711323042);
    render.addWater(Vector2(24.624999999999986, -311.3750000000001), Vector2(295.6872418620728, 4), -1.1161479454681489);
    render.addWood(Vector2(311.1, -449.22499999999985), Vector2(50.576007157544964, 8), -1.3087929297870304);
    render.addWood(Vector2(339.6, -458.8249999999999), Vector2(52.974828928463815, 8), 0.5940234732009722);
    render.addWater(Vector2(232.07500000000005, -235.2249999999999), Vector2(618.430727729469, 4), 3.117416208582593);
    render.addWater(Vector2(387.1500000000001, -211.4749999999998), Vector2(314.3654123786524, 4), -0.1999845306398804);
    render.addWater(Vector2(498.8250000000003, -340.12499999999983), Vector2(212.48314050766496, 4), -1.9810644053656885);
    render.addWater(Vector2(488.9250000000003, -364.4499999999998), Vector2(159.97794379226184, 4), 1.1527306669274615);
    render.addWater(Vector2(531.3000000000003, -267.0249999999997), Vector2(52.52487505934682, 4), 1.1842797692665337);
    render.addWater(Vector2(510.2000000000001, -277.8749999999997), Vector2(35.0437226903766, 4), 2.2642558313101344);
    render.addWater(Vector2(180.7500000000001, -334.3249999999999), Vector2(312.7326693839322, 4), 1.487562153167915);
    render.addWater(Vector2(58.35000000000002, -203.12500000000006), Vector2(275.2420798133894, 4), -2.9616904097684973);
    render.addWater(Vector2(34.674999999999976, -335.57499999999993), Vector2(333.6282736819526, 4), -1.2049567150001823);
    render.addWater(Vector2(142.27499999999998, -334.6749999999997), Vector2(327.68192656904364, 4), 1.273946503531019);
    render.addWater(Vector2(411.22500000000014, -417.8749999999998), Vector2(98.63886151005633, 4), -0.4103496660628211);
    render.addWater(Vector2(493.7750000000001, -351.35), Vector2(237.09873997978212, 4), -1.9823615110919248);
    render.addWater(Vector2(451.4000000000001, -448.77500000000015), Vector2(24.617321137768517, 4), 1.148035010404229);
    render.addWater(Vector2(406.17499999999995, -429.1), Vector2(101.3674627284321, 4), 2.485957175915139);
    render.addWater(Vector2(367.07499999999993, -348.3999999999999), Vector2(491.20637465326143, 4), -0.7667551576276914);
    render.addWater(Vector2(217.95, -273.975), Vector2(229.72368728539965, 4), -2.567535052828205);
    render.addWood(Vector2(333.6500000000002, -423.02499999999986), Vector2(86.02739389287599, 8), 2.743493100483446);
    render.addWater(Vector2(230.87500000000006, -448.2499999999998), Vector2(151.53053322680555, 4), -2.555603408720134);
    render.addWater(Vector2(510.32500000000016, -242.04999999999984), Vector2(61.763682694606445, 4), 3.1205431314527505);
    render.addWater(Vector2(201.19999999999993, -234.57500000000002), Vector2(556.6673804885645, 4), 3.1170692689775787);
    render.addWater(Vector2(489.22499999999997, -252.89999999999986), Vector2(30.186130921335128, 4), 2.2752903910371147);
    render.addWater(Vector2(78.02499999999989, -204.0), Vector2(313.7662704944559, 4), -2.989621792239287);
    render.addWater(Vector2(273.75, -195.9249999999999), Vector2(87.13502453089697, 4), 2.773553661168991);
    render.addWater(Vector2(177.29999999999995, -258.3), Vector2(191.88999452811518, 4), -2.191469875271229);
    render.addWater(Vector2(101.84999999999992, -258.225), Vector2(161.11658046271984, 4), 1.8172050657194116);
    render.addWater(Vector2(128.92499999999995, -335.9999999999999), Vector2(325.5029070530707, 4), -1.2796043667157695);
    render.addWater(Vector2(198.45000000000036, -334.325), Vector2(318.4319118744224, 4), 1.4271005931631653);
    render.addWater(Vector2(100.35000000000004, -180.77500000000006), Vector2(250.7075836507545, 4), 3.1338145894655076);
    render.addWater(Vector2(188.7, -181.17500000000007), Vector2(74.0089352713578, 4), 3.126053363925027);
    render.addWater(Vector2(116.9499999999999, -180.34999999999997), Vector2(69.50179853787958, 4), 3.1343985330994997);
    render.addWater(Vector2(354.4749999999999, -433.34999999999974), Vector2(25.571712887485667, 4), 2.1571720337301);
    render.addWater(Vector2(325.9749999999999, -423.7499999999997), Vector2(42.90142771517041, 4), -3.0926236650644974);
    render.addWater(Vector2(332.525, -448.1749999999999), Vector2(58.999703389085056, 4), -2.0992977867246085);
    render.addWater(Vector2(356.69999999999993, -410.4499999999997), Vector2(30.76052665348906, 4), 0.9214435292675521);
    render.addWater(Vector2(260.5250000000001, -292.22499999999997), Vector2(237.8662754574508, 4), 1.856112300080174);
    render.addWater(Vector2(300.1750000000002, -308.90000000000003), Vector2(299.70589333544973, 4), -1.0610241619609253);
    render.addWater(Vector2(158.29999999999998, -311.1500000000001), Vector2(299.5253912442148, 4), 1.0938599674468634);

    render.render(scale, shift)

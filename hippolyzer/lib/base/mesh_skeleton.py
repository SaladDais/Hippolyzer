from typing import *

from hippolyzer.lib.base.datatypes import Vector3


class JointNode(NamedTuple):
    parent: Optional[str]
    translation: Vector3


# Joint translation data resolved from the male collada file
# TODO: Get this from avatar_skeleton.xml instead? We may need other transforms.
SKELETON_JOINTS = {
    'mPelvis': JointNode(parent=None, translation=Vector3(0.0, 0.0, 1.067)),
    'PELVIS': JointNode(parent='mPelvis', translation=Vector3(-0.01, 0.0, -0.02)),
    'BUTT': JointNode(parent='mPelvis', translation=Vector3(-0.06, 0.0, -0.1)),
    'mSpine1': JointNode(parent='mPelvis', translation=Vector3(0.0, 0.0, 0.084)),
    'mSpine2': JointNode(parent='mSpine1', translation=Vector3(0.0, 0.0, -0.084)),
    'mTorso': JointNode(parent='mSpine2', translation=Vector3(0.0, 0.0, 0.084)),
    'BELLY': JointNode(parent='mTorso', translation=Vector3(0.028, 0.0, 0.04)),
    'LEFT_HANDLE': JointNode(parent='mTorso', translation=Vector3(0.0, 0.1, 0.058)),
    'RIGHT_HANDLE': JointNode(parent='mTorso', translation=Vector3(0.0, -0.1, 0.058)),
    'LOWER_BACK': JointNode(parent='mTorso', translation=Vector3(0.0, 0.0, 0.023)),
    'mSpine3': JointNode(parent='mTorso', translation=Vector3(-0.015, 0.0, 0.205)),
    'mSpine4': JointNode(parent='mSpine3', translation=Vector3(0.015, 0.0, -0.205)),
    'mChest': JointNode(parent='mSpine4', translation=Vector3(-0.015, 0.0, 0.205)),
    'CHEST': JointNode(parent='mChest', translation=Vector3(0.028, 0.0, 0.07)),
    'LEFT_PEC': JointNode(parent='mChest', translation=Vector3(0.119, 0.082, 0.042)),
    'RIGHT_PEC': JointNode(parent='mChest', translation=Vector3(0.119, -0.082, 0.042)),
    'UPPER_BACK': JointNode(parent='mChest', translation=Vector3(0.0, 0.0, 0.017)),
    'mNeck': JointNode(parent='mChest', translation=Vector3(-0.01, 0.0, 0.251)),
    'NECK': JointNode(parent='mNeck', translation=Vector3(0.0, 0.0, 0.02)),
    'mHead': JointNode(parent='mNeck', translation=Vector3(0.0, 0.0, 0.076)),
    'HEAD': JointNode(parent='mHead', translation=Vector3(0.02, 0.0, 0.07)),
    'mSkull': JointNode(parent='mHead', translation=Vector3(0.0, 0.0, 0.079)),
    'mEyeRight': JointNode(parent='mHead', translation=Vector3(0.098, -0.036, 0.079)),
    'mEyeLeft': JointNode(parent='mHead', translation=Vector3(0.098, 0.036, 0.079)),
    'mFaceRoot': JointNode(parent='mHead', translation=Vector3(0.025, 0.0, 0.045)),
    'mFaceEyeAltRight': JointNode(parent='mFaceRoot', translation=Vector3(0.073, -0.036, 0.034)),
    'mFaceEyeAltLeft': JointNode(parent='mFaceRoot', translation=Vector3(0.073, 0.036, 0.034)),
    'mFaceForeheadLeft': JointNode(parent='mFaceRoot', translation=Vector3(0.061, 0.035, 0.083)),
    'mFaceForeheadRight': JointNode(parent='mFaceRoot', translation=Vector3(0.061, -0.035, 0.083)),
    'mFaceEyebrowOuterLeft': JointNode(parent='mFaceRoot', translation=Vector3(0.064, 0.051, 0.048)),
    'mFaceEyebrowCenterLeft': JointNode(parent='mFaceRoot', translation=Vector3(0.07, 0.043, 0.056)),
    'mFaceEyebrowInnerLeft': JointNode(parent='mFaceRoot', translation=Vector3(0.075, 0.022, 0.051)),
    'mFaceEyebrowOuterRight': JointNode(parent='mFaceRoot', translation=Vector3(0.064, -0.051, 0.048)),
    'mFaceEyebrowCenterRight': JointNode(parent='mFaceRoot', translation=Vector3(0.07, -0.043, 0.056)),
    'mFaceEyebrowInnerRight': JointNode(parent='mFaceRoot', translation=Vector3(0.075, -0.022, 0.051)),
    'mFaceEyeLidUpperLeft': JointNode(parent='mFaceRoot', translation=Vector3(0.073, 0.036, 0.034)),
    'mFaceEyeLidLowerLeft': JointNode(parent='mFaceRoot', translation=Vector3(0.073, 0.036, 0.034)),
    'mFaceEyeLidUpperRight': JointNode(parent='mFaceRoot', translation=Vector3(0.073, -0.036, 0.034)),
    'mFaceEyeLidLowerRight': JointNode(parent='mFaceRoot', translation=Vector3(0.073, -0.036, 0.034)),
    'mFaceEar1Left': JointNode(parent='mFaceRoot', translation=Vector3(0.0, 0.08, 0.002)),
    'mFaceEar2Left': JointNode(parent='mFaceEar1Left', translation=Vector3(-0.019, 0.018, 0.025)),
    'mFaceEar1Right': JointNode(parent='mFaceRoot', translation=Vector3(0.0, -0.08, 0.002)),
    'mFaceEar2Right': JointNode(parent='mFaceEar1Right', translation=Vector3(-0.019, -0.018, 0.025)),
    'mFaceNoseLeft': JointNode(parent='mFaceRoot', translation=Vector3(0.086, 0.015, -0.004)),
    'mFaceNoseCenter': JointNode(parent='mFaceRoot', translation=Vector3(0.102, 0.0, 0.0)),
    'mFaceNoseRight': JointNode(parent='mFaceRoot', translation=Vector3(0.086, -0.015, -0.004)),
    'mFaceCheekLowerLeft': JointNode(parent='mFaceRoot', translation=Vector3(0.05, 0.034, -0.031)),
    'mFaceCheekUpperLeft': JointNode(parent='mFaceRoot', translation=Vector3(0.07, 0.034, -0.005)),
    'mFaceCheekLowerRight': JointNode(parent='mFaceRoot', translation=Vector3(0.05, -0.034, -0.031)),
    'mFaceCheekUpperRight': JointNode(parent='mFaceRoot', translation=Vector3(0.07, -0.034, -0.005)),
    'mFaceJaw': JointNode(parent='mFaceRoot', translation=Vector3(-0.001, 0.0, -0.015)),
    'mFaceChin': JointNode(parent='mFaceJaw', translation=Vector3(0.074, 0.0, -0.054)),
    'mFaceTeethLower': JointNode(parent='mFaceJaw', translation=Vector3(0.021, 0.0, -0.039)),
    'mFaceLipLowerLeft': JointNode(parent='mFaceTeethLower', translation=Vector3(0.045, 0.0, 0.0)),
    'mFaceLipLowerRight': JointNode(parent='mFaceTeethLower', translation=Vector3(0.045, 0.0, 0.0)),
    'mFaceLipLowerCenter': JointNode(parent='mFaceTeethLower', translation=Vector3(0.045, 0.0, 0.0)),
    'mFaceTongueBase': JointNode(parent='mFaceTeethLower', translation=Vector3(0.039, 0.0, 0.005)),
    'mFaceTongueTip': JointNode(parent='mFaceTongueBase', translation=Vector3(0.022, 0.0, 0.007)),
    'mFaceJawShaper': JointNode(parent='mFaceRoot', translation=Vector3(0.0, 0.0, 0.0)),
    'mFaceForeheadCenter': JointNode(parent='mFaceRoot', translation=Vector3(0.069, 0.0, 0.065)),
    'mFaceNoseBase': JointNode(parent='mFaceRoot', translation=Vector3(0.094, 0.0, -0.016)),
    'mFaceTeethUpper': JointNode(parent='mFaceRoot', translation=Vector3(0.02, 0.0, -0.03)),
    'mFaceLipUpperLeft': JointNode(parent='mFaceTeethUpper', translation=Vector3(0.045, 0.0, -0.003)),
    'mFaceLipUpperRight': JointNode(parent='mFaceTeethUpper', translation=Vector3(0.045, 0.0, -0.003)),
    'mFaceLipCornerLeft': JointNode(parent='mFaceTeethUpper', translation=Vector3(0.028, -0.019, -0.01)),
    'mFaceLipCornerRight': JointNode(parent='mFaceTeethUpper', translation=Vector3(0.028, 0.019, -0.01)),
    'mFaceLipUpperCenter': JointNode(parent='mFaceTeethUpper', translation=Vector3(0.045, 0.0, -0.003)),
    'mFaceEyecornerInnerLeft': JointNode(parent='mFaceRoot', translation=Vector3(0.075, 0.017, 0.032)),
    'mFaceEyecornerInnerRight': JointNode(parent='mFaceRoot', translation=Vector3(0.075, -0.017, 0.032)),
    'mFaceNoseBridge': JointNode(parent='mFaceRoot', translation=Vector3(0.091, 0.0, 0.02)),
    'mCollarLeft': JointNode(parent='mChest', translation=Vector3(-0.021, 0.085, 0.165)),
    'L_CLAVICLE': JointNode(parent='mCollarLeft', translation=Vector3(0.02, 0.0, 0.02)),
    'mShoulderLeft': JointNode(parent='mCollarLeft', translation=Vector3(0.0, 0.079, 0.0)),
    'L_UPPER_ARM': JointNode(parent='mShoulderLeft', translation=Vector3(0.0, 0.12, 0.01)),
    'mElbowLeft': JointNode(parent='mShoulderLeft', translation=Vector3(0.0, 0.248, 0.0)),
    'L_LOWER_ARM': JointNode(parent='mElbowLeft', translation=Vector3(0.0, 0.1, 0.0)),
    'mWristLeft': JointNode(parent='mElbowLeft', translation=Vector3(0.0, 0.205, 0.0)),
    'L_HAND': JointNode(parent='mWristLeft', translation=Vector3(0.01, 0.05, 0.0)),
    'mHandMiddle1Left': JointNode(parent='mWristLeft', translation=Vector3(0.013, 0.101, 0.015)),
    'mHandMiddle2Left': JointNode(parent='mHandMiddle1Left', translation=Vector3(-0.001, 0.04, -0.006)),
    'mHandMiddle3Left': JointNode(parent='mHandMiddle2Left', translation=Vector3(-0.001, 0.049, -0.008)),
    'mHandIndex1Left': JointNode(parent='mWristLeft', translation=Vector3(0.038, 0.097, 0.015)),
    'mHandIndex2Left': JointNode(parent='mHandIndex1Left', translation=Vector3(0.017, 0.036, -0.006)),
    'mHandIndex3Left': JointNode(parent='mHandIndex2Left', translation=Vector3(0.014, 0.032, -0.006)),
    'mHandRing1Left': JointNode(parent='mWristLeft', translation=Vector3(-0.01, 0.099, 0.009)),
    'mHandRing2Left': JointNode(parent='mHandRing1Left', translation=Vector3(-0.013, 0.038, -0.008)),
    'mHandRing3Left': JointNode(parent='mHandRing2Left', translation=Vector3(-0.013, 0.04, -0.009)),
    'mHandPinky1Left': JointNode(parent='mWristLeft', translation=Vector3(-0.031, 0.095, 0.003)),
    'mHandPinky2Left': JointNode(parent='mHandPinky1Left', translation=Vector3(-0.024, 0.025, -0.006)),
    'mHandPinky3Left': JointNode(parent='mHandPinky2Left', translation=Vector3(-0.015, 0.018, -0.004)),
    'mHandThumb1Left': JointNode(parent='mWristLeft', translation=Vector3(0.031, 0.026, 0.004)),
    'mHandThumb2Left': JointNode(parent='mHandThumb1Left', translation=Vector3(0.028, 0.032, -0.001)),
    'mHandThumb3Left': JointNode(parent='mHandThumb2Left', translation=Vector3(0.023, 0.031, -0.001)),
    'mCollarRight': JointNode(parent='mChest', translation=Vector3(-0.021, -0.085, 0.165)),
    'R_CLAVICLE': JointNode(parent='mCollarRight', translation=Vector3(0.02, 0.0, 0.02)),
    'mShoulderRight': JointNode(parent='mCollarRight', translation=Vector3(0.0, -0.079, 0.0)),
    'R_UPPER_ARM': JointNode(parent='mShoulderRight', translation=Vector3(0.0, -0.12, 0.01)),
    'mElbowRight': JointNode(parent='mShoulderRight', translation=Vector3(0.0, -0.248, 0.0)),
    'R_LOWER_ARM': JointNode(parent='mElbowRight', translation=Vector3(0.0, -0.1, 0.0)),
    'mWristRight': JointNode(parent='mElbowRight', translation=Vector3(0.0, -0.205, 0.0)),
    'R_HAND': JointNode(parent='mWristRight', translation=Vector3(0.01, -0.05, 0.0)),
    'mHandMiddle1Right': JointNode(parent='mWristRight', translation=Vector3(0.013, -0.101, 0.015)),
    'mHandMiddle2Right': JointNode(parent='mHandMiddle1Right', translation=Vector3(-0.001, -0.04, -0.006)),
    'mHandMiddle3Right': JointNode(parent='mHandMiddle2Right', translation=Vector3(-0.001, -0.049, -0.008)),
    'mHandIndex1Right': JointNode(parent='mWristRight', translation=Vector3(0.038, -0.097, 0.015)),
    'mHandIndex2Right': JointNode(parent='mHandIndex1Right', translation=Vector3(0.017, -0.036, -0.006)),
    'mHandIndex3Right': JointNode(parent='mHandIndex2Right', translation=Vector3(0.014, -0.032, -0.006)),
    'mHandRing1Right': JointNode(parent='mWristRight', translation=Vector3(-0.01, -0.099, 0.009)),
    'mHandRing2Right': JointNode(parent='mHandRing1Right', translation=Vector3(-0.013, -0.038, -0.008)),
    'mHandRing3Right': JointNode(parent='mHandRing2Right', translation=Vector3(-0.013, -0.04, -0.009)),
    'mHandPinky1Right': JointNode(parent='mWristRight', translation=Vector3(-0.031, -0.095, 0.003)),
    'mHandPinky2Right': JointNode(parent='mHandPinky1Right', translation=Vector3(-0.024, -0.025, -0.006)),
    'mHandPinky3Right': JointNode(parent='mHandPinky2Right', translation=Vector3(-0.015, -0.018, -0.004)),
    'mHandThumb1Right': JointNode(parent='mWristRight', translation=Vector3(0.031, -0.026, 0.004)),
    'mHandThumb2Right': JointNode(parent='mHandThumb1Right', translation=Vector3(0.028, -0.032, -0.001)),
    'mHandThumb3Right': JointNode(parent='mHandThumb2Right', translation=Vector3(0.023, -0.031, -0.001)),
    'mWingsRoot': JointNode(parent='mChest', translation=Vector3(-0.014, 0.0, 0.0)),
    'mWing1Left': JointNode(parent='mWingsRoot', translation=Vector3(-0.099, 0.105, 0.181)),
    'mWing2Left': JointNode(parent='mWing1Left', translation=Vector3(-0.168, 0.169, 0.067)),
    'mWing3Left': JointNode(parent='mWing2Left', translation=Vector3(-0.181, 0.183, 0.0)),
    'mWing4Left': JointNode(parent='mWing3Left', translation=Vector3(-0.171, 0.173, 0.0)),
    'mWing4FanLeft': JointNode(parent='mWing3Left', translation=Vector3(-0.171, 0.173, 0.0)),
    'mWing1Right': JointNode(parent='mWingsRoot', translation=Vector3(-0.099, -0.105, 0.181)),
    'mWing2Right': JointNode(parent='mWing1Right', translation=Vector3(-0.168, -0.169, 0.067)),
    'mWing3Right': JointNode(parent='mWing2Right', translation=Vector3(-0.181, -0.183, 0.0)),
    'mWing4Right': JointNode(parent='mWing3Right', translation=Vector3(-0.171, -0.173, 0.0)),
    'mWing4FanRight': JointNode(parent='mWing3Right', translation=Vector3(-0.171, -0.173, 0.0)),
    'mHipRight': JointNode(parent='mPelvis', translation=Vector3(0.034, -0.129, -0.041)),
    'R_UPPER_LEG': JointNode(parent='mHipRight', translation=Vector3(-0.02, 0.05, -0.22)),
    'mKneeRight': JointNode(parent='mHipRight', translation=Vector3(-0.001, 0.049, -0.491)),
    'R_LOWER_LEG': JointNode(parent='mKneeRight', translation=Vector3(-0.02, 0.0, -0.2)),
    'mAnkleRight': JointNode(parent='mKneeRight', translation=Vector3(-0.029, 0.0, -0.468)),
    'R_FOOT': JointNode(parent='mAnkleRight', translation=Vector3(0.077, 0.0, -0.041)),
    'mFootRight': JointNode(parent='mAnkleRight', translation=Vector3(0.112, 0.0, -0.061)),
    'mToeRight': JointNode(parent='mFootRight', translation=Vector3(0.109, 0.0, 0.0)),
    'mHipLeft': JointNode(parent='mPelvis', translation=Vector3(0.034, 0.127, -0.041)),
    'L_UPPER_LEG': JointNode(parent='mHipLeft', translation=Vector3(-0.02, -0.05, -0.22)),
    'mKneeLeft': JointNode(parent='mHipLeft', translation=Vector3(-0.001, -0.046, -0.491)),
    'L_LOWER_LEG': JointNode(parent='mKneeLeft', translation=Vector3(-0.02, 0.0, -0.2)),
    'mAnkleLeft': JointNode(parent='mKneeLeft', translation=Vector3(-0.029, 0.001, -0.468)),
    'L_FOOT': JointNode(parent='mAnkleLeft', translation=Vector3(0.077, 0.0, -0.041)),
    'mFootLeft': JointNode(parent='mAnkleLeft', translation=Vector3(0.112, 0.0, -0.061)),
    'mToeLeft': JointNode(parent='mFootLeft', translation=Vector3(0.109, 0.0, 0.0)),
    'mTail1': JointNode(parent='mPelvis', translation=Vector3(-0.116, 0.0, 0.047)),
    'mTail2': JointNode(parent='mTail1', translation=Vector3(-0.197, 0.0, 0.0)),
    'mTail3': JointNode(parent='mTail2', translation=Vector3(-0.168, 0.0, 0.0)),
    'mTail4': JointNode(parent='mTail3', translation=Vector3(-0.142, 0.0, 0.0)),
    'mTail5': JointNode(parent='mTail4', translation=Vector3(-0.112, 0.0, 0.0)),
    'mTail6': JointNode(parent='mTail5', translation=Vector3(-0.094, 0.0, 0.0)),
    'mGroin': JointNode(parent='mPelvis', translation=Vector3(0.064, 0.0, -0.097)),
    'mHindLimbsRoot': JointNode(parent='mPelvis', translation=Vector3(-0.2, 0.0, 0.084)),
    'mHindLimb1Left': JointNode(parent='mHindLimbsRoot', translation=Vector3(-0.204, 0.129, -0.125)),
    'mHindLimb2Left': JointNode(parent='mHindLimb1Left', translation=Vector3(0.002, -0.046, -0.491)),
    'mHindLimb3Left': JointNode(parent='mHindLimb2Left', translation=Vector3(-0.03, -0.003, -0.468)),
    'mHindLimb4Left': JointNode(parent='mHindLimb3Left', translation=Vector3(0.112, 0.0, -0.061)),
    'mHindLimb1Right': JointNode(parent='mHindLimbsRoot', translation=Vector3(-0.204, -0.129, -0.125)),
    'mHindLimb2Right': JointNode(parent='mHindLimb1Right', translation=Vector3(0.002, 0.046, -0.491)),
    'mHindLimb3Right': JointNode(parent='mHindLimb2Right', translation=Vector3(-0.03, 0.003, -0.468)),
    'mHindLimb4Right': JointNode(parent='mHindLimb3Right', translation=Vector3(0.112, 0.0, -0.061)),
}


def required_joint_hierarchy(joint_names: Collection[str]) -> Set[str]:
    """Get all joints required to have a chain from all joints up to the root joint"""
    required = set(joint_names)
    for joint_name in joint_names:
        while parent_node := SKELETON_JOINTS.get(joint_name):
            required.add(joint_name)
            joint_name = parent_node.parent
    return required


# def load_skeleton_nodes() -> etree.ElementBase:
#     # TODO: this sucks. Can't we construct nodes with the appropriate transformation
#     #  matrices from the data in `avatar_skeleton.xml`?
#     skel_path = get_resource_filename("lib/base/data/male_collada_joints.xml")
#     with open(skel_path, 'r') as f:
#         return etree.fromstring(f.read())
#
#
# def print_skeleton():
#     import pprint
#     skel_root = load_skeleton_nodes()
#
#     dae = collada.Collada()
#     joints = {}
#     for skel_node in skel_root.iter():
#         # xpath is loathsome so this is easier.
#         if "node" not in skel_node.tag or skel_node.get('type') != 'JOINT':
#             continue
#         col_node = collada.scene.Node.load(dae, skel_node, {})
#
#         par_node = skel_node.getparent()
#         parent_name = None
#         if par_node and par_node.get('name'):
#             parent_name = par_node.get('name')
#         translation = Vector3(*transformations.translation_from_matrix(col_node.matrix))
#         joints[col_node.id] = JointNode(parent=parent_name, translation=translation)
#     pprint.pprint(joints, sort_dicts=False)

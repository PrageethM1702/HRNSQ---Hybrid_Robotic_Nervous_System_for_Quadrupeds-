import pybullet as p
import pybullet_data
import numpy as np
import math
import time

p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)
p.setRealTimeSimulation(0)
p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 0)

p.loadURDF("plane.urdf")

dog = p.loadURDF(
    "laikago/laikago_toes_zup.urdf",
    [0, 0, 0.48],
    p.getQuaternionFromEuler([0, 0, 0]),
    flags=p.URDF_USE_SELF_COLLISION,
    useFixedBase=False
)

for j in range(p.getNumJoints(dog)):
    p.changeDynamics(dog, j, linearDamping=0, angularDamping=0)
    p.setJointMotorControl2(dog, j, p.VELOCITY_CONTROL, force=0)

# From official bullet3 laikago.py
# jointDirections=[-1,1,1, 1,1,1, -1,1,1, 1,1,1]
# jointOffsets   =[ 0,-0.7,0.7, 0,-0.7,0.7, 0,-0.7,0.7, 0,-0.7,0.7]
# jointIds — only REVOLUTE/PRISMATIC joints, skip fixed:
jointIds = []
for j in range(p.getNumJoints(dog)):
    info = p.getJointInfo(dog, j)
    jtype = info[2]
    if jtype in (p.JOINT_REVOLUTE, p.JOINT_PRISMATIC):
        jointIds.append(j)
        print(f"  active joint {j}: {info[1].decode()}")

print(f"Active joints: {jointIds}  count={len(jointIds)}")

jointDirections = [-1, 1, 1,  1, 1, 1,  -1, 1, 1,  1, 1, 1]
jointOffsets    = [ 0,-0.7, 0.7,  0,-0.7, 0.7,  0,-0.7, 0.7,  0,-0.7, 0.7]

FORCE    = 60.0
MAX_VEL  = 10.0

def setJoints(angles, force=FORCE):
    for i, jid in enumerate(jointIds[:12]):
        tgt = jointDirections[i] * angles[i] + jointOffsets[i]
        p.setJointMotorControl2(
            dog, jid, p.POSITION_CONTROL,
            targetPosition=tgt,
            force=force,
            maxVelocity=MAX_VEL
        )

# Stand pose: hip=0, thigh=-0.6, calf=1.0 (matches offset convention)
STAND = [0, 0.6, -1.0] * 4
setJoints(STAND, force=80)

for _ in range(500):
    p.stepSimulation()

p.resetDebugVisualizerCamera(
    cameraDistance=1.4, cameraYaw=-20,
    cameraPitch=-25, cameraTargetPosition=[0, 0, 0.3]
)

# ── Sinusoidal trot gait ──────────────────────────────────────────────────────
# Leg order in jointIds blocks: FL=0, FR=1, BL=2, BR=3
# Trot diagonal pairs: (FL,BR) and (FR,BL) in antiphase
# Per leg: [abduction, hip, knee]

HIP_STAND   =  0.6    # thigh angle at mid-stance
KNEE_STAND  = -1.0    # knee angle at mid-stance
HIP_SWING   =  0.35   # amplitude of hip swing
KNEE_SWING  =  0.6    # amplitude of knee flexion
ABD_AMP     =  0.0    # lateral abduction (keep 0 for straight walk)

# Phase offsets for trot: FL and BR together, FR and BL together
PHASE = [0.0, math.pi, math.pi, 0.0]   # FL, FR, BL, BR

FREQ   = 1.8    # Hz
DT     = 1./240.
t      = 0.0

cyaw   = -20
cpitch = -25
cdist  = 1.4
dr     = 0      # 0=stop,1=fwd,2=bwd,3=right,4=left

# Tiny 1-hidden-layer network that modulates gait amplitude with body state
# Weights are hand-crafted to produce stable forward walking correction
class StabiliserNet:
    def __init__(self):
        # input: [roll, pitch, roll_vel, pitch_vel]  (4,)
        # output: [delta_hip_amp, delta_abd]          (2,)
        self.W1 = np.array([
            [ 0.4, -0.1,  0.1, -0.05],
            [-0.1,  0.4, -0.05, 0.1 ],
            [ 0.2,  0.2,  0.05, 0.05],
            [-0.2, -0.2, -0.05,-0.05],
        ], dtype=float)
        self.b1 = np.zeros(4)
        self.W2 = np.array([
            [ 0.3,  0.3, -0.3, -0.3],
            [-0.5,  0.5,  0.1, -0.1],
        ], dtype=float)
        self.b2 = np.zeros(2)

    def forward(self, x):
        h  = np.tanh(self.W1 @ x + self.b1)
        return np.tanh(self.W2 @ h + self.b2) * 0.12

net = StabiliserNet()

prev_roll  = 0.0
prev_pitch = 0.0
prev_t     = time.time()
DIAG_T     = 3.0
last_diag  = prev_t

print("[MAIN] Running. Arrow keys: fwd/bwd/turn. A/D/C/F: camera. Z/X: zoom.")

while True:
    now = time.time()

    pos, orn = p.getBasePositionAndOrientation(dog)
    eul = p.getEulerFromQuaternion(orn)
    roll, pitch, yaw = eul
    roll_d  = math.degrees(roll)
    pitch_d = math.degrees(pitch)

    if abs(roll_d) > 70 or abs(pitch_d) > 60 or pos[2] < 0.1:
        print(f"[FLIP] roll={roll_d:.1f} pitch={pitch_d:.1f} z={pos[2]:.2f} — reset")
        p.resetBasePositionAndOrientation(dog, [0, 0, 0.48], [0, 0, 0, 1])
        for j in range(p.getNumJoints(dog)):
            p.resetJointState(dog, j, 0.0, 0.0)
        setJoints(STAND, force=80)
        for _ in range(300):
            p.stepSimulation()
        t = 0.0
        prev_roll = prev_pitch = 0.0
        continue

    dt_real = now - prev_t
    if dt_real < 1e-6:
        dt_real = DT
    prev_t  = now
    roll_vel  = (roll  - prev_roll)  / dt_real
    pitch_vel = (pitch - prev_pitch) / dt_real
    prev_roll, prev_pitch = roll, pitch

    net_in  = np.array([roll, pitch, roll_vel * 0.1, pitch_vel * 0.1])
    net_out = net.forward(net_in)
    d_hip_amp = float(net_out[0])
    d_abd     = float(net_out[1])

    keys = p.getKeyboardEvents()
    if keys.get(100): cyaw   += 1
    if keys.get(97):  cyaw   -= 1
    if keys.get(99):  cpitch += 1
    if keys.get(102): cpitch -= 1
    if keys.get(122): cdist  += 0.02
    if keys.get(120): cdist  -= 0.02
    if keys.get(65297): dr = 1
    if keys.get(65298): dr = 2
    if keys.get(65296): dr = 3
    if keys.get(65295): dr = 4
    if keys.get(32):    dr = 0

    if dr == 0:
        setJoints(STAND)
        for _ in range(4):
            p.stepSimulation()
        t += DT * 4
        p.resetDebugVisualizerCamera(cdist, cyaw, cpitch, list(pos))
        time.sleep(DT * 4)
        continue

    fwd_sign = 1.0 if dr == 1 else (-1.0 if dr == 2 else 0.0)
    yaw_sign = 0.0
    if dr == 3: yaw_sign =  1.0
    if dr == 4: yaw_sign = -1.0

    hip_amp  = (HIP_SWING + d_hip_amp) * max(abs(fwd_sign), 0.4)
    knee_amp = KNEE_SWING * max(abs(fwd_sign), 0.4)

    angles = []
    for leg in range(4):
        ph     = 2 * math.pi * FREQ * t + PHASE[leg]
        s      = math.sin(ph)
        c      = math.cos(ph)
        lift   = max(0.0, -c)            # foot lifts when c < 0

        hip_tgt  = HIP_STAND  + fwd_sign * hip_amp  * s
        knee_tgt = KNEE_STAND - knee_amp * lift

        # lateral abduction for turning
        is_left  = (leg == 0 or leg == 2)
        abd_turn = yaw_sign * ABD_AMP * 0.3 * (1 if is_left else -1)
        abd_tgt  = d_abd + abd_turn

        angles += [abd_tgt, hip_tgt, knee_tgt]

    setJoints(angles)

    for _ in range(4):
        p.stepSimulation()
    t += DT * 4

    if now - last_diag > DIAG_T:
        last_diag = now
        vel, angvel = p.getBaseVelocity(dog)
        print(f"[DIAG] pos={[round(x,3) for x in pos]}  roll={roll_d:.1f}  pitch={pitch_d:.1f}")
        print(f"       vel={[round(x,3) for x in vel]}  dr={dr}")
        print(f"       net_out: d_hip={d_hip_amp:.3f}  d_abd={d_abd:.3f}")

    p.resetDebugVisualizerCamera(cdist, cyaw, cpitch, list(pos))
    time.sleep(DT * 4)

p.disconnect()
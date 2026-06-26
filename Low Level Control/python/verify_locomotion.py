from hrnsq_locomotion import FrozenHipLocomotion


def main() -> None:
    controller = FrozenHipLocomotion()
    for gait, speed in (("stand", 0.0), ("trot", 0.35)):
        frame = controller.command_frame(t=0.25, gait=gait, speed=speed)
        assert set(frame) == {"FL", "FR", "RL", "RR"}
        for leg, command in frame.items():
            assert command["hip_deg"] == 90.0, f"{leg} hip is not frozen"
            assert 0.0 <= command["shoulder_deg"] <= 180.0
            assert 0.0 <= command["knee_deg"] <= 180.0
            assert 500 <= command["pwm_us"] <= 2500
    print("locomotion verification passed: hip motors frozen, IK outputs in servo range")


if __name__ == "__main__":
    main()

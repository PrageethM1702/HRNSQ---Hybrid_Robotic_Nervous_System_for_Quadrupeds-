float impedance_torque(float desired_position, float measured_position, float desired_velocity, float measured_velocity, float stiffness, float damping)
{
    float position_error = desired_position - measured_position;
    float velocity_error = desired_velocity - measured_velocity;
    return stiffness * position_error + damping * velocity_error;
}

float impedance_clamp(float value, float limit)
{
    if (value > limit)
    {
        return limit;
    }
    if (value < -limit)
    {
        return -limit;
    }
    return value;
}

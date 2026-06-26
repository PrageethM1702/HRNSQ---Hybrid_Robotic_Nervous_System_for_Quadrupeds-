float torque_from_current(float current_amp, float torque_constant)
{
    return current_amp * torque_constant;
}

float current_from_torque(float torque_nm, float torque_constant)
{
    if (torque_constant == 0.0f)
    {
        return 0.0f;
    }
    return torque_nm / torque_constant;
}

float torque_limit(float torque, float limit)
{
    if (torque > limit)
    {
        return limit;
    }
    if (torque < -limit)
    {
        return -limit;
    }
    return torque;
}

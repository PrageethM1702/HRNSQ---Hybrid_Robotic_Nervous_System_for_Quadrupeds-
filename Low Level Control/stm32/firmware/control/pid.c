typedef struct
{
    float kp;
    float ki;
    float kd;
    float integral;
    float previous_error;
    float output_min;
    float output_max;
} PIDController;

void pid_init(PIDController *pid, float kp, float ki, float kd, float out_min, float out_max)
{
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->integral = 0.0f;
    pid->previous_error = 0.0f;
    pid->output_min = out_min;
    pid->output_max = out_max;
}

float pid_update(PIDController *pid, float setpoint, float measurement, float dt)
{
    float error = setpoint - measurement;
    pid->integral += error * dt;
    float derivative = dt > 0.0f ? (error - pid->previous_error) / dt : 0.0f;
    float output = pid->kp * error + pid->ki * pid->integral + pid->kd * derivative;
    pid->previous_error = error;
    if (output > pid->output_max)
    {
        output = pid->output_max;
    }
    if (output < pid->output_min)
    {
        output = pid->output_min;
    }
    return output;
}

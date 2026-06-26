const ids = [
  "connection",
  "source",
  "mode",
  "gait",
  "speed",
  "battery",
  "risk",
  "safety",
  "camera-status",
  "front-camera",
  "depth-camera",
  "camera-resolution",
  "camera-fps",
  "gps-fix",
  "gps-lat",
  "gps-lon",
  "gps-alt",
  "gps-sats",
  "gps-heading",
  "gps-speed",
  "accel-x",
  "accel-y",
  "accel-z",
  "imu-status",
  "roll",
  "pitch",
  "yaw",
  "tilt",
  "gyro-x",
  "gyro-y",
  "gyro-z",
  "last-reflex",
  "reflex-gain",
  "reflex-threshold",
  "contact-ratio",
  "reflex-latency",
  "cpg-frequency",
  "vision-confidence",
  "terrain",
  "obstacles",
  "nearest",
  "flow",
  "path-state",
  "pose-x",
  "pose-y",
  "target",
  "target-distance",
  "logic-voltage",
  "battery-voltage",
  "current",
  "power",
  "battery-percent",
  "temperature",
  "object-temp",
  "humidity",
  "eco2",
  "policy",
  "decision",
  "stability",
  "inference",
  "terrain-class",
  "packet-sequence",
  "can",
  "i2c",
  "uart",
  "wifi",
  "uptime"
];

const el = Object.fromEntries(ids.map(id => [id, document.getElementById(id)]));
const history = { x: [], y: [], z: [] };
let socket = null;
let telemetrySource = localStorage.getItem("hrnsq-source") || "sim";

function number(value, digits = 2) {
  return Number(value || 0).toFixed(digits);
}

function text(id, value) {
  if (el[id]) {
    el[id].textContent = value;
  }
}

function render(state) {
  if (state.source) {
    telemetrySource = state.source;
    updateSourceButtons();
  }
  text("connection", `${telemetrySource.toUpperCase()} telemetry connected | ${new Date((state.timestamp || Date.now() / 1000) * 1000).toLocaleTimeString()}`);
  text("mode", state.mode || "idle");
  text("gait", state.gait || "stand");
  text("speed", `${number(state.speed)} m/s`);
  text("battery", `${number(state.battery_percent, 1)}%`);
  text("risk", number(state.ai?.risk));
  text("safety", state.safety?.state || "safe");
  el.safety.className = state.safety?.state === "safe" ? "ok" : "bad";
  renderCamera(state.camera || {});
  renderGps(state.gps || {});
  renderImu(state);
  renderFeet(state.foot_pressure || {}, state.reflex || {});
  renderCpg(state.cpg || {});
  renderVision(state.vision || {});
  renderNavigation(state.navigation || {});
  renderPower(state);
  renderEnvironment(state);
  renderAi(state.ai || {});
  renderCommunication(state.communication || {});
  renderActuators(state.actuators || {});
  renderLogs(state.logs || []);
  drawAccel(state.accelerometer || {});
}

function renderCamera(camera) {
  if (camera.front) {
    el["front-camera"].src = streamUrl(camera.front);
  }
  if (camera.depth) {
    el["depth-camera"].src = streamUrl(camera.depth);
  }
  text("camera-status", camera.status || "offline");
  text("camera-resolution", camera.resolution || "--");
  text("camera-fps", camera.fps ? `${camera.fps} fps` : "--");
}

function renderGps(gps) {
  text("gps-fix", gps.fix || "--");
  text("gps-lat", gps.lat ?? "--");
  text("gps-lon", gps.lon ?? "--");
  text("gps-alt", gps.alt_m ? `${number(gps.alt_m)} m` : "--");
  text("gps-sats", gps.satellites ?? "--");
  text("gps-heading", gps.heading_deg ? `${number(gps.heading_deg)} deg` : "--");
  text("gps-speed", gps.speed_mps ? `${number(gps.speed_mps)} m/s` : "0.00 m/s");
}

function renderImu(state) {
  const accel = state.accelerometer || {};
  const gyro = state.gyroscope || {};
  const attitude = state.attitude || {};
  text("accel-x", number(accel.x, 3));
  text("accel-y", number(accel.y, 3));
  text("accel-z", number(accel.z, 3));
  text("imu-status", state.imu?.status || "--");
  text("roll", `${number(attitude.roll)} deg`);
  text("pitch", `${number(attitude.pitch)} deg`);
  text("yaw", `${number(attitude.yaw)} deg`);
  text("tilt", `${number(attitude.tilt)} deg`);
  text("gyro-x", number(gyro.x, 3));
  text("gyro-y", number(gyro.y, 3));
  text("gyro-z", number(gyro.z, 3));
}

function renderFeet(feet, reflex) {
  const root = document.getElementById("feet");
  root.innerHTML = "";
  Object.entries(feet).forEach(([leg, data]) => {
    const pressure = Math.round(Number(data.pressure || 0) * 100);
    const item = document.createElement("article");
    item.innerHTML = `<span>${leg}</span><strong>${pressure}%</strong><span>${data.contact ? "contact" : "swing"} | ${number(data.fsr_voltage)} V | ${number(data.load_n)} N</span><div class="bar"><i style="width:${pressure}%"></i></div>`;
    root.appendChild(item);
  });
  text("last-reflex", reflex.last_trigger || "none");
  text("reflex-gain", number(reflex.gain));
  text("reflex-threshold", `${number(reflex.threshold_voltage)} V`);
  text("contact-ratio", number(reflex.contact_ratio));
  text("reflex-latency", `${number(reflex.loop_latency_us)} us`);
}

function renderCpg(cpg) {
  text("cpg-frequency", cpg.frequency_hz ? `${number(cpg.frequency_hz)} Hz` : "0.00 Hz");
  const root = document.getElementById("cpg-phase");
  root.innerHTML = "";
  Object.entries(cpg.phase || {}).forEach(([leg, phase]) => {
    const pct = Math.round(Number(phase || 0) * 100);
    const item = document.createElement("div");
    item.innerHTML = `<span>${leg}</span><strong>${number(phase)}</strong><div class="bar"><i style="width:${pct}%"></i></div>`;
    root.appendChild(item);
  });
}

function renderVision(vision) {
  text("vision-confidence", vision.confidence ? `${number(vision.confidence * 100, 0)}%` : "--");
  text("terrain", vision.terrain || "--");
  text("obstacles", vision.obstacle_count ?? "--");
  text("nearest", vision.nearest_obstacle_m ? `${number(vision.nearest_obstacle_m)} m` : "--");
  const flow = vision.optical_flow || {};
  text("flow", `${number(flow.x, 3)}, ${number(flow.y, 3)}`);
}

function renderNavigation(nav) {
  text("path-state", nav.path_state || "--");
  text("pose-x", number(nav.pose?.x));
  text("pose-y", number(nav.pose?.y));
  text("target", `${number(nav.target?.x)}, ${number(nav.target?.y)}`);
  text("target-distance", nav.distance_to_target_m ? `${number(nav.distance_to_target_m)} m` : "--");
}

function renderPower(state) {
  text("logic-voltage", `${number(state.logic_voltage)} V logic`);
  text("battery-voltage", `${number(state.battery_voltage)} V`);
  text("current", `${number(state.current_a)} A`);
  text("power", `${number(state.power_w)} W`);
  text("battery-percent", `${number(state.battery_percent, 1)}%`);
}

function renderEnvironment(state) {
  text("temperature", `${number(state.temperature_c, 1)} C`);
  text("object-temp", `${number(state.object_temp_c, 1)} C`);
  text("humidity", `${number(state.humidity_percent, 1)}%`);
  text("eco2", `${state.air_quality_eco2 || "--"} ppm`);
}

function renderAi(ai) {
  text("policy", ai.policy || "--");
  text("decision", ai.decision || "--");
  text("stability", number(ai.stability));
  text("inference", ai.inference_ms ? `${number(ai.inference_ms)} ms` : "--");
  text("terrain-class", ai.terrain_class || "--");
}

function renderCommunication(comms) {
  text("packet-sequence", `packet ${comms.packet_sequence || 0}`);
  ["can", "i2c", "uart", "wifi"].forEach(id => {
    text(id, `${id.toUpperCase()} ${comms[id] || "--"}`);
  });
}

function renderActuators(actuators) {
  const root = document.getElementById("actuators");
  root.innerHTML = "";
  Object.entries(actuators).forEach(([leg, data]) => {
    const item = document.createElement("article");
    item.innerHTML = `<span>${leg}</span><strong>${data.enabled ? "enabled" : "off"}</strong><span>hip ${number(data.hip_deg)} deg</span><span>knee ${number(data.knee_deg)} deg</span><span>ankle ${number(data.ankle_deg)} deg</span><span>pwm ${data.pwm_us || 0} us</span>`;
    root.appendChild(item);
  });
}

function renderLogs(logs) {
  text("uptime", `${number(window.lastUptime || 0, 1)} s`);
  const root = document.getElementById("logs");
  root.innerHTML = "";
  logs.slice(-12).reverse().forEach(log => {
    const row = document.createElement("div");
    row.textContent = `${log.time} ${log.level}: ${log.message}`;
    root.appendChild(row);
  });
}

function drawAccel(accel) {
  window.lastUptime = window.lastUptime || 0;
  history.x.push(Number(accel.x || 0));
  history.y.push(Number(accel.y || 0));
  history.z.push(Number(accel.z || 0));
  ["x", "y", "z"].forEach(axis => {
    if (history[axis].length > 80) {
      history[axis].shift();
    }
  });
  const canvas = document.getElementById("accel-chart");
  const ctx = canvas.getContext("2d");
  const width = canvas.width = canvas.clientWidth;
  const height = canvas.height = 120;
  ctx.clearRect(0, 0, width, height);
  ctx.strokeStyle = "#d7dee8";
  ctx.beginPath();
  ctx.moveTo(0, height / 2);
  ctx.lineTo(width, height / 2);
  ctx.stroke();
  drawLine(ctx, history.x, "#1d4ed8", width, height, 9.81);
  drawLine(ctx, history.y, "#15803d", width, height, 9.81);
  drawLine(ctx, history.z, "#b91c1c", width, height, 9.81);
}

function drawLine(ctx, values, color, width, height, scale) {
  ctx.strokeStyle = color;
  ctx.beginPath();
  values.forEach((value, index) => {
    const x = values.length <= 1 ? 0 : index / (values.length - 1) * width;
    const y = height / 2 - value / scale * height * 0.35;
    if (index === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  });
  ctx.stroke();
}

function send(command) {
  const payload = JSON.stringify({ command, source: telemetrySource });
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(payload);
  }
}

function streamUrl(url) {
  if (!url || url.startsWith("data:")) {
    return url;
  }
  try {
    const parsed = new URL(url, window.location.href);
    if (["127.0.0.1", "localhost", "0.0.0.0"].includes(parsed.hostname)) {
      parsed.hostname = window.location.hostname;
    }
    return parsed.toString();
  } catch (_error) {
    return url;
  }
}

function setSource(source) {
  telemetrySource = source;
  localStorage.setItem("hrnsq-source", source);
  updateSourceButtons();
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ source }));
  }
}

function updateSourceButtons() {
  document.querySelectorAll("[data-source]").forEach(button => {
    button.classList.toggle("active", button.dataset.source === telemetrySource);
  });
}

function connect() {
  socket = new WebSocket(`ws://${window.location.hostname}:9001`);
  socket.onopen = () => {
    text("connection", "Telemetry connected");
    setSource(telemetrySource);
  };
  socket.onmessage = event => render(JSON.parse(event.data));
  socket.onclose = () => {
    text("connection", "Telemetry disconnected, retrying");
    setTimeout(connect, 1500);
  };
}

document.querySelectorAll("[data-command]").forEach(button => {
  button.addEventListener("click", () => send(button.dataset.command));
});

document.querySelectorAll("[data-source]").forEach(button => {
  button.addEventListener("click", () => setSource(button.dataset.source));
});

updateSourceButtons();
connect();

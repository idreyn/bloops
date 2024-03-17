const deepmerge = require("deepmerge")

const { Device, Overrides } = require("./models.js");
const { Message } = require("../protocol.js");

const DEFAULT_CONFIG = require("../../config.json");

const PHYSICAL_BUTTONS = {
	JS_LEFT: "Joystick left",
	JS_RIGHT: "Joystick right",
	JS_DOWN: "Joystick down",
	LEFT: "Left",
	RIGHT: "Right",
	UP: "Up",
	DOWN: "Down",
};

class Remote {
	constructor(update, backend) {
		this.update = update;
		this.backend = backend;
		this.device = new Device();
		this.overrides = new Overrides();
		this.logs = [];
		this.physicalButtons = PHYSICAL_BUTTONS;
		this.config = DEFAULT_CONFIG;
		this.pulseHistory = new PulseHistory(this.config.pulse, (p) => this.updatePulse(p));
		backend.on(
			Message.DEVICE_STATUS,
			this.handleDeviceStatus.bind(this)
		);
		backend.on(
			Message.DEVICE_LOG,
			this.handleDeviceLog.bind(this),
		)
	}

	handleDeviceStatus({ info, config, ...rest }) {
		if (!info) return;
		this.device = this.device.copy(info);
		if (!this.config.generated_at || config.generated_at > this.config.generated_at) {
			this.config = config;
			this.pulseHistory.insert(config.pulse);
		}
		this.update();
	}

	handleDeviceLog(message) {
		this.logs.push(message);
	}

	triggerPulse() {
		this.backend.emit(Message.TRIGGER_PULSE);
	}

	updateConfig(partialConfig) {
		const partialConfigWithTimestamp = { ...partialConfig, generated_at: Date.now() }
		this.config = deepmerge(this.config, partialConfigWithTimestamp)
		this.backend.emit(Message.UPDATE_CONFIG, {
			config: partialConfigWithTimestamp,
			save: true,
		})
		this.update();
	}

	updatePulse(pulse) {
		this.updateConfig({ pulse });
		this.pulseHistory.insert(this.config.pulse);
	}

	updateOverrides(obj) {
		this.overrides = this.overrides.copy(obj);
		this.backend.emit(Message.UPDATE_OVERRIDES, this.overrides);
		this.update();
	}

	updateLabel(label) {
		this.updateConfig({
			save: {
				file_prefix: label,
			}
		})
	}

	assignPulseToButton(button, pulse) {
		this.updateConfig({
			remote: {
				remote_keys: {
					[button]: pulse
				}
			}
		});
	}
}

class PulseHistory {
	constructor(initial, update) {
		this.list = [initial];
		this.pointer = 0;
		this.update = update;
	}

	atStart() {
		return this.pointer === 0;
	}

	atEnd() {
		return this.pointer === this.list.length - 1;
	}

	insert(p) {
		if (JSON.stringify(p) === JSON.stringify(this.getCurrent())) {
			return;
		}
		if (!this.atEnd()) {
			this.list = this.list.slice(0, this.pointer);
			this.pointer = this.list.length - 1;
		}
		this.list.push(p);
		this.pointer++;
		this.doUpdate();
	}

	undo() {
		if (!this.atStart()) {
			--this.pointer;
		}
		this.doUpdate();
	}

	redo() {
		if (!this.atEnd()) {
			++this.pointer;
		}
		this.doUpdate();
	}

	getCurrent() {
		return this.list[this.pointer];
	}

	doUpdate() {
		this.update(this.getCurrent());
	}
}

module.exports = { Remote };
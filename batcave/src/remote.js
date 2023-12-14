const { Pulse, Device, Overrides } = require("./models.js");
const { Message } = require("../protocol.js");

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
		this.pulse = Pulse.getDefaultPulse();
		this.pulseSetByInfo = false;
		this.overrides = new Overrides();
		this.msRecordDuration = 100;
		this.physicalButtons = PHYSICAL_BUTTONS;
		this.pulseHistory = new PulseHistory(this.pulse, (p) => {
			this.pulse = p;
			this.update();
		});
		backend.on(
			Message.DEVICE_STATUS,
			this.handleDeviceStatus.bind(this)
		);
	}

	handleDeviceStatus({ status, info }) {
		if (!info) return;
		let { pulse, ...rest } = info;
		this.device = this.device.copy(rest);
		if (pulse && !this.pulseSetByInfo) {
			this.pulse = this.pulse.copy(pulse);
			this.pulseSetByInfo = true;
		}
		this.update();
	}

	triggerPulse() {
		this.backend.emit(Message.TRIGGER_PULSE);
	}

	updatePulse(pulse) {
		this.backend.emit(Message.UPDATE_PULSE, pulse);
		this.pulseHistory.insert(pulse);
	}

	updateRecordDuration(d) {
		this.msRecordDuration = d;
		this.backend.emit(Message.SET_RECORD_DURATION, d);
		this.update();
	}

	updateOverrides(obj) {
		this.overrides = this.overrides.copy(obj);
		this.backend.emit(Message.UPDATE_OVERRIDES, this.overrides);
		this.update();
	}

	updateLabel(label) {
		this.backend.emit(Message.UPDATE_LABEL, label);
		this.update();
	}

	assignPulseToButton(button, pulse) {
		this.backend.emit(Message.ASSIGN_PULSE, { button, pulse });
	}
}

class PulseHistory {
	constructor(first, update) {
		this.list = [first];
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
		if (p.equalTo(this.getCurrent())) {
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
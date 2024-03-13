class Model {
	constructor() {

	}

	enumerable(props, override) {
		override = override || {};
		Object.defineProperty(this, "__properties", {
			enumerable: false, configurable: true, writable: true
		});
		this.__properties = [];
		for (let k in props) {
			this.__properties.push(k);
			Object.defineProperty(this, k, {
				enumerable: true, configurable: true, writable: true
			});
			this[k] = override[k] || props[k];
		}
		for (let k in override) {
			if (!this.__properties.includes(k)) {
				console.warn(
					`Did not assign non-enumerable prop ${k}` +
					` which is only present in override.`
				);
			}
		}
	}

	copy(obj) {
		var k = new this.constructor({
			...this,
			...obj
		});
		return k;
	}

	equalTo(other) {
		if (other.constructor !== this.constructor) {
			return false;
		}
		for (let k of this.__properties) {
			if (this[k] !== other[k]) {
				return false;
			}
		}
		return true;
	}
}

class Device extends Model {
	constructor(obj) {
		super();
		this.enumerable({
			id: "",
			ip: "",
			bluetoothConnections: "",
			deviceBatteryLow: false,
			emitterBatteryLow: false,
			lastSeen: "",
		}, obj);
	}
}

class Pulse extends Model {
	constructor(obj) {
		super();
		this.enumerable({
			type: Pulse.types.CHIRP,
			usDuration: 5e3,
			khzStart: 50,
			khzEnd: 25,
			isSquare: false,
			isLogarithmic: false,
		}, obj);
	}
}

Pulse.getDefaultPulse = function () {
	return new Pulse({
		usDuration: 5e3,
		khzStart: 50,
		khzEnd: 25,
	});
};

Pulse.types = {
	TONE: "tone",
	CHIRP: "chirp",
	CLICK: "click",
	NOISE: "noise",
};

class Overrides extends Model {
	constructor(obj) {
		super();
		this.enumerable({
			wipersEnabled: false,
			sWipersPeriod: 1,
			forceEnableEmitters: false,
			disableSave: false,
			disablePlayback: false
		}, obj);
	}
}

module.exports = { Device, Pulse, Overrides };
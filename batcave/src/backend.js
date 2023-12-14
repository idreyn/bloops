class Backend {
	constructor() {
		this.hasSocket = !!window.io;
		if (this.hasSocket) {
			this.socket = window.io();
		}
	}

	on(...args) {
		this.socket && this.socket.on.apply(this.socket, args);
	}

	off(...args) {
		this.socket && this.socket.off.apply(this.socket, args);
	}

	emit(...args) {
		this.socket && this.socket.emit.apply(this.socket, args);
	}
}

module.exports = { Backend };